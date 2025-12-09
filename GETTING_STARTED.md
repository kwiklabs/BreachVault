# 🚀 Getting Started with BreachVault

## Installation & First Run

### 1. Clone and Setup
```bash
git clone https://github.com/kwiklabs/BreachVault.git
cd BreachVault
cp .env.example .env
```

### 2. Configure Environment
```bash
nano .env
```

**Required Changes:**
```env
# Change these!
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD=StrongPassword123!
JWT_SECRET=generate_with_openssl_rand_hex_32

# Database (can keep defaults for development)
POSTGRES_USER=breachvault
POSTGRES_PASSWORD=YourSecureDBPassword
POSTGRES_DB=breachvault
```

**Generate JWT Secret:**
```bash
openssl rand -hex 32
```

### 3. Start Services
```bash
./docker-manage.sh start
```

Expected output:
```
ℹ Starting BreachVault services...
✓ Services started!
ℹ Frontend: http://localhost:3000
ℹ Backend API: http://localhost:8000
ℹ API Docs: http://localhost:8000/docs
```

### 4. Verify Installation
```bash
./docker-manage.sh status
```

Should show:
- ✅ postgres (healthy)
- ✅ redis (healthy)
- ✅ backend (healthy)
- ✅ frontend (healthy)

## Using BreachVault

### Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Main password checker |
| **Admin Panel** | http://localhost:3000/admin | Upload breach files |
| **API** | http://localhost:8000 | REST API |
| **API Docs** | http://localhost:8000/docs | Interactive documentation |
| **Stats** | http://localhost:3000/stats | Database statistics |

### First Login

1. Go to http://localhost:3000/admin
2. Login with credentials from `.env`:
   - Username: `your_admin_username`
   - Password: `StrongPassword123!`

### Upload Your First Breach File

#### Option 1: Via Admin Panel (Recommended for Large Files)

1. Visit http://localhost:3000/admin
2. Click "Click to select a breach file"
3. Choose your file (up to 100GB!)
4. Click "Start Upload"
5. Watch real-time progress:
   - Upload speed
   - Passwords processed
   - Time remaining

**Supports:**
- `.txt` - Plain text
- `.lst` - Password lists
- `.dic` - Dictionary files
- `.wordlist` - Wordlist files

#### Option 2: Use Pre-built Download Script

```bash
# Download popular breach datasets automatically
./scripts/download-breaches.sh
```

This downloads:
- RockYou (14M passwords, 133MB)
- CrackStation (1.5B passwords, 15GB)
- SecLists common passwords
- 10 Million Password List

#### Option 3: Manual Import Script

```bash
# For local files
cd backend/scripts
python seed_rockyou.py /path/to/your/passwords.txt
```

### Check a Password

#### Web Interface

1. Visit http://localhost:3000
2. Enter password in the checker
3. Click "Check Password"
4. Result shows:
   - ✅ Safe (not in database)
   - ❌ Compromised (found in breach)

#### API (Programmatic)

```bash
# Hash password with SHA-256
PASSWORD="password123"
HASH=$(echo -n "$PASSWORD" | sha256sum | cut -d' ' -f1)

# Check via API
curl -X POST http://localhost:8000/api/v1/check \
  -H "Content-Type: application/json" \
  -d "{\"hash\": \"$HASH\"}"
```

Response:
```json
{
  "breached": true,
  "source": "rockyou.txt"
}
```

## Common Workflows

### Daily Development

```bash
# Morning: Start services
./docker-manage.sh start

# Work on your code...
nano backend/app/routers/breach_chunk.py

# Apply changes (rebuilds containers)
./docker-manage.sh rebuild

# Check logs
./docker-manage.sh logs-backend

# Evening: Stop services
./docker-manage.sh stop
```

### Updating Code

```bash
# Pull latest changes
git pull

# Rebuild with new code
./docker-manage.sh rebuild

# Verify
./docker-manage.sh status
```

### Debugging

```bash
# View real-time logs
./docker-manage.sh logs-backend

# Check specific error
./docker-manage.sh logs-backend | grep ERROR

# Open shell in backend
./docker-manage.sh shell

# Access database
./docker-manage.sh db
```

### Production Deployment

