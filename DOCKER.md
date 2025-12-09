# Docker Learning Guide - BreachVault

This guide teaches you Docker by doing. You'll learn the essential commands and concepts hands-on with this project.

## What is Docker?

Docker runs applications in **containers** - isolated environments that package code, dependencies, and system tools together. Think of them as lightweight virtual machines.

**Key Concepts:**
- **Image**: Blueprint for a container (like a class in programming)
- **Container**: Running instance of an image (like an object)
- **Volume**: Persistent storage that survives container restarts
- **Network**: How containers talk to each other
- **Compose**: Tool to run multi-container apps (like our 4-service setup)

## Your BreachVault Stack

```
┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│  Frontend   │   │   Backend   │   │  PostgreSQL │   │    Redis    │
│   (Next.js) │◄─►│  (FastAPI)  │◄─►│  (Database) │   │   (Cache)   │
│  Port 3000  │   │  Port 8000  │   │  Port 5433  │   │  Port 6379  │
└─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘
```

## Essential Docker Commands

### 1. Starting Everything

```bash
# Start all services in background (-d = detached mode)
docker compose up -d

# What this does:
# - Reads docker-compose.yml
# - Pulls images if needed (postgres:16-alpine, redis:7-alpine)
# - Builds custom images (backend, frontend)
# - Creates network for containers to communicate
# - Starts all 4 containers
```

### 2. Checking Status

```bash
# See running containers
docker compose ps

# See ALL containers (including stopped)
docker ps -a

# Check resource usage (CPU, RAM, Network)
docker stats

# Example output:
# CONTAINER ID   NAME                CPU %     MEM USAGE / LIMIT
# a1b2c3d4e5f6   breachvault-backend   2.5%      180MiB / 8GiB
```

### 3. Viewing Logs

```bash
# Follow logs from all services
docker compose logs -f

# Follow logs from specific service
docker compose logs -f backend
docker compose logs -f frontend

# See last 100 lines
docker compose logs --tail=100 backend

# Filter by time
docker compose logs --since 30m backend
```

**Pro tip:** Logs show errors, API requests, database queries. Essential for debugging!

### 4. Stopping Services

```bash
# Stop all containers (keeps them for restart)
docker compose stop

# Stop specific service
docker compose stop backend

# Stop AND remove containers (but keeps volumes/data)
docker compose down

# Nuclear option - remove EVERYTHING including volumes (deletes database!)
docker compose down -v
```

### 5. Rebuilding After Code Changes

```bash
# Rebuild images (needed after changing Dockerfile or backend/frontend code)
docker compose build

# Rebuild specific service
docker compose build backend

# Rebuild and restart
docker compose up -d --build

# Rebuild without using cache (if having issues)
docker compose build --no-cache
```

**When to rebuild:**
- Changed backend Python code → `docker compose build backend`
- Changed frontend Next.js code → `docker compose build frontend`
- Changed `Dockerfile` → `docker compose build`
- Changed dependencies (package.json, requirements.txt) → `docker compose build --no-cache`

### 6. Accessing Container Shell

```bash
# Get shell in running container
docker compose exec backend sh
docker compose exec frontend sh

# Now you're INSIDE the container - try:
# ls -la          (see files)
# ps aux          (see running processes)
# env             (see environment variables)
# exit            (leave container)

# Access PostgreSQL database
docker compose exec db psql -U breachvault -d breachvault

# Once in PostgreSQL:
# \dt                              (list tables)
# SELECT COUNT(*) FROM breached_hashes;  (count passwords)
# \q                               (quit)
```

### 7. Viewing Container Details

```bash
# Inspect container configuration (JSON output)
docker compose exec backend env

# See network configuration
docker network ls
docker network inspect breachvault_default

# See volumes
docker volume ls
docker volume inspect breachvault_postgres_data
```

### 8. Resource Management

```bash
# Remove stopped containers
docker container prune

# Remove unused images (frees disk space)
docker image prune

# Remove unused volumes (⚠️ deletes data!)
docker volume prune

# Remove EVERYTHING unused
docker system prune -a
```

