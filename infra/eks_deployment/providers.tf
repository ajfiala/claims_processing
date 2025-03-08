terraform {
  required_version = ">= 1.0.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
  }
  
  backend "s3" {
    bucket = "claimsdemo-state-bucket"
    key    = "eks_deployment/terraform.tfstate"
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

# Kubernetes provider configuration
provider "kubernetes" {
  host                   = data.terraform_remote_state.eks.outputs.cluster_endpoint
  cluster_ca_certificate = base64decode(data.terraform_remote_state.eks.outputs.cluster_certificate_authority_data)
  
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args        = ["eks", "get-token", "--cluster-name", data.terraform_remote_state.eks.outputs.cluster_name, "--region", local.config.region]
  }
}