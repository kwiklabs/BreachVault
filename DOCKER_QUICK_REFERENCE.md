# Quick Reference: Docker Management

## Common Commands

### Start Services
```bash
./docker-manage.sh start
```

### Stop Services
```bash
./docker-manage.sh stop
```

### Restart Services (without rebuilding)
```bash
./docker-manage.sh restart
```

### Rebuild After Code Changes ⭐
```bash
./docker-manage.sh rebuild
```
**Use this after:**
- Editing backend Python code
- Editing frontend React code
- Changing dependencies
- Modifying Dockerfiles

### View Logs
```bash
# All services
./docker-manage.sh logs

# Backend only
./docker-manage.sh logs-backend

# Frontend only
./docker-manage.sh logs-frontend
```

### Check Status
```bash
./docker-manage.sh status
```

### Pull Updates from Git and Rebuild
```bash
./docker-manage.sh update
```

### Clean Containers (Keep Data)
```bash
./docker-manage.sh clean
```

### Reset Everything (DELETES DATA!)
```bash
./docker-manage.sh reset
```

## Typical Workflows

### 1. Making Code Changes

```bash
# Edit your code files
nano backend/app/routers/breach_chunk.py

# Rebuild and restart
./docker-manage.sh rebuild

# Check logs to verify
./docker-manage.sh logs-backend
```

### 2. Debugging Issues

```bash
# Check service status
./docker-manage.sh status

# View real-time logs
./docker-manage.sh logs-backend

# Open shell in backend container
./docker-manage.sh shell

# Check database
./docker-manage.sh db
```

### 3. Daily Operations

```bash
# Morning: Start services
./docker-manage.sh start

# Check everything is running
./docker-manage.sh status

# Evening: Stop services
./docker-manage.sh stop
```

### 4. Updating Production

```bash
# Pull latest code from Git
git pull

# Rebuild containers
./docker-manage.sh rebuild

# Verify everything works
./docker-manage.sh status
./docker-manage.sh logs
```

## Manual Docker Commands

If you prefer manual control:

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# Rebuild specific service
docker compose build backend
docker compose up -d backend

# View logs
docker compose logs -f backend

# Execute command in container
docker compose exec backend python --version

# Database shell
docker compose exec postgres psql -U breachvault -d breachvault

# Backend shell
docker compose exec backend /bin/bash

# Check resource usage
docker stats

# Remove all stopped containers
docker compose down -v
```

## Troubleshooting

### Port Already in Use
```bash
# Stop services
./docker-manage.sh stop

# Check what's using the port
sudo lsof -i :3000  # Frontend
sudo lsof -i :8000  # Backend
sudo lsof -i :5433  # PostgreSQL

# Kill the process or change ports in docker-compose.yml
```

### Database Connection Issues
```bash
# Restart database
docker compose restart postgres

# Check database logs
docker compose logs postgres

# Access database directly
./docker-manage.sh db
```

### Out of Memory
```bash
# Check current usage
docker stats

# Clean unused images/containers
docker system prune -a

# Restart services
./docker-manage.sh restart
```

### Code Changes Not Appearing
```bash
# Rebuild containers (no cache)
docker compose build --no-cache

# Or use the script
./docker-manage.sh rebuild
```

## Backup & Restore

### Backup Database
```bash
docker compose exec postgres pg_dump -U breachvault breachvault > backup_$(date +%Y%m%d).sql
```

### Restore Database
```bash
docker compose exec -T postgres psql -U breachvault breachvault < backup_20251209.sql
```

### Backup Docker Volumes
```bash
docker run --rm -v breachvault_postgres_data:/data -v $(pwd):/backup ubuntu tar czf /backup/postgres_backup.tar.gz /data
```

## Environment Variables

Edit `.env` file and restart:

```bash
# Edit environment
nano .env

# Rebuild to apply changes
./docker-manage.sh rebuild
```

## Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000

# API docs
open http://localhost:8000/docs
```

## Performance Monitoring

```bash
# Real-time stats
docker stats

# Container sizes
docker system df

# Detailed inspection
docker compose exec backend python -c "import psutil; print(f'CPU: {psutil.cpu_percent()}%, RAM: {psutil.virtual_memory().percent}%')"
```
