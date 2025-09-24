output "web_url" {
  description = "Production web application URL"
  value       = module.compute.web_url
}

output "api_url" {
  description = "Production API URL"
  value       = module.compute.api_url
}

output "agent_url" {
  description = "Production agent service URL"
  value       = module.compute.agent_url
}

output "database_connection_name" {
  description = "Database connection name"
  value       = module.database.database_connection_name
}

output "static_bucket_url" {
  description = "Static assets bucket URL"
  value       = module.storage.static_bucket_url
}
