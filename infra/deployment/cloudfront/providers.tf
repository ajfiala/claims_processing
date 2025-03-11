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
    key    = "cloudfront/terraform.tfstate"
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