## Common Workflows

### Workflow 1: Making Code Changes

```bash
# 1. Edit your code (e.g., backend/app/routers/breach_chunk.py)
vim backend/app/routers/breach_chunk.py

# 2. Rebuild the service
docker compose build backend

# 3. Restart it
docker compose up -d backend

# 4. Watch logs for errors
docker compose logs -f backend
```

### Workflow 2: Debugging Issues

```bash
# 1. Check if containers are running
docker compose ps

# 2. Check logs for errors
docker compose logs --tail=50 backend

# 3. Check resource usage (maybe out of memory?)
docker stats

# 4. Access container to investigate
docker compose exec backend sh
# Inside container:
ps aux                    # See processes
df -h                     # Disk space
cat /proc/meminfo         # Memory info

# 5. Restart problematic service
docker compose restart backend
```

### Workflow 3: Database Operations

```bash
# Backup database
docker compose exec db pg_dump -U breachvault breachvault > backup.sql

# Restore database
cat backup.sql | docker compose exec -T db psql -U breachvault -d breachvault

# Reset database completely
docker compose down
docker volume rm breachvault_postgres_data
docker compose up -d

# Import passwords from script
docker compose exec backend python scripts/seed_rockyou.py
```

### Workflow 4: Performance Testing

```bash
# Monitor while uploading large file
docker stats

# Check database size
docker compose exec db psql -U breachvault -d breachvault -c "SELECT pg_size_pretty(pg_database_size('breachvault'));"

# Check backend memory usage
docker compose exec backend ps aux | grep python

# See network traffic
docker stats --format "table {{.Name}}\t{{.NetIO}}"
```

## Understanding docker-compose.yml

```yaml
services:
  db:
    image: postgres:16-alpine          # Use official PostgreSQL image
    ports:
      - "5433:5432"                   # Map host:container ports
    environment:
      POSTGRES_PASSWORD: breachpass   # Set via env vars
    volumes:
      - postgres_data:/var/lib/postgresql/data  # Persist data

  backend:
    build: ./backend                  # Build from Dockerfile in backend/
    depends_on:
      - db                            # Start db first
    environment:
      DATABASE_URL: postgresql://...  # Connection string
```

**Key points:**
- `ports`: `host:container` - access container port via host port
- `volumes`: Named volumes persist data, bind mounts sync code
- `depends_on`: Start order (but doesn't wait for ready state)
- `environment`: Pass config to container

## Troubleshooting

### Port Already in Use
```bash
# Find what's using port 5433
lsof -i :5433
# Kill it or change port in docker-compose.yml
```

### Container Keeps Restarting
```bash
# Check logs
docker compose logs backend
# Usually: syntax error, missing env var, connection refused
```

### Out of Disk Space
```bash
# See disk usage
docker system df

# Clean up
docker system prune -a
docker volume prune
```

### Changes Not Reflecting
```bash
# Rebuild without cache
docker compose build --no-cache
docker compose up -d
```

### Database Connection Failed
```bash
# Check if db is ready
docker compose exec db pg_isready

# Check connection from backend
docker compose exec backend ping db
```

## Quick Reference Card

```bash
# Start everything
docker compose up -d

# View logs
docker compose logs -f [service]

# Rebuild after changes
docker compose build [service]
docker compose up -d [service]

# Shell access
docker compose exec [service] sh

# Database access
docker compose exec db psql -U breachvault -d breachvault

# Stop everything
docker compose down

# Resource monitoring
docker stats

# Clean up
docker system prune
```

## Learning More

- **Official Docs**: https://docs.docker.com/compose/
- **Docker Hub**: https://hub.docker.com/ (find images)
- **Best Practices**: https://docs.docker.com/develop/dev-best-practices/

**Practice exercises:**
1. Stop backend, change log level in code, rebuild, restart
2. Access PostgreSQL, run queries, export results
3. Monitor memory usage during large upload
4. Create database backup, delete everything, restore
5. Add new environment variable to docker-compose.yml

Remember: **containers are ephemeral** (temporary). Always use volumes for important data!
