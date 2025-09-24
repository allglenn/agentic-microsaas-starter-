variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "agentic-microsaas-staging"
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "europe-west1"
}

variable "registry_url" {
  description = "Container registry URL"
  type        = string
  default     = "gcr.io"
}

variable "image_tag" {
  description = "Container image tag"
  type        = string
  default     = "latest"
}

variable "staging_db_tier" {
  description = "Staging database tier"
  type        = string
  default     = "db-standard-1"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "nextauth_url" {
  description = "NextAuth URL for staging"
  type        = string
  default     = "https://staging.agentic-microsaas.com"
}

variable "nextauth_secret" {
  description = "NextAuth secret"
  type        = string
  sensitive   = true
}

variable "google_client_id" {
  description = "Google OAuth client ID"
  type        = string
  sensitive   = true
}

variable "google_client_secret" {
  description = "Google OAuth client secret"
  type        = string
  sensitive   = true
}

variable "api_secret_key" {
  description = "API secret key"
  type        = string
  sensitive   = true
}

variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
  sensitive   = true
}
