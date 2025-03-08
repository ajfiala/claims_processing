# Get EKS cluster information (to reference in IAM policies)
data "terraform_remote_state" "eks" {
  backend = "s3"
  config = {
    bucket = "claimsdemo-state-bucket"
    key    = "eks/terraform.tfstate"
    region = "us-east-1"
  }
  workspace = terraform.workspace
}

# ECR Repository
resource "aws_ecr_repository" "api" {
  name                 = "${local.config.repository_name}-${terraform.workspace}"
  image_tag_mutability = local.config.image_tag_mutability
  
  image_scanning_configuration {
    scan_on_push = local.config.scan_on_push
  }

  encryption_configuration {
    encryption_type = "KMS"
  }

  tags = {
    Name = "${local.config.repository_name}-${terraform.workspace}"
  }
}

# ECR Repository Policy
resource "aws_ecr_repository_policy" "api_policy" {
  repository = aws_ecr_repository.api.name

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid    = "AllowPullFromEKS",
        Effect = "Allow",
        Principal = {
          AWS = data.terraform_remote_state.eks.outputs.cluster_iam_role_arn
        },
        Action = [
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability"
        ]
      }
    ]
  })
}
