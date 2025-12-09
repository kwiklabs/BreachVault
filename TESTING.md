# BreachVault Testing Guide

## Project Verification ✅

All project files have been created and verified:

### Backend Files
- ✅ `backend/Dockerfile`
- ✅ `backend/requirements.txt`
- ✅ `backend/app/main.py` - FastAPI application with lifespan events
- ✅ `backend/app/config.py` - Settings management
- ✅ `backend/app/models.py` - Pydantic models
- ✅ `backend/app/dependencies.py` - JWT authentication
- ✅ `backend/app/middleware.py` - Rate limiting + logging
- ✅ `backend/app/routers/auth.py` - Admin authentication
- ✅ `backend/app/routers/check.py` - Breach checking (Bloom → Redis → PostgreSQL)
- ✅ `backend/app/routers/import.py` - File upload with deduplication
- ✅ `backend/app/routers/health.py` - Health checks + stats
- ✅ `backend/app/services/bloom.py` - Bloom filter service
- ✅ `backend/app/services/cache.py` - Redis cache service
- ✅ `backend/app/services/db.py` - PostgreSQL service
- ✅ `backend/app/utils/hash.py` - Hash utilities
- ✅ `backend/scripts/seed_rockyou.py` - Bulk import script

### Frontend Files
- ✅ `frontend/Dockerfile`
- ✅ `frontend/package.json`
- ✅ `frontend/tsconfig.json`
- ✅ `frontend/next.config.mjs`
- ✅ `frontend/tailwind.config.js`
- ✅ `frontend/app/layout.tsx` - Root layout
- ✅ `frontend/app/page.tsx` - Public password checker
- ✅ `frontend/app/globals.css` - Styles
- ✅ `frontend/app/admin/page.tsx` - Admin dashboard
- ✅ `frontend/app/admin/login/page.tsx` - Admin login
- ✅ `frontend/app/stats/page.tsx` - Statistics page
- ✅ `frontend/components/PasswordChecker.tsx` - Main checker UI
- ✅ `frontend/components/BreachResult.tsx` - Result display
- ✅ `frontend/components/UploadBreachForm.tsx` - Admin file upload
- ✅ `frontend/components/KwikIntegration.tsx` - 🎯 kwik.gg integration component
- ✅ `frontend/lib/crypto.ts` - Client-side SHA-256
- ✅ `frontend/lib/api.ts` - API client
- ✅ `frontend/lib/cn.ts` - Tailwind utilities

### Configuration Files
- ✅ `docker-compose.yml` - Container orchestration
- ✅ `.env.example` - Environment template
- ✅ `.env` - Local environment (created)
- ✅ `.gitignore` - Git ignore rules
- ✅ `LICENSE` - MIT License

### Documentation Files
- ✅ `README.md` - Main documentation
- ✅ `QUICKSTART.md` - Quick start guide
- ✅ `DEPLOYMENT.md` - Deployment guide
- ✅ `KWIK_INTEGRATION.md` - Integration guide
- ✅ `PROJECT_SUMMARY.md` - Technical overview
- ✅ `TESTING.md` - This file

## Manual Testing Steps

Since automatic Docker testing encountered permission issues, here's how to test manually:

### 1. Start Services

```bash
cd /home/mmi/kwiklabs/BreachVault
docker compose up --build
```

**Expected Output:**
```
🚀 Starting BreachVault...
📊 Loading existing hashes into Bloom Filter...
✅ BreachVault started successfully with 0 hashes
```

### 2. Test Backend Health

```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "database": "up",
  "redis": "up",
  "bloom_filter": "initialized"
}
```

### 3. Test API Documentation

Open browser: http://localhost:8000/docs

**Expected:** Interactive Swagger UI with all endpoints

### 4. Test Frontend

Open browser: http://localhost:3000

**Expected:** Public password checker page with:
- Password input field
- "Check Password" button
- Privacy notice about client-side hashing

### 5. Test Password Check (No Data Yet)

In browser at http://localhost:3000:
1. Enter any password (e.g., "test123")
2. Click "Check Password"

**Expected:** Green "Password Safe" message

### 6. Test Admin Login

1. Navigate to http://localhost:3000/admin/login
2. Username: `admin`
3. Password: `changeme2025`
4. Click "Login"

**Expected:** Redirect to admin dashboard

### 7. Test Admin Dashboard

At http://localhost:3000/admin:

**Expected to see:**
- Statistics cards (Total Hashes: 0, Sources: 0, etc.)
- Upload Breach File form
- Home and Statistics buttons
- Logout button

### 8. Import Test Data

Create a test file:
```bash
cat > /tmp/test_passwords.txt << 'EOF'
password
123456
qwerty
letmein
welcome
admin
EOF
```

In Admin Dashboard:
1. Source name: `test_data`
2. Choose file: `/tmp/test_passwords.txt`
3. Click "Upload and Import"

**Expected:**
- Success message
- Imported: 6
- Skipped: 0
- Total: 6

### 9. Test Breach Check (With Data)

Return to http://localhost:3000:
1. Enter "password" in the checker
2. Click "Check Password"

**Expected:**
- Red warning: "Password Compromised!"
- Source: "test_data"
- Recommendation message

### 10. Test API Directly

```bash
# Test with "password" (SHA-256 hash)
curl -X POST http://localhost:8000/api/v1/check \
  -H "Content-Type: application/json" \
  -d '{"hash": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"}'
```

