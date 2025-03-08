output "distribution_id" {
  value       = aws_cloudfront_distribution.frontend.id
  description = "The ID of the CloudFront distribution"
}

output "distribution_domain_name" {
  value       = aws_cloudfront_distribution.frontend.domain_name
  description = "The domain name of the CloudFront distribution"
}

output "s3_bucket_name" {
  value       = aws_s3_bucket.frontend.id
  description = "The name of the S3 bucket for static assets"
}

output "s3_bucket_arn" {
  value       = aws_s3_bucket.frontend.arn
  description = "The ARN of the S3 bucket for static assets"
}

output "website_domain" {
  value       = local.config.domain_name
  description = "The custom domain for the website"
}