# Compute Module - Cloud Run Services
terraform {
  required_version = ">= 1.6.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

# Cloud Run service for Web
resource "google_cloud_run_service" "web" {
  name     = "${var.project_id}-${var.environment}-web"
  location = var.region

  template {
    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale"  = var.max_instances
        "autoscaling.knative.dev/minScale"  = var.min_instances
        "run.googleapis.com/cpu-throttling" = "false"
      }
    }

    spec {
      containers {
        image = "${var.registry_url}/${var.project_id}/web:${var.image_tag}"
        ports {
          container_port = 3000
        }

        env {
          name  = "DATABASE_URL"
          value = var.database_url
        }
        env {
          name  = "REDIS_URL"
          value = var.redis_url
        }
        env {
          name  = "NEXTAUTH_URL"
          value = var.nextauth_url
        }
        env {
          name  = "NEXTAUTH_SECRET"
          value = var.nextauth_secret
        }
        env {
          name  = "GOOGLE_CLIENT_ID"
          value = var.google_client_id
        }
        env {
          name  = "GOOGLE_CLIENT_SECRET"
          value = var.google_client_secret
        }

        resources {
          limits = {
            cpu    = var.cpu_limit
            memory = var.memory_limit
          }
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Cloud Run service for API
resource "google_cloud_run_service" "api" {
  name     = "${var.project_id}-${var.environment}-api"
  location = var.region

  template {
    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale"  = var.max_instances
        "autoscaling.knative.dev/minScale"  = var.min_instances
        "run.googleapis.com/cpu-throttling" = "false"
      }
    }

    spec {
      containers {
        image = "${var.registry_url}/${var.project_id}/api:${var.image_tag}"
        ports {
          container_port = 8000
        }

        env {
          name  = "DATABASE_URL"
          value = var.database_url
        }
        env {
          name  = "REDIS_URL"
          value = var.redis_url
        }
        env {
          name  = "API_SECRET_KEY"
          value = var.api_secret_key
        }
        env {
          name  = "OPENAI_API_KEY"
          value = var.openai_api_key
        }

        resources {
          limits = {
            cpu    = var.cpu_limit
            memory = var.memory_limit
          }
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Cloud Run service for Agent
resource "google_cloud_run_service" "agent" {
  name     = "${var.project_id}-${var.environment}-agent"
  location = var.region

  template {
    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale"  = var.max_instances
        "autoscaling.knative.dev/minScale"  = var.min_instances
        "run.googleapis.com/cpu-throttling" = "false"
      }
    }

    spec {
      containers {
        image = "${var.registry_url}/${var.project_id}/agent:${var.image_tag}"

        env {
          name  = "DATABASE_URL"
          value = var.database_url
        }
        env {
          name  = "REDIS_URL"
          value = var.redis_url
        }
        env {
          name  = "OPENAI_API_KEY"
          value = var.openai_api_key
        }

        resources {
          limits = {
            cpu    = var.cpu_limit
            memory = var.memory_limit
          }
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}
