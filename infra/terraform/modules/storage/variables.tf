variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
}

variable "force_destroy" {
  description = "Force destroy bucket on terraform destroy"
  type        = bool
  default     = false
}

variable "enable_versioning" {
  description = "Enable bucket versioning"
  type        = bool
  default     = true
}

variable "lifecycle_age" {
  description = "Lifecycle rule age in days"
  type        = number
  default     = 30
}

variable "cors_origins" {
  description = "CORS origins for static bucket"
  type        = list(string)
  default     = ["*"]
}
