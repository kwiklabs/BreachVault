# BreachVault Quick Start Guide

## Getting Started in 60 Seconds

### 1. Navigate to Project
```bash
cd /home/mmi/kwiklabs/BreachVault
```

### 2. Start All Services
```bash
docker compose up --build
```

Wait for:
```
✅ BreachVault started successfully with 0 hashes
```

### 3. Access the Application

Open in your browser:
- **Public Checker**: http://localhost:3000
- **Admin Panel**: http://localhost:3000/admin
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 4. Login to Admin

- URL: http://localhost:3000/admin/login
- Username: `admin`
- Password: `changeme2025`

## Import Sample Data (Optional)

Create a test file:
```bash
cat > /tmp/test_breaches.txt << 'EOF'
password
123456
qwerty
letmein
welcome
EOF
```

Upload via Admin Panel:
1. Go to http://localhost:3000/admin
2. Enter source name: "test_data"
3. Upload `/tmp/test_breaches.txt`
4. Watch import progress

## Test the API

### Check a Password (that exists)
```bash
# The hash for "password" is:
curl -X POST http://localhost:8000/api/v1/check \
  -H "Content-Type: application/json" \
  -d '{"hash": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"}'
```

Response:
```json
{
  "breached": true,
  "source": "test_data",
  "timestamp": "2025-12-09T..."
}
```

### Check a Password (that doesn't exist)
```bash
# Random hash that's not in database
curl -X POST http://localhost:8000/api/v1/check \
  -H "Content-Type: application/json" \
  -d '{"hash": "0000000000000000000000000000000000000000000000000000000000000000"}'
```

Response:
```json
{
  "breached": false
}
```

## Integrate into kwik.gg

### Step 1: Copy Integration Files

```bash
# From BreachVault directory
cp frontend/components/KwikIntegration.tsx ../kwik/components/security/
cp frontend/lib/crypto.ts ../kwik/lib/
cp frontend/lib/api.ts ../kwik/lib/breachvault.ts
```

### Step 2: Install Dependencies in kwik.gg

```bash
cd ../kwik
npm install lucide-react
```

### Step 3: Add to Environment

```bash
# In kwik/.env.local
echo "NEXT_PUBLIC_BREACHVAULT_API=http://localhost:8000" >> .env.local
```

### Step 4: Use in Passphrase Input

Edit your passphrase modal (example location: `components/FileUpload.tsx` or similar):

```tsx
import { KwikIntegration } from '@/components/security/KwikIntegration'
import { useState } from 'react'

export function PassphraseModal() {
  const [passphrase, setPassphrase] = useState('')
  const [breachWarning, setBreachWarning] = useState(false)

  return (
    <div>
      <input
        type="password"
        value={passphrase}
        onChange={(e) => setPassphrase(e.target.value)}
        placeholder="Enter passphrase..."
      />

      {/* Drop-in BreachVault integration */}
      <KwikIntegration
        passphrase={passphrase}
        onBreached={() => setBreachWarning(true)}
      />

      {breachWarning && (
        <div className="warning">
          ⚠️ This passphrase has been found in a data breach.
          Consider using a different one for better security.
        </div>
      )}

      <button onClick={handleSubmit}>
        Continue {breachWarning && '(Not Recommended)'}
      </button>
    </div>
  )
}
```

## Common Commands

### View Logs
```bash
docker compose logs -f backend
docker compose logs -f frontend
```

### Restart Services
```bash
docker compose restart
```

### Stop Services
```bash
docker compose down
```

### Reset Database (Caution!)
```bash
docker compose down -v  # Deletes all data!
docker compose up --build
```

### Check Statistics
```bash
curl http://localhost:8000/api/v1/stats
```

### Admin Login via API
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "changeme2025"}'
```

Save the token:
```bash
export TOKEN="<access_token_from_response>"
```

### Import via API
```bash
curl -X POST http://localhost:8000/api/v1/import \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/breaches.txt" \
  -F "source=rockyou.txt"
```

## Production Checklist

Before deploying to production:

1. **Change Credentials**
   ```bash
   # Generate secrets
   openssl rand -hex 32  # For JWT_SECRET
   openssl rand -hex 32  # For NEXTAUTH_SECRET

   # Edit .env
   vim .env
   ```

2. **Update Environment**
   - Set strong `ADMIN_PASSWORD`
   - Set production `DATABASE_URL`
   - Set production `REDIS_URL`
   - Set production `NEXT_PUBLIC_API_URL`

3. **Configure HTTPS**
   - Add nginx reverse proxy
   - Install SSL certificates
   - Update CORS settings

4. **Test Integration**
   ```bash
   cd ../kwik
   npm run dev
   # Test the passphrase modal
   ```

## Troubleshooting

### Backend won't start
```bash
# Check if ports are in use
lsof -i :8000
lsof -i :5432
lsof -i :6379

# Check logs
docker compose logs backend --tail=100
```

### Frontend build fails
```bash
cd frontend
rm -rf .next node_modules
npm install
npm run build
```

### Database connection issues
```bash
# Check PostgreSQL is running
docker compose ps postgres

# Test connection
docker compose exec postgres psql -U breachvault -c "SELECT 1"
```

### Redis connection issues
```bash
# Check Redis is running
docker compose ps redis

# Test connection
docker compose exec redis redis-cli ping
```

## Next Steps

1. ✅ Test the public checker at http://localhost:3000
2. ✅ Upload some breach data via admin panel
3. ✅ Test API endpoints with curl
4. ✅ Integrate into kwik.gg passphrase modal
5. ✅ Test the integration end-to-end
6. 📊 Monitor performance and adjust bloom filter settings
7. 🚀 Deploy to production when ready

## Support

- **Project README**: `/home/mmi/kwiklabs/BreachVault/README.md`
- **Deployment Guide**: `/home/mmi/kwiklabs/BreachVault/DEPLOYMENT.md`
- **Integration Guide**: `/home/mmi/kwiklabs/BreachVault/KWIK_INTEGRATION.md`
- **Project Summary**: `/home/mmi/kwiklabs/BreachVault/PROJECT_SUMMARY.md`

---

**Ready to integrate!** 🎯

The `KwikIntegration` component is your one-line solution to add password breach checking to kwik.gg.
