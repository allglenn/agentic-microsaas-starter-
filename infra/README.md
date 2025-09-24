# Infrastructure (Terraform)

Infrastructure as Code for deploying the Agentic MicroSaaS platform to Google Cloud Platform with **environment separation** (dev, staging, prod).

## 🚀 Features

- **Google Cloud Platform** deployment
- **Cloud Run** for containerized services
- **Cloud SQL** with PostgreSQL and pgvector
- **Redis** for caching and task queues
- **Cloud Storage** for static assets
- **IAM** roles and permissions
- **VPC** networking configuration

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Google Cloud Platform                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Cloud Run   │  │ Cloud Run   │  │ Cloud Run   │         │
│  │   (Web)     │  │   (API)     │  │  (Agent)    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│         │                 │                 │               │
│         └─────────────────┼─────────────────┘               │
│                           │                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Cloud SQL   │  │   Redis     │  │Cloud Storage│         │
│  │ PostgreSQL  │  │   Cache     │  │   Bucket    │         │
│  │ + pgvector  │  │             │  │             │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Prerequisites

- **Google Cloud SDK** installed and configured
- **Terraform** 1.6.0 or later
- **Docker** for building container images
- **gcloud** CLI authenticated with your GCP project

### Setup Google Cloud

1. **Create a GCP project**:
   ```bash
   gcloud projects create agentic-microsaas --name="Agentic MicroSaaS"
   gcloud config set project agentic-microsaas
   ```

2. **Enable required APIs**:
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable sqladmin.googleapis.com
   gcloud services enable redis.googleapis.com
   gcloud services enable storage.googleapis.com
   ```

3. **Set up authentication**:
   ```bash
   gcloud auth application-default login
   ```

## 🚀 Deployment

### Environment-Specific Deployment

The infrastructure is now organized into separate environments with different configurations:

#### **Development Environment**

```bash
# 1. Initialize Terraform for development
make tf.init.dev

# 2. Plan deployment
make tf.plan.dev

# 3. Apply configuration
make tf.apply.dev

# 4. Deploy applications
make cr.deploy.dev
```

#### **Staging Environment**

```bash
# 1. Initialize Terraform for staging
make tf.init.staging

# 2. Plan deployment
make tf.plan.staging

# 3. Apply configuration
make tf.apply.staging

# 4. Deploy applications
make cr.deploy.staging
```

#### **Production Environment**

```bash
# 1. Initialize Terraform for production
make tf.init.prod

# 2. Plan deployment
make tf.plan.prod

# 3. Apply configuration
make tf.apply.prod

