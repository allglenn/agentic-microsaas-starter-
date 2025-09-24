output "database_connection_name" {
  description = "Database connection name"
  value       = google_sql_database_instance.main.connection_name
}

output "database_private_ip" {
  description = "Database private IP address"
  value       = google_sql_database_instance.main.private_ip_address
}

output "database_public_ip" {
  description = "Database public IP address"
  value       = google_sql_database_instance.main.public_ip_address
}

output "redis_host" {
  description = "Redis host address"
  value       = google_redis_instance.cache.host
}

output "redis_port" {
  description = "Redis port"
  value       = google_redis_instance.cache.port
}
