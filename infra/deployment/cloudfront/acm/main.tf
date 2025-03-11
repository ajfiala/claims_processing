# Look up the Route53 zone
data "aws_route53_zone" "selected" {
  name         = local.config.domain_name
  private_zone = false
}

# ACM Certificate for CloudFront (must be in us-east-1)
resource "aws_acm_certificate" "cloudfront_cert" {
  provider                  = aws.us_east_1
  domain_name               = local.config.domain_name
  subject_alternative_names = local.config.subject_alternative_names
  validation_method         = local.config.validation_method

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name = "cloudfront-${local.config.domain_name}-cert"
  }
}

# DNS validation records for CloudFront cert
resource "aws_route53_record" "cloudfront_cert_validation" {
  provider = aws.us_east_1
  for_each = {
    for dvo in aws_acm_certificate.cloudfront_cert.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.selected.zone_id
}

# Certificate validation for CloudFront
resource "aws_acm_certificate_validation" "cloudfront_cert" {
  provider                = aws.us_east_1
  certificate_arn         = aws_acm_certificate.cloudfront_cert.arn
  validation_record_fqdns = [for record in aws_route53_record.cloudfront_cert_validation : record.fqdn]

  timeouts {
    create = "30m"
  }
}

# ACM Certificate for ALB (in specified region)
resource "aws_acm_certificate" "alb_cert" {
  domain_name               = local.config.domain_name
  subject_alternative_names = local.config.subject_alternative_names
  validation_method         = local.config.validation_method

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name = "alb-${local.config.domain_name}-cert"
  }
}

# DNS validation records for ALB cert
resource "aws_route53_record" "alb_cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.alb_cert.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.selected.zone_id
}

# Certificate validation for ALB
resource "aws_acm_certificate_validation" "alb_cert" {
  certificate_arn         = aws_acm_certificate.alb_cert.arn
  validation_record_fqdns = [for record in aws_route53_record.alb_cert_validation : record.fqdn]

  timeouts {
    create = "30m"
  }
}