# 4. Deploy applications
make cr.deploy.prod
```

### Environment Configuration

Each environment has its own configuration:

- **Development**: Small instances, public IPs, no deletion protection
- **Staging**: Medium instances, private IPs, staging-specific settings
- **Production**: Large instances, high availability, monitoring, deletion protection

## 📁 Infrastructure Components

### Cloud SQL (PostgreSQL)

```hcl
resource "google_sql_database_instance" "main" {
  name             = "${var.project_id}-db"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = "db-f1-micro"
    
    database_flags {
      name  = "shared_preload_libraries"
      value = "vector"
    }
  }
}
```

**Features:**
- PostgreSQL 15 with pgvector extension
- Automated backups
- High availability configuration
- Private IP networking

### Cloud Run Services

```hcl
resource "google_cloud_run_service" "web" {
  name     = "web"
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/web:latest"
        ports {
          container_port = 3000
        }
      }
    }
  }
}
```

**Features:**
- Auto-scaling based on traffic
- HTTPS by default
- Custom domains support
- Environment variable injection

### Redis Cache

```hcl
resource "google_redis_instance" "cache" {
  name           = "${var.project_id}-cache"
  tier           = "BASIC"
  memory_size_gb = 1
  region         = var.region
}
```

**Features:**
- In-memory data store
- High availability
- Automatic failover
- Redis AUTH support

### Cloud Storage

```hcl
resource "google_storage_bucket" "static" {
  name          = "${var.project_id}-static"
  location      = "US"
  force_destroy = true
}
```

**Features:**
- Static asset hosting
- CDN integration
- Lifecycle management
- Access control

## 🔧 Configuration

### Variables

```hcl
variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "agentic-microsaas"
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "europe-west1"
}
```

### Environment-Specific Configurations

Create separate `.tfvars` files for different environments:

**development.tfvars:**
```hcl
project_id = "agentic-microsaas-dev"
region     = "europe-west1"
```

**production.tfvars:**
```hcl
project_id = "agentic-microsaas-prod"
region     = "europe-west1"
```

## 🔒 Security

### IAM Roles

```hcl
resource "google_cloud_run_service_iam_member" "web_public" {
  service  = google_cloud_run_service.web.name
  location = google_cloud_run_service.web.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
```

### Network Security

- **VPC**: Private network configuration
- **Firewall Rules**: Restrictive access controls
- **SSL/TLS**: End-to-end encryption
- **Private IPs**: Database and cache on private network

## 📊 Monitoring

### Cloud Monitoring

- **Application Metrics**: Custom metrics for API calls and task processing
- **Infrastructure Metrics**: CPU, memory, and network usage
- **Log Aggregation**: Centralized logging with Cloud Logging
- **Alerting**: Automated alerts for critical issues

### Cost Optimization

- **Auto-scaling**: Scale down during low usage
- **Resource Sizing**: Right-size instances based on usage
- **Scheduled Scaling**: Scale down during off-hours
- **Reserved Instances**: Long-term cost savings

## 🚀 CI/CD Integration

### GitHub Actions

```yaml
name: Deploy Infrastructure
on:
  push:
    branches: [main]
    paths: ['infra/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: hashicorp/setup-terraform@v1
      - name: Terraform Init
        run: terraform init
      - name: Terraform Apply
        run: terraform apply -auto-approve
```

### GitLab CI

```yaml
deploy_infrastructure:
  stage: deploy
  image: hashicorp/terraform:1.6.0
  script:
    - terraform init
    - terraform plan
    - terraform apply -auto-approve
  only:
    - main
```

## 🔄 Maintenance

### Updates

```bash
# Update Terraform providers
terraform init -upgrade

# Plan updates
terraform plan

# Apply updates
terraform apply
```

### Backup Strategy

- **Database Backups**: Automated daily backups with 30-day retention
- **Configuration Backups**: Terraform state stored in Cloud Storage
- **Disaster Recovery**: Multi-region deployment capability

## 💰 Cost Estimation

### Monthly Costs (Estimated)

- **Cloud Run**: $10-50 (depending on traffic)
- **Cloud SQL**: $25-100 (depending on instance size)
- **Redis**: $15-30 (depending on memory)
- **Cloud Storage**: $5-20 (depending on usage)
- **Total**: ~$55-200/month

### Cost Optimization Tips

1. **Use Preemptible Instances** for non-critical workloads
2. **Implement Auto-scaling** to scale down during low usage
3. **Use Committed Use Discounts** for predictable workloads
4. **Monitor and Alert** on cost thresholds

## 🐛 Troubleshooting

### Common Issues

1. **API Not Enabled**:
   ```bash
   gcloud services enable [SERVICE_NAME].googleapis.com
   ```

2. **Permission Denied**:
   ```bash
   gcloud auth application-default login
   ```

3. **Resource Quotas**:
   ```bash
   gcloud compute project-info describe --project=PROJECT_ID
   ```

### Debug Commands

```bash
# Check Terraform state
terraform show

# Validate configuration
terraform validate

# Check resource status
gcloud run services list
gcloud sql instances list
```

## 📚 Additional Resources

- [Terraform Google Provider Documentation](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud SQL Documentation](https://cloud.google.com/sql/docs)
- [Redis Documentation](https://cloud.google.com/memorystore/docs/redis)
