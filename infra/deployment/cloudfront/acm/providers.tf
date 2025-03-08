terraform {
  required_version = ">= 1.0.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket = "claimsdemo-state-bucket"
    key    = "acm/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = local.config.region
  
  default_tags {
    tags = {
      Environment = terraform.workspace
      Project     = "ClaimsDemo"
      ManagedBy   = "Terraform"
    }
  }
}

# Provider for CloudFront certificate (must be in us-east-1)
provider "aws" {
  alias  = "us_east_1"
  region = local.config.cloudfront_region
  
  default_tags {
    tags = {
      Environment = terraform.workspace
      Project     = "ClaimsDemo"
      ManagedBy   = "Terraform"
    }
  }
}