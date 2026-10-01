output "ecr_repository_url" {
  value = aws_ecr_repository.gateway.repository_url
}

output "artifact_bucket" {
  value = aws_s3_bucket.artifacts.bucket
}