**Expected Response:**
```json
{
  "breached": true,
  "source": "test_data",
  "timestamp": "2025-12-09T..."
}
```

### 11. Test Statistics Page

Navigate to http://localhost:3000/stats

**Expected:**
- Total Hashes: 6
- Bloom Filter Size: 6
- Redis Keys: (varies)
- Sources: test_data

### 12. Test Authentication

```bash
# Login via API
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "changeme2025"}' \
  | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

echo "Token: $TOKEN"

# Verify token
curl -X GET http://localhost:8000/api/v1/auth/verify \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:**
```json
{
  "valid": true,
  "username": "admin"
}
```

### 13. Test Import via API

```bash
curl -X POST http://localhost:8000/api/v1/import \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/test_passwords.txt" \
  -F "source=test_data_2"
```

**Expected:**
```json
{
  "imported": 6,
  "skipped": 0,
  "total": 6,
  "source": "test_data_2"
}
```

## Performance Testing

### Test Bloom Filter Speed

```bash
# Should return instantly (< 10ms)
time curl -s -X POST http://localhost:8000/api/v1/check \
  -H "Content-Type: application/json" \
  -d '{"hash": "0000000000000000000000000000000000000000000000000000000000000000"}' > /dev/null
```

### Test Rate Limiting

```bash
# Should fail after 60 requests in a minute
for i in {1..65}; do
  curl -s -X POST http://localhost:8000/api/v1/check \
    -H "Content-Type: application/json" \
    -d '{"hash": "abc123"}' > /dev/null
  echo "Request $i"
done
```

**Expected:** HTTP 429 "Too Many Requests" after request 61

## kwik.gg Integration Testing

### 1. Copy Files to kwik.gg

```bash
# From BreachVault directory
cd /home/mmi/kwiklabs/BreachVault

# Copy integration component
cp frontend/components/KwikIntegration.tsx \
   /home/mmi/kwiklabs/kwik/components/security/

# Copy utilities
cp frontend/lib/crypto.ts /home/mmi/kwiklabs/kwik/lib/
cp frontend/lib/api.ts /home/mmi/kwiklabs/kwik/lib/breachvault.ts
```

### 2. Install Dependencies

```bash
cd /home/mmi/kwiklabs/kwik
npm install lucide-react
```

### 3. Add Environment Variable

```bash
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" >> .env.local
```

### 4. Test Integration

Add to your passphrase modal component:

```tsx
import { KwikIntegration } from '@/components/security/KwikIntegration'
import { useState } from 'react'

export function YourPassphraseModal() {
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

      {/* BreachVault integration */}
      <KwikIntegration
        passphrase={passphrase}
        onBreached={() => setBreachWarning(true)}
      />

      {breachWarning && (
        <div className="text-red-500 mt-2">
          ⚠️ This passphrase has been found in a data breach!
        </div>
      )}
    </div>
  )
}
```

### 5. Test End-to-End

1. Start kwik.gg dev server: `npm run dev`
2. Navigate to file upload/passphrase modal
3. Enter "password" (from test data)
4. Should see warning after 500ms debounce

## Troubleshooting

### Backend won't start

```bash
# Check logs
docker compose logs backend

# Check if ports are in use
lsof -i :8000
lsof -i :5432
lsof -i :6379
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
# Check PostgreSQL
docker compose ps postgres
docker compose logs postgres

# Test connection
docker compose exec postgres psql -U breachvault -c "SELECT 1"
```

### Redis connection issues

```bash
# Check Redis
docker compose ps redis
docker compose logs redis

# Test connection
docker compose exec redis redis-cli ping
```

### Bloom filter not initializing

Check backend logs:
```bash
docker compose logs backend | grep -i bloom
```

Expected:
```
📊 Loading existing hashes into Bloom Filter...
Bloom filter initialized with X hashes
```

## Test Checklist

- [ ] Backend starts successfully
- [ ] Frontend builds and starts
- [ ] PostgreSQL is healthy
- [ ] Redis is healthy
- [ ] Bloom filter initializes
- [ ] Health endpoint returns 200
- [ ] Public checker loads
- [ ] Admin login works
- [ ] Admin dashboard loads
- [ ] File upload works
- [ ] Breach check works (negative)
- [ ] Breach check works (positive)
- [ ] Statistics page loads
- [ ] API authentication works
- [ ] Rate limiting works
- [ ] Client-side hashing works
- [ ] kwik.gg integration works

## Security Testing

- [ ] Passwords are hashed client-side
- [ ] JWT tokens expire after 24h
- [ ] Admin panel requires authentication
- [ ] Rate limiting prevents abuse
- [ ] CORS is configured
- [ ] No SQL injection vulnerabilities
- [ ] No plaintext passwords in logs
- [ ] File upload validates input

## Performance Benchmarks

| Metric | Target | Test Command |
|--------|--------|--------------|
| Bloom check | < 1ms | `time curl ...check` |
| Redis lookup | < 5ms | With cached data |
| DB lookup | < 50ms | Cold cache |
| Import speed | > 1000/s | Upload 10k hashes |

## Status: ✅ Ready for Testing

All files created and verified. The project is ready for manual testing following the steps above.

**Note:** Due to permission restrictions, automated Docker testing couldn't be completed. Please follow the manual testing steps to verify the system works end-to-end.
