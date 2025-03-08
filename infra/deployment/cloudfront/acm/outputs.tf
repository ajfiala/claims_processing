output "cloudfront_certificate_arn" {
  value       = aws_acm_certificate_validation.cloudfront_cert.certificate_arn
  description = "ARN of the validated ACM certificate for CloudFront"
}

output "alb_certificate_arn" {
  value       = aws_acm_certificate_validation.alb_cert.certificate_arn
  description = "ARN of the validated ACM certificate for ALB"
}

output "certificate_domain" {
  value       = local.config.domain_name
  description = "Domain name for the certificate"
}

output "certificate_alt_names" {
  value       = local.config.subject_alternative_names
  description = "Alternative domain names for the certificate"
}