# BreachVault Deployment Guide

Complete instructions for deploying BreachVault to production environments.

## Table of Contents

1. [Docker Deployment (Recommended)](#docker-deployment)
2. [Bare Metal Deployment](#bare-metal-deployment)
3. [Cloud Platforms](#cloud-platforms)
4. [Nginx Configuration](#nginx-configuration)
5. [SSL/TLS Setup](#ssltls-setup)
6. [Scaling & Performance](#scaling--performance)

---

## Docker Deployment

### Prerequisites

- Docker 24.0+
- Docker Compose 2.20+
- 4GB+ RAM
- 20GB+ disk space (minimum)

### Quick Start

```bash
# Clone repository
git clone https://github.com/kwiklabs/BreachVault.git
cd BreachVault

# Configure environment
cp .env.example .env
nano .env  # Edit configuration

# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Check health
curl http://localhost:8000/health
```

### Environment Variables

```bash
# .env file
# Database
POSTGRES_USER=breachvault
POSTGRES_PASSWORD=<strong-password>
POSTGRES_DB=breachvault
DATABASE_URL=postgresql://breachvault:<password>@postgres:5432/breachvault

# Redis
REDIS_URL=redis://redis:6379

# Admin credentials (CHANGE THESE!)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<strong-password>

# JWT Secret (generate with: openssl rand -hex 32)
JWT_SECRET=<random-secret-key>

# API URLs
NEXT_PUBLIC_API_URL=http://localhost:8000
API_URL=http://backend:8000
```

### Production Configuration

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  postgres:
    restart: always
    volumes:
      - postgres_data:/var/lib/postgresql/data
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G

  redis:
    restart: always
    command: redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru

  backend:
    restart: always
    environment:
      - LOG_LEVEL=WARNING
      - WORKERS=4
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 2G

  frontend:
    restart: always
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 1G

volumes:
  postgres_data:
    driver: local
```

Run with: `docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d`

---

## Bare Metal Deployment

### System Requirements

- Ubuntu 22.04 LTS or RHEL 8+
- 8GB+ RAM
- 100GB+ SSD storage
- Python 3.12+
- Node.js 20+
- PostgreSQL 16+
- Redis 7+

### Installation Steps

#### 1. Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install PostgreSQL
sudo apt install postgresql-16 postgresql-contrib -y

# Install Redis
sudo apt install redis-server -y

# Install Python
sudo apt install python3.12 python3.12-venv python3-pip -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs -y

# Install pnpm
npm install -g pnpm
```

#### 2. Setup Database

```bash
# Create database and user
sudo -u postgres psql << EOF
CREATE USER breachvault WITH PASSWORD 'your-password';
CREATE DATABASE breachvault OWNER breachvault;
GRANT ALL PRIVILEGES ON DATABASE breachvault TO breachvault;
EOF
```

#### 3. Deploy Backend

```bash
# Clone repository
git clone https://github.com/kwiklabs/BreachVault.git
cd BreachVault/backend

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cat > .env << EOF
DATABASE_URL=postgresql://breachvault:your-password@localhost:5432/breachvault
REDIS_URL=redis://localhost:6379
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-admin-password
JWT_SECRET=$(openssl rand -hex 32)
EOF

# Run migrations (if applicable)
# alembic upgrade head

# Start backend with systemd
sudo tee /etc/systemd/system/breachvault-backend.service << EOF
[Unit]
Description=BreachVault Backend API
After=network.target postgresql.service redis.service

[Service]
User=www-data
WorkingDirectory=/opt/BreachVault/backend
Environment="PATH=/opt/BreachVault/backend/venv/bin"
EnvironmentFile=/opt/BreachVault/backend/.env
ExecStart=/opt/BreachVault/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable breachvault-backend
sudo systemctl start breachvault-backend
```

#### 4. Deploy Frontend

```bash
cd ../frontend

# Install dependencies
pnpm install

# Build production bundle
pnpm build

# Start with PM2
npm install -g pm2
pm2 start npm --name "breachvault-frontend" -- start
pm2 save
pm2 startup
```

---

## Cloud Platforms

### AWS Deployment

#### Using ECS + RDS

```bash
# 1. Create RDS PostgreSQL instance
# 2. Create ElastiCache Redis cluster
# 3. Build and push Docker images to ECR
# 4. Create ECS task definitions
# 5. Deploy with ALB

# Build and push
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com

docker build -t breachvault-backend backend/
docker tag breachvault-backend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/breachvault-backend:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/breachvault-backend:latest

docker build -t breachvault-frontend frontend/
docker tag breachvault-frontend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/breachvault-frontend:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/breachvault-frontend:latest
```

### Google Cloud Platform (GCP)

```bash
# Deploy to Cloud Run with Cloud SQL
gcloud builds submit --tag gcr.io/PROJECT_ID/breachvault-backend backend/
gcloud run deploy breachvault-backend --image gcr.io/PROJECT_ID/breachvault-backend --platform managed
```

### Azure

```bash
# Deploy to Azure Container Instances
az container create \
  --resource-group breachvault \
  --name breachvault-backend \
  --image breachvault-backend:latest \
  --dns-name-label breachvault \
  --ports 8000
```

---

## Nginx Configuration

### Reverse Proxy Setup

```nginx
# /etc/nginx/sites-available/breachvault
upstream backend {
    least_conn;
    server 127.0.0.1:8000;
    # Add more backend servers for load balancing
    # server 127.0.0.1:8001;
}

upstream frontend {
    server 127.0.0.1:3000;
}

# Rate limiting
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=web_limit:10m rate=30r/s;

server {
    listen 80;
    server_name breachvault.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name breachvault.yourdomain.com;
    
    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/breachvault.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/breachvault.yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # API backend
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        
        proxy_pass http://backend/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Frontend
    location / {
        limit_req zone=web_limit burst=50 nodelay;
        
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
    
    # Static files caching
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable and reload:

```bash
sudo ln -s /etc/nginx/sites-available/breachvault /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## SSL/TLS Setup

### Let's Encrypt (Certbot)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d breachvault.yourdomain.com

# Auto-renewal (already configured)
sudo certbot renew --dry-run
```

### Custom Certificate

```bash
# Generate private key
openssl genrsa -out private.key 4096

# Generate CSR
openssl req -new -key private.key -out certificate.csr

# Obtain signed certificate from CA
# Install certificate in nginx config
```

---

## Scaling & Performance

### Horizontal Scaling

```yaml
# docker-compose.scale.yml
services:
  backend:
    deploy:
      replicas: 4
  
  frontend:
    deploy:
      replicas: 2

  # Add load balancer
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend
      - frontend
```

### Database Optimization

```sql
-- Add indexes for better performance
CREATE INDEX idx_breached_hashes_hash ON breached_hashes(hash);
CREATE INDEX idx_breached_hashes_source ON breached_hashes(source);

-- Analyze tables
ANALYZE breached_hashes;

-- Vacuum regularly
VACUUM ANALYZE breached_hashes;
```

### Redis Optimization

```bash
# redis.conf
maxmemory 4gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### Monitoring

```bash
# Install Prometheus + Grafana
docker compose -f docker-compose.monitoring.yml up -d

# Endpoints to monitor
# - /health (backend health)
# - /metrics (Prometheus metrics)
# - PostgreSQL metrics
# - Redis metrics
```

---

## Troubleshooting

### Common Issues

**Database connection errors:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -h localhost -U breachvault -d breachvault
```

**Redis connection errors:**
```bash
# Check Redis
redis-cli ping

# View Redis logs
sudo tail -f /var/log/redis/redis-server.log
```

**High memory usage:**
```bash
# Check container stats
docker stats

# Adjust memory limits in docker-compose.yml
# Reduce bloom filter size in config.yml
```

**Slow imports:**
```bash
# Increase batch size in config.yml
# Add more workers
# Use SSD storage
# Optimize PostgreSQL settings
```

---

## Security Checklist

- [ ] Change default admin credentials
- [ ] Use strong JWT secret (32+ characters)
- [ ] Enable HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Enable rate limiting
- [ ] Regular security updates
- [ ] Database backups configured
- [ ] Monitor logs for suspicious activity
- [ ] Use environment variables (never commit secrets)
- [ ] Restrict admin panel access (IP whitelist)

---

## Support

- GitHub Issues: https://github.com/kwiklabs/BreachVault/issues
- Documentation: https://github.com/kwiklabs/BreachVault/wiki
- Email: support@kwik.gg
