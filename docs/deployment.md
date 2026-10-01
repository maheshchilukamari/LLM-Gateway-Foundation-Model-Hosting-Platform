# Deployment

## Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

Services:

- `gateway`
- `redis`
- `postgres`
- `prometheus`
- `grafana`

## Kubernetes

Example manifests live in `infra/kubernetes/`.

```bash
kubectl apply -f infra/kubernetes/
```

Use `secret-example.yaml` as a template only. Do not commit real secrets.

## Helm

```bash
helm install llm-gateway infra/helm/llm-gateway
```

## Terraform

The scoped Terraform foundation creates ECR and S3 resources and documents where production EKS, RDS, ElastiCache, IAM, and GPU node groups would be added.

```bash
cd infra/terraform
terraform init
terraform plan
```

