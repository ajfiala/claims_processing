# Get CloudFront distribution information
data "terraform_remote_state" "cloudfront" {
  backend = "s3"
  config = {
    bucket = "claimsdemo-state-bucket"
    key    = "cloudfront/terraform.tfstate"
    region = "us-east-1"
  }
  workspace = terraform.workspace
}

# Get the most recently created load balancer with the specified tag
data "aws_lb" "eks_alb" {
  tags = {
    "${local.config.alb_tag_key}" = local.config.alb_tag_value
  }
}

# Looking up the Route53 zone
data "aws_route53_zone" "main" {
  name = local.config.domain_name
  private_zone = false
}

# Create record for frontend (CloudFront)
resource "aws_route53_record" "frontend" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "${local.config.frontend_subdomain}.${local.config.domain_name}"
  type    = "A"

  alias {
    name                   = data.terraform_remote_state.cloudfront.outputs.distribution_domain_name
    zone_id                = "Z2FDTNDATAQYW2" # CloudFront's zone ID is always this value
    evaluate_target_health = false
  }
}

# Create record for API (ALB)
resource "aws_route53_record" "api" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "${local.config.api_subdomain}.${local.config.domain_name}"
  type    = "A"

  alias {
    name                   = data.aws_lb.eks_alb.dns_name
    zone_id                = data.aws_lb.eks_alb.zone_id
    evaluate_target_health = true
  }
}