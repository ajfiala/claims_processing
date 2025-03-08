# Remote state data sources
data "terraform_remote_state" "eks" {
  backend = "s3"
  config = {
    bucket = "claimsdemo-state-bucket"
    key    = "eks/terraform.tfstate"
    region = "us-east-1"
  }
  workspace = terraform.workspace
}

data "terraform_remote_state" "acm" {
  backend = "s3"
  config = {
    bucket = "claimsdemo-state-bucket"
    key    = "acm/terraform.tfstate"
    region = "us-east-1"
  }
  workspace = terraform.workspace
}

data "terraform_remote_state" "ecr" {
  backend = "s3"
  config = {
    bucket = "claimsdemo-state-bucket"
    key    = "ecr/terraform.tfstate"
    region = "us-east-1"
  }
  workspace = terraform.workspace
}

# Get the latest image from ECR
data "aws_ecr_image" "api_image" {
  repository_name = data.terraform_remote_state.ecr.outputs.repository_name
  image_tag       = local.config.image_tag
}

# Kubernetes Service Account
resource "kubernetes_service_account" "api" {
  metadata {
    name = "${local.config.app_name}-sa"
    annotations = {
      "eks.amazonaws.com/role-arn" = data.terraform_remote_state.eks.outputs.backend_service_account_role
    }
  }
}

# Kubernetes Deployment
resource "kubernetes_deployment" "api" {
  metadata {
    name = local.config.app_name
    labels = {
      app = local.config.app_name
    }
  }

  spec {
    replicas = local.config.replicas

    selector {
      match_labels = {
        app = local.config.app_name
      }
    }

    template {
      metadata {
        labels = {
          app = local.config.app_name
        }
        # Add annotation to force redeployment when image changes
        annotations = {
          "image-digest" = data.aws_ecr_image.api_image.image_digest
        }
      }

      spec {
        service_account_name = kubernetes_service_account.api.metadata[0].name
        
        container {
          image = "${data.terraform_remote_state.ecr.outputs.repository_url}:${local.config.image_tag}"
          name  = local.config.app_name
          
          port {
            container_port = local.config.container_port
          }
          
          dynamic "env" {
            for_each = local.config.container_env
            content {
              name  = env.key
              value = env.value
            }
          }
          
          resources {
            limits = {
              cpu    = local.config.resources.limits.cpu
              memory = local.config.resources.limits.memory
            }
            requests = {
              cpu    = local.config.resources.requests.cpu
              memory = local.config.resources.requests.memory
            }
          }
          
          liveness_probe {
            http_get {
              path = local.config.health_check.path
              port = local.config.container_port
            }
            initial_delay_seconds = local.config.health_check.liveness_initial
            period_seconds        = local.config.health_check.liveness_period
          }
          
          readiness_probe {
            http_get {
              path = local.config.health_check.path
              port = local.config.container_port
            }
            initial_delay_seconds = local.config.health_check.readiness_initial
            period_seconds        = local.config.health_check.readiness_period
          }
        }
      }
    }
  }

  # Make deployment recreate pods when image changes
  lifecycle {
    create_before_destroy = true
  }
  
}

# Kubernetes Service
resource "kubernetes_service" "api" {
  metadata {
    name = local.config.app_name
  }
  
  spec {
    selector = {
      app = local.config.app_name
    }
    
    port {
      port        = local.config.service_port
      target_port = local.config.container_port
    }
    
    type = "ClusterIP"
  }
}

# EKS Auto Mode IngressClassParams
resource "kubernetes_manifest" "ingress_class_params" {
  manifest = {
    apiVersion = "eks.amazonaws.com/v1"
    kind       = "IngressClassParams"
    metadata = {
      name = "alb-${local.config.app_name}"
    }
    spec = {
      scheme = "internet-facing"
      ipAddressType = "ipv4"
      certificateARNs = [data.terraform_remote_state.acm.outputs.alb_certificate_arn]
      tags = [
        {
          key   = "Environment"
          value = terraform.workspace
        },
        {
          key   = "Application"
          value = local.config.app_name
        }
      ]
      group = {
        name = "opsloom"
      }
      loadBalancerAttributes = [
        {
          key   = "idle_timeout.timeout_seconds"
          value = "60"
        },
        {
          key   = "routing.http.drop_invalid_header_fields.enabled"
          value = "true"
        }
      ]
    }
  }
}

# EKS Auto Mode IngressClass
resource "kubernetes_manifest" "ingress_class" {
  manifest = {
    apiVersion = "networking.k8s.io/v1"
    kind       = "IngressClass"
    metadata = {
      name = "alb-${local.config.app_name}"
      annotations = {
        "ingressclass.kubernetes.io/is-default-class" = "false"
      }
    }
    spec = {
      controller = "eks.amazonaws.com/alb"
      parameters = {
        apiGroup = "eks.amazonaws.com"
        kind     = "IngressClassParams"
        name     = "alb-${local.config.app_name}"
      }
    }
  }

  depends_on = [
    kubernetes_manifest.ingress_class_params
  ]
}

# Kubernetes Ingress using EKS Auto Mode
resource "kubernetes_ingress_v1" "api" {
  metadata {
    name = local.config.app_name
  }
  
  spec {
    ingress_class_name = "alb-${local.config.app_name}"
    
    rule {
      host = local.config.domain_name
      http {
        path {
          path      = "/"
          path_type = "Prefix"
          backend {
            service {
              name = kubernetes_service.api.metadata[0].name
              port {
                number = local.config.service_port
              }
            }
          }
        }
      }
    }
  }

  depends_on = [
    kubernetes_manifest.ingress_class
  ]
}