# AWS Architecture

The intended AWS deployment uses:

- EKS for container orchestration.
- ECR for gateway and model-serving images.
- Application Load Balancer for ingress.
- RDS PostgreSQL for metadata.
- ElastiCache Redis for cache and rate limiting.
- S3 for model artifacts, ingestion data, and benchmark artifacts.
- Secrets Manager for API keys and database credentials.
- CloudWatch for logs and platform metrics.
- Prometheus and Grafana for service-level metrics.
- Optional GPU EC2 node group for larger model serving.

```mermaid
flowchart TD
    Internet --> ALB[Application Load Balancer]
    ALB --> EKS[EKS Cluster]
    EKS --> Gateway[LLM Gateway Pods]
    Gateway --> ModelPods[Model Serving Pods]
    Gateway --> RDS[(RDS PostgreSQL)]
    Gateway --> Redis[(ElastiCache Redis)]
    Gateway --> S3[(S3)]
    Gateway --> CloudWatch[CloudWatch]
    Gateway --> Prom[Prometheus / Grafana]
    Secrets[Secrets Manager] --> EKS
```

Local development does not require AWS resources.

