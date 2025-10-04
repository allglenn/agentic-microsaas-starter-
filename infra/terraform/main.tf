terraform {
  required_version = ">= 1.6.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" { default = "agentic-microsaas" }
variable "region" { default = "europe-west1" }

# Cloud SQL PostgreSQL with pgvector
resource "google_sql_database_instance" "main" {
  name             = "${var.project_id}-db"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = "db-f1-micro"

    database_flags {
      name  = "shared_preload_libraries"
      value = "vector"
    }

    ip_configuration {
      ipv4_enabled = true
      authorized_networks {
        name  = "all"
        value = "0.0.0.0/0"
      }
    }
  }

  deletion_protection = false
}

resource "google_sql_database" "database" {
  name     = "agentic_microsaas"
  instance = google_sql_database_instance.main.name
}

resource "google_sql_user" "user" {
  name     = "user"
  instance = google_sql_database_instance.main.name
  password = "password"
}

# Cloud Run services
resource "google_cloud_run_service" "web" {
  name     = "web"
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/web:latest"
        ports {
          container_port = 3000
        }
        env {
          name  = "DATABASE_URL"
          value = "postgresql://user:password@${google_sql_database_instance.main.private_ip_address}:5432/agentic_microsaas"
        }
        env {
          name  = "REDIS_URL"
          value = "redis://${google_redis_instance.cache.host}:6379"
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

resource "google_cloud_run_service" "api" {
  name     = "api"
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/api:latest"
        ports {
          container_port = 8000
        }
        env {
          name  = "DATABASE_URL"
          value = "postgresql://user:password@${google_sql_database_instance.main.private_ip_address}:5432/agentic_microsaas"
        }
        env {
          name  = "REDIS_URL"
          value = "redis://${google_redis_instance.cache.host}:6379"
        }
        env {
          name  = "GCS_BUCKET_NAME"
          value = google_storage_bucket.files.name
        }
        env {
          name  = "GCP_PROJECT_ID"
          value = var.project_id
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

resource "google_cloud_run_service" "agent" {
  name     = "agent"
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/agent:latest"
        env {
          name  = "DATABASE_URL"
          value = "postgresql://user:password@${google_sql_database_instance.main.private_ip_address}:5432/agentic_microsaas"
        }
        env {
          name  = "REDIS_URL"
          value = "redis://${google_redis_instance.cache.host}:6379"
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Redis instance
resource "google_redis_instance" "cache" {
  name           = "${var.project_id}-cache"
  tier           = "BASIC"
  memory_size_gb = 1
  region         = var.region
}

# Cloud Storage buckets
resource "google_storage_bucket" "static" {
  name          = "${var.project_id}-static"
  location      = "US"
  force_destroy = true
}

# File storage bucket for user uploads
resource "google_storage_bucket" "files" {
  name          = "${var.project_id}-files"
  location      = var.region
  force_destroy = true

  # Enable versioning for file recovery
  versioning {
    enabled = true
  }

  # Lifecycle management for cost optimization
  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type = "Delete"
    }
  }

  # CORS configuration for web uploads
  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD", "PUT", "POST", "DELETE"]
    response_header = ["*"]
    max_age_seconds = 3600
  }
}

# Service account for file operations
resource "google_service_account" "file_storage" {
  account_id   = "file-storage-sa"
  display_name = "File Storage Service Account"
  description  = "Service account for file storage operations"
}

# IAM binding for file storage service account
resource "google_storage_bucket_iam_member" "file_storage_admin" {
  bucket = google_storage_bucket.files.name
  role   = "roles/storage.admin"
  member = "serviceAccount:${google_service_account.file_storage.email}"
}

# IAM binding for Cloud Run to access file storage
resource "google_storage_bucket_iam_member" "cloud_run_files" {
  bucket = google_storage_bucket.files.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.file_storage.email}"
}

# IAM bindings
resource "google_cloud_run_service_iam_member" "web_public" {
  service  = google_cloud_run_service.web.name
  location = google_cloud_run_service.web.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Outputs
output "web_url" {
  value = google_cloud_run_service.web.status[0].url
}

output "api_url" {
  value = google_cloud_run_service.api.status[0].url
}

output "database_connection_name" {
  value = google_sql_database_instance.main.connection_name
}

output "file_storage_bucket" {
  value = google_storage_bucket.files.name
}

output "file_storage_service_account" {
  value = google_service_account.file_storage.email
}
