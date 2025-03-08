output "repository_url" {
  value       = aws_ecr_repository.api.repository_url
  description = "The URL of the ECR repository"
}

output "repository_name" {
  value       = aws_ecr_repository.api.name
  description = "The name of the ECR repository"
}

output "repository_arn" {
  value       = aws_ecr_repository.api.arn
  description = "The ARN of the ECR repository"
}

output "registry_id" {
  value       = aws_ecr_repository.api.registry_id
  description = "The registry ID of the ECR repository"
}