# Infrastructure as Code (IAC)

This directory contains all infrastructure configuration for SmartKitchen Connect.

## Structure

```
IAC/
├── docker/                     # Docker configurations
│   ├── docker-compose.yml      # Main compose file
│   ├── docker-compose.dev.yml  # Development overrides
│   └── docker-compose.prod.yml # Production overrides
├── kubernetes/                 # Kubernetes manifests (optional)
│   ├── deployments/
│   ├── services/
│   └── ingress/
├── terraform/                  # Terraform scripts (optional)
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
└── nginx/                      # Nginx configurations
    ├── nginx.conf              # Main configuration
    └── ssl/                    # SSL certificates
```

## Requirements

**Traceability:**
- RNF-05: Docker deployment support
- RNF-03: Secure HTTPS configuration
- RNF-01: Performance optimization

## Design Thinking

**Ideare:** 
- Containerization ensures consistency across environments
- Infrastructure as code enables reproducibility

**Prototype:**
- Docker Compose for rapid local development
- Kubernetes for scalable production deployment

**Evaluate:**
- Monitor deployment metrics
- Optimize resource allocation based on usage

## Quick Start

### Development with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### Production Deployment

See deployment guide in `Docs/deployment/`.

## Services

| Service | Port | Purpose |
|---------|------|---------|
| backend | 8000 | Django API server |
| db | 5432 | PostgreSQL database |
| redis | 6379 | Cache and message broker |
| celery_worker | - | Background task processor |
| celery_beat | - | Scheduled task manager |
| nginx | 80, 443 | Reverse proxy and static files |

## Environment Variables

Configure services using `.env` file in Backend directory. See `.env.example` for required variables.

## Security Notes (RNF-03)

- Change default passwords in production
- Use SSL certificates for HTTPS
- Restrict database access
- Keep images updated
- Use secrets management for sensitive data
