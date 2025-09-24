# Database Module
terraform {
  required_version = ">= 1.6.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

# Cloud SQL PostgreSQL with pgvector
resource "google_sql_database_instance" "main" {
  name             = "${var.project_id}-${var.environment}-db"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = var.db_tier

    database_flags {
      name  = "shared_preload_libraries"
      value = "vector"
    }

    ip_configuration {
      ipv4_enabled = var.enable_public_ip
      authorized_networks {
        name  = "all"
        value = "0.0.0.0/0"
      }
    }

    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      location                       = var.region
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = 7
      backup_retention_settings {
        retained_backups = 30
        retention_unit   = "COUNT"
      }
    }

    maintenance_window {
      day          = 7
      hour         = 3
      update_track = "stable"
    }
  }

  deletion_protection = var.deletion_protection
}

resource "google_sql_database" "database" {
  name     = "agentic_microsaas"
  instance = google_sql_database_instance.main.name
}

resource "google_sql_user" "user" {
  name     = "user"
  instance = google_sql_database_instance.main.name
  password = var.db_password
}

# Redis instance
resource "google_redis_instance" "cache" {
  name           = "${var.project_id}-${var.environment}-cache"
  tier           = var.redis_tier
  memory_size_gb = var.redis_memory_size
  region         = var.region

  auth_enabled = true

  redis_configs = {
    maxmemory-policy = "allkeys-lru"
  }
}