```bash
# On server
git clone https://github.com/kwiklabs/BreachVault.git
cd BreachVault

# Configure for production
cp .env.example .env
nano .env  # Set production values

# Start services
./docker-manage.sh start

# Set up nginx (see DEPLOYMENT_GUIDE.md)
# Configure SSL (see DEPLOYMENT_GUIDE.md)

# Test
curl http://localhost:8000/health
```

## Troubleshooting

### Problem: Port Already in Use

```bash
# Check what's using port 3000
sudo lsof -i :3000

# Option 1: Kill the process
kill -9 <PID>

# Option 2: Change port in docker-compose.yml
ports:
  - "3001:3000"  # Use 3001 instead
```

### Problem: Services Won't Start

```bash
# Check logs
./docker-manage.sh logs

# Restart everything
./docker-manage.sh stop
./docker-manage.sh start

# Still failing? Reset and start fresh
./docker-manage.sh reset  # WARNING: Deletes data!
./docker-manage.sh start
```

### Problem: Upload Fails with "Malicious Pattern Detected"

Your file contains suspicious content. Check SECURITY.md for allowed patterns.

**Common causes:**
- File has SQL commands mixed in
- File contains script tags
- Binary file instead of text

**Solution:**
```bash
# Clean your file
cat passwords.txt | grep -v '^#' | grep -v '^//' > clean_passwords.txt

# Upload clean version
```

### Problem: Out of Disk Space

```bash
# Check space
df -h

# Clean Docker
docker system prune -a

# Remove old images
docker image prune -a

# Check database size
./docker-manage.sh db
SELECT pg_size_pretty(pg_database_size('breachvault'));
```

### Problem: Slow Performance

```bash
# Check resource usage
docker stats

# Adjust in config.yml
import:
  batch_size: 5000  # Reduce for less RAM
  max_workers: 2    # Reduce for less CPU

# Rebuild
./docker-manage.sh rebuild
```

## Testing Security

### Test Malicious Upload (Should Be Blocked)

```bash
# Create malicious test file
echo "password123'; DROP TABLE breached_hashes; --" > malicious.txt

# Try to upload (should fail)
# Visit admin panel and upload malicious.txt
# Expected: "Security validation failed: Malicious pattern detected"
```

### Test Valid Upload (Should Work)

```bash
# Create valid test file
cat > valid_passwords.txt << EOF
password123
qwerty123
letmein
admin123
EOF

# Upload via admin panel
# Expected: Success with 4 passwords processed
```

## Performance Benchmarks

**Tested on:**
- CPU: 4 cores
- RAM: 8GB
- Disk: SSD

**Results:**
- Upload speed: 100-200 MB/s (local)
- Processing: ~100K passwords/second
- Memory usage: ~100MB (constant)
- Database inserts: 10K batch, ~1s/batch

**40GB file:**
- Upload: 6 minutes
- Processing: 40 minutes
- Total passwords: 850 million
- Final DB size: 28GB

## Next Steps

1. ✅ **Upload breach data** - Use admin panel or download script
2. ✅ **Test password checker** - Try some passwords
3. ✅ **Configure for production** - See DEPLOYMENT_GUIDE.md
4. ✅ **Set up monitoring** - Check logs regularly
5. ✅ **Enable HTTPS** - Use Let's Encrypt
6. ✅ **Backup database** - Schedule daily backups

## Getting Help

- **Documentation**: See README.md, DEPLOYMENT_GUIDE.md, SECURITY.md
- **Issues**: https://github.com/kwiklabs/BreachVault/issues
- **Discussions**: https://github.com/kwiklabs/BreachVault/discussions
- **Email**: support@kwik.gg

## Quick Reference Card

```bash
# Essential Commands
./docker-manage.sh start       # Start all services
./docker-manage.sh stop        # Stop all services
./docker-manage.sh rebuild     # Apply code changes
./docker-manage.sh logs        # View logs
./docker-manage.sh status      # Check health

# URLs
http://localhost:3000          # Frontend
http://localhost:3000/admin    # Admin panel
http://localhost:8000          # API
http://localhost:8000/docs     # API docs

# Files
.env                           # Configuration
config.yml                     # Advanced settings
docker-compose.yml             # Docker setup
```

**Save this card for quick reference!**
