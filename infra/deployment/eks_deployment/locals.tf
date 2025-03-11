locals {
  config = yamldecode(file("${path.module}/config/dev.yml"))
}