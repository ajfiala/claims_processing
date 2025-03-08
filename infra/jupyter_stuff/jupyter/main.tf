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
    key    = "sagemaker/terraform.tfstate"
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

# Fetch remote state for VPC and EKS config
data "terraform_remote_state" "eks" {
  backend = "s3"
  
  config = {
    bucket = "claimsdemo-state-bucket"
    key    = "eks/terraform.tfstate"
    region = "us-east-1"
  }
  workspace = terraform.workspace
}

# Create IAM role for SageMaker
resource "aws_iam_role" "sagemaker_role" {
  name = local.config.sagemaker.role_name

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "sagemaker.amazonaws.com"
        }
      },
    ]
  })

  tags = local.config.tags
}

# Attach policies to the SageMaker role
resource "aws_iam_role_policy_attachment" "sagemaker_full_access" {
  role       = aws_iam_role.sagemaker_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
}

resource "aws_iam_role_policy_attachment" "bedrock_full_access" {
  role       = aws_iam_role.sagemaker_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonBedrockFullAccess"
}

resource "aws_iam_role_policy_attachment" "s3_full_access" {
  role       = aws_iam_role.sagemaker_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

# Set up GitHub repository connection
resource "aws_sagemaker_code_repository" "github_repo" {
  code_repository_name = local.config.sagemaker.github_repo_name

  git_config {
    repository_url = local.config.sagemaker.github_repo_url
    secret_arn     = local.config.sagemaker.github_repo_secret_id
  }
}

# Create SageMaker notebook instance
resource "aws_sagemaker_notebook_instance" "jupyter" {
  name                    = local.config.sagemaker.instance_name
  role_arn                = aws_iam_role.sagemaker_role.arn
  instance_type           = local.config.sagemaker.instance_type
  volume_size             = local.config.sagemaker.volume_size
  subnet_id               = data.terraform_remote_state.eks.outputs.private_subnet_ids[0]
  security_groups         = [data.terraform_remote_state.eks.outputs.node_security_group_id]
  direct_internet_access  = "Enabled"
  
  default_code_repository = aws_sagemaker_code_repository.github_repo.code_repository_name

  lifecycle {
    ignore_changes = [
      # Ignore changes to the root access to prevent unnecessary updates
      root_access,
      default_code_repository
    ]
  }

  tags = merge(local.config.tags, {
    Name = local.config.sagemaker.instance_name
  })
}

# Add an S3 bucket for the SageMaker notebook instance
resource "aws_s3_bucket" "jupyter_data_bucket" {
  bucket = local.config.sagemaker.bucket_name
  
  tags = merge(local.config.tags, {
    Name = local.config.sagemaker.bucket_name
  })
}

# Configure bucket versioning
resource "aws_s3_bucket_versioning" "bucket_versioning" {
  bucket = aws_s3_bucket.jupyter_data_bucket.id
  
  versioning_configuration {
    status = local.config.sagemaker.enable_bucket_versioning ? "Enabled" : "Disabled"
  }
}

# Configure server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "bucket_encryption" {
  bucket = aws_s3_bucket.jupyter_data_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Configure public access block for security
resource "aws_s3_bucket_public_access_block" "bucket_public_access_block" {
  bucket = aws_s3_bucket.jupyter_data_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Create a policy that grants SageMaker access to the S3 bucket
resource "aws_iam_policy" "sagemaker_s3_bucket_access" {
  name        = "sagemaker-s3-bucket-access-${local.config.sagemaker.instance_name}"
  description = "Policy to allow SageMaker instance to access the S3 bucket"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Effect   = "Allow"
        Resource = [
          "${aws_s3_bucket.jupyter_data_bucket.arn}",
          "${aws_s3_bucket.jupyter_data_bucket.arn}/*"
        ]
      }
    ]
  })
}

# Attach the policy to the SageMaker role
resource "aws_iam_role_policy_attachment" "sagemaker_s3_bucket_access" {
  role       = aws_iam_role.sagemaker_role.name
  policy_arn = aws_iam_policy.sagemaker_s3_bucket_access.arn
}