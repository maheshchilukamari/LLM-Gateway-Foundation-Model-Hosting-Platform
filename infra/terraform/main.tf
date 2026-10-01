resource "aws_ecr_repository" "gateway" {
  name                 = "${var.project_name}-${var.environment}"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_s3_bucket" "artifacts" {
  bucket_prefix = "${var.project_name}-${var.environment}-artifacts-"
}

# Production deployments would add VPC, EKS node groups, RDS PostgreSQL,
# ElastiCache Redis, IAM roles for service accounts, ALB controller integration,
# Secrets Manager, and optional GPU node groups. This scoped foundation keeps the
# repo safe to inspect without accidentally provisioning expensive resources.

