output "static_bucket_name" {
  description = "Static assets bucket name"
  value       = google_storage_bucket.static.name
}

output "static_bucket_url" {
  description = "Static assets bucket URL"
  value       = google_storage_bucket.static.url
}

output "backups_bucket_name" {
  description = "Backups bucket name"
  value       = google_storage_bucket.backups.name
}

output "backups_bucket_url" {
  description = "Backups bucket URL"
  value       = google_storage_bucket.backups.url
}
