# BreachVault Deployment Guide

## Quick Start (Local Development)

```bash
# Clone and enter directory
git clone https://github.com/yourusername/BreachVault.git
cd BreachVault

# Copy environment file
cp .env.example .env

# Start all services
docker compose up --build
```

Access the application:
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Admin Panel: http://localhost:3000/admin

Default credentials:
- Username: `admin`
- Password: `changeme2025`

## Production Deployment

### 1. Environment Variables

Generate secure secrets:
```bash
# Generate JWT secret
openssl rand -hex 32

# Generate NextAuth secret
openssl rand -hex 32
```

Edit `.env` with production values:
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@db-host:5432/breachvault
POSTGRES_USER=breachvault
POSTGRES_PASSWORD=<strong-password>
POSTGRES_DB=breachvault

# Redis
REDIS_URL=redis://redis-host:6379/0

# Backend
JWT_SECRET=<generated-secret>
ADMIN_USERNAME=<your-admin-username>
ADMIN_PASSWORD=<strong-password>

# Frontend
NEXT_PUBLIC_API_URL=https://api.breachvault.yourdomain.com
NEXTAUTH_SECRET=<generated-secret>
NEXTAUTH_URL=https://breachvault.yourdomain.com
```

### 2. Docker Compose Production

```bash
# Build and start in detached mode
docker compose up -d --build

# View logs
docker compose logs -f

# Stop services
docker compose down
```

### 3. Kubernetes Deployment

Create Kubernetes manifests:

**namespace.yaml**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: breachvault
```

**postgres.yaml**
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: breachvault
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: breachvault
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:16-alpine
        env:
        - name: POSTGRES_DB
          value: breachvault
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: breachvault-secrets
              key: postgres-user
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: breachvault-secrets
              key: postgres-password
        ports:
        - containerPort: 5432
        volumeMounts:
        - mountPath: /var/lib/postgresql/data
          name: postgres-storage
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: breachvault
spec:
  ports:
  - port: 5432
  selector:
    app: postgres
```

Deploy:
```bash
kubectl apply -f namespace.yaml
kubectl apply -f postgres.yaml
kubectl apply -f redis.yaml
kubectl apply -f backend.yaml
kubectl apply -f frontend.yaml
kubectl apply -f ingress.yaml
```

### 4. AWS Deployment (ECS + RDS + ElastiCache)

1. Create RDS PostgreSQL instance
2. Create ElastiCache Redis cluster
3. Build and push Docker images to ECR
4. Create ECS task definitions
5. Deploy ECS services

### 5. GCP Deployment (Cloud Run + Cloud SQL + Memorystore)

```bash
# Build and push images
gcloud builds submit --tag gcr.io/PROJECT_ID/breachvault-backend ./backend
gcloud builds submit --tag gcr.io/PROJECT_ID/breachvault-frontend ./frontend

# Deploy to Cloud Run
gcloud run deploy breachvault-backend \
  --image gcr.io/PROJECT_ID/breachvault-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

gcloud run deploy breachvault-frontend \
  --image gcr.io/PROJECT_ID/breachvault-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### 6. Azure Deployment (Container Apps + Cosmos DB)

Use Azure Container Apps with Azure Database for PostgreSQL and Azure Cache for Redis.

## Post-Deployment

### 1. Import Breach Data

Via admin panel:
1. Navigate to /admin
2. Login with admin credentials
3. Upload breach files

Via CLI:
```bash
docker compose exec backend python scripts/seed_rockyou.py /path/to/breachfile.txt
```

### 2. Monitoring

Check health:
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "database": "up",
  "redis": "up",
  "bloom_filter": "initialized"
}
```

### 3. Backup

Backup PostgreSQL:
```bash
docker compose exec postgres pg_dump -U breachvault breachvault > backup.sql
```

Restore:
```bash
docker compose exec -T postgres psql -U breachvault breachvault < backup.sql
```

## Security Checklist

- [ ] Change default admin credentials
- [ ] Generate strong JWT_SECRET
- [ ] Generate strong NEXTAUTH_SECRET
- [ ] Use HTTPS in production
- [ ] Configure firewall rules
- [ ] Enable rate limiting
- [ ] Set up monitoring and alerts
- [ ] Regular security updates
- [ ] Backup database regularly

## Performance Optimization

### Bloom Filter Tuning

Edit `.env`:
```bash
BLOOM_FILTER_CAPACITY=100000000  # Adjust based on data size
BLOOM_FILTER_ERROR_RATE=0.001    # Lower = more memory, fewer false positives
```

### Redis Configuration

For high traffic:
```bash
CACHE_TTL=86400  # 24 hours in seconds
```

### Database Indexing

Already included in the schema:
```sql
CREATE INDEX idx_breached_hashes_source ON breached_hashes(source);
```

## Troubleshooting

### Backend won't start
```bash
# Check logs
docker compose logs backend

# Check database connection
docker compose exec backend python -c "from app.services.db import db_service; import asyncio; asyncio.run(db_service.connect())"
```

### Frontend build fails
```bash
# Clear cache and rebuild
cd frontend
rm -rf .next node_modules
npm install
npm run build
```

### Bloom filter initialization slow
- Reduce `BLOOM_FILTER_CAPACITY`
- Increase available memory
- Consider pre-building bloom filter and loading from file

## Scaling

### Horizontal Scaling

Backend can be scaled horizontally:
```yaml
backend:
  deploy:
    replicas: 3
```

Note: Bloom filter is initialized per instance. For large-scale deployments, consider using a shared bloom filter service.

### Vertical Scaling

Increase resources:
```yaml
backend:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 4G
```

## Support

For deployment issues:
- GitHub Issues: https://github.com/yourusername/BreachVault/issues
- Email: support@breachvault.dev
