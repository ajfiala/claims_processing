# Get caller identity for account ID
data "aws_caller_identity" "current" {}
data "aws_availability_zones" "available" {}



locals {
  account_id = data.aws_caller_identity.current.account_id
  
  # Available availability zones
  azs = slice(data.aws_availability_zones.available.names, 0, 3)
}

# VPC
# Fix for the VPC module in your terraform configuration
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = local.config.vpc_name
  cidr = local.config.vpc_cidr

  azs             = local.azs
  private_subnets = [for k, v in local.azs : cidrsubnet(local.config.vpc_cidr, 4, k)]
  public_subnets  = [for k, v in local.azs : cidrsubnet(local.config.vpc_cidr, 8, k + 48)]

  enable_nat_gateway = true
  single_nat_gateway = true

  # UPDATED - Tags required for EKS with workspace-specific cluster name
  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = "1"
    "kubernetes.io/cluster/${local.config.cluster_name}-${terraform.workspace}" = "shared"
  }

  public_subnet_tags = {
    "kubernetes.io/role/elb" = "1"
    "kubernetes.io/cluster/${local.config.cluster_name}-${terraform.workspace}" = "shared"
  }
}

# EKS Cluster
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name                   = "${local.config.cluster_name}-${terraform.workspace}"
  cluster_version                = local.config.cluster_version
  cluster_endpoint_public_access = local.config.enable_public_access

  enable_cluster_creator_admin_permissions = false

  # KMS key administrators
  kms_key_administrators = [
    "arn:aws:iam::${local.account_id}:user/andrewdev"
  ]

  # Access entries for cluster administrators
  access_entries = {
    andrew = {
      principal_arn     = "arn:aws:iam::${local.account_id}:user/andrewdev"
      kubernetes_groups = ["masters"]
      policy_associations = {
        eks_admin_policy = {
          policy_arn  = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSAdminPolicy"
          access_scope = {
            type = "cluster"
          }
        }
        cluster_admin_policy = {
          policy_arn  = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
          access_scope = {
            type = "cluster"
          }
        }
      }
    }
  }

  # Enable EKS Auto Mode
  cluster_compute_config = {
    enabled = true
    node_pools = ["system", "general-purpose"]
  }

  create_node_iam_role = true
  
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  # Enable OIDC provider for service account roles
  enable_irsa = true

  tags = local.config.cluster_tags
}



# IRSA for backend application
module "backend_irsa" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.30"

  role_name = "claims-api-${terraform.workspace}"
  
  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["default:claims-api-sa"]
    }
  }
}

# IAM policy for backend application
resource "aws_iam_policy" "backend_policy" {
  name        = "claims-api-policy-${terraform.workspace}"
  description = "Policy for Claims API application"
  
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetAuthorizationToken"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = [
          "secretsmanager:GetSecretValue",
          "ssm:GetParameter",
          "ssm:GetParameters",
          "ssm:GetParametersByPath"
        ],
        Resource = [
          "arn:aws:secretsmanager:${local.config.region}:${local.account_id}:secret:claims/*",
          "arn:aws:ssm:${local.config.region}:${local.account_id}:parameter/claims/*"
        ]
      }
    ]
  })
}

# Attach policy to role
resource "aws_iam_role_policy_attachment" "backend_policy_attachment" {
  role       = module.backend_irsa.iam_role_name
  policy_arn = aws_iam_policy.backend_policy.arn
}
