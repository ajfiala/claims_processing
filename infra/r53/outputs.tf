output "zone_id" {
  value       = data.aws_route53_zone.main.zone_id
  description = "The Route53 zone ID for the domain"
}

output "frontend_fqdn" {
  value       = aws_route53_record.frontend.fqdn
  description = "The fully qualified domain name for the frontend"
}

output "api_fqdn" {
  value       = aws_route53_record.api.fqdn
  description = "The fully qualified domain name for the API"
}

output "alb_dns_name" {
  value       = data.aws_lb.eks_alb.dns_name
  description = "The DNS name of the Application Load Balancer"
}