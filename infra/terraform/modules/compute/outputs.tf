output "web_url" {
  description = "Web service URL"
  value       = google_cloud_run_service.web.status[0].url
}

output "api_url" {
  description = "API service URL"
  value       = google_cloud_run_service.api.status[0].url
}

output "agent_url" {
  description = "Agent service URL"
  value       = google_cloud_run_service.agent.status[0].url
}

output "web_service_name" {
  description = "Web service name"
  value       = google_cloud_run_service.web.name
}

output "api_service_name" {
  description = "API service name"
  value       = google_cloud_run_service.api.name
}

output "agent_service_name" {
  description = "Agent service name"
  value       = google_cloud_run_service.agent.name
}
