# BreachVault 🔐

<div align="center">
  <strong>Production-ready password breach checker</strong>
  <br>
  Ultra-fast lookup (Bloom Filter → Redis → PostgreSQL)
  <br>
  Built by <a href="https://github.com/kwiklabs">kwiklabs</a> for <a href="https://kwik.gg">kwik.gg</a>
</div>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#deployment">Deployment</a> •
  <a href="#configuration">Configuration</a> •
  <a href="#api">API</a>
</p>

---

## Features

- ✅ **Client-side SHA-256 hashing** – Never sends plaintext passwords
- ⚡ **Ultra-fast lookup** – Bloom Filter → Redis → PostgreSQL cascade
- 🔒 **Admin panel** – Upload breach files with automatic duplicate detection
- 🚀 **One-command deployment** – Docker + docker-compose
- 🧩 **Drop-in integration** – `<KwikIntegration />` component for kwik.gg
- 📊 **Real-time stats** – Track breach database size and sources

## Quick Start

```bash
# Clone the repository
git clone https://github.com/kwiklabs/BreachVault.git
cd BreachVault

# Set up environment variables
cp .env.example .env

# Start all services
docker compose up --build
```

That's it! The application will be available at:
- **Frontend**: http://localhost:3000
- **Admin Panel**: http://localhost:3000/admin
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Default Credentials

**Admin Login:**
- Username: `admin`
- Password: `changeme2025`

⚠️ **Change these immediately in production!** Edit the `.env` file.

## Features Highlight

### 🚀 Chunked Upload System

Upload breach files of **any size** (tested up to 100GB) without crashing:

- **Stream Processing**: Files are processed in 10MB chunks
- **Direct to Database**: Passwords are hashed and inserted directly - no temp files stored
- **Progress Tracking**: Real-time progress with speed and ETA
- **Duplicate Handling**: Automatic deduplication using `ON CONFLICT DO NOTHING`
- **Resume Capability**: Can pause and resume large uploads
- **Memory Efficient**: Never loads full file into memory

**Upload a 40GB breach file:**
```typescript
// Admin panel automatically uses chunked upload
// Processes ~100K passwords/second
// Uses ~100MB RAM regardless of file size
```

## Architecture

```
┌─────────────┐
│   Next.js   │ ← Client-side SHA-256 hashing + Chunked uploads
│   Frontend  │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│   FastAPI   │ ← Stream processing (no temp file storage)
│   Backend   │
└──────┬──────┘
       │
       ↓
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    Bloom    │ →   │    Redis    │ →   │ PostgreSQL  │
│   Filter    │     │   (24h TTL) │     │  (Source)   │
└─────────────┘     └─────────────┘     └─────────────┘
```

### Lookup Flow

1. **Bloom Filter** – Fast negative check (~1μs)
2. **Redis Cache** – Hot data (24h TTL)
3. **PostgreSQL** – Full breach database

## API Endpoints

### Check Password
```bash
POST /api/v1/check
Content-Type: application/json

{
  "hash": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"
}
```

Response:
```json
{
  "breached": true,
  "source": "rockyou.txt",
  "timestamp": "2025-12-09T12:34:56Z"
}
```

### Import Breaches (Admin Only)
```bash
POST /api/v1/import
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data

file: <breach_file.txt>
source: "rockyou.txt"
```

Response:
```json
{
  "imported": 14344391,
  "skipped": 0,
  "total": 14344391,
  "source": "rockyou.txt"
}
```

## Integration with kwik.gg

Drop this component into your passphrase input:

```tsx
import { KwikIntegration } from '@/components/KwikIntegration'

export function PassphraseModal() {
  const [passphrase, setPassphrase] = useState('')
  const [showWarning, setShowWarning] = useState(false)

  return (
    <div>
      <input
        value={passphrase}
        onChange={(e) => setPassphrase(e.target.value)}
      />

      <KwikIntegration
        passphrase={passphrase}
        onBreached={() => setShowWarning(true)}
      />

      {showWarning && (
        <div className="text-red-500">
          ⚠️ This password has been breached!
        </div>
      )}
    </div>
  )
}
```

## Development

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Importing Breach Data

### Via Admin Panel
1. Go to http://localhost:3000/admin
2. Login with admin credentials
3. Upload a breach file (one hash per line)
4. Monitor progress in real-time

### Via Script
```bash
# Seed with rockyou.txt (example)
docker compose exec backend python scripts/seed_rockyou.py /path/to/rockyou.txt
```

## Production Deployment

### Environment Variables
Edit `.env` and set:
- `JWT_SECRET` – Generate with `openssl rand -hex 32`
- `NEXTAUTH_SECRET` – Generate with `openssl rand -hex 32`
- `ADMIN_USERNAME` / `ADMIN_PASSWORD` – Secure credentials
- `DATABASE_URL` – Production PostgreSQL connection
- `REDIS_URL` – Production Redis connection

### Docker Compose
```bash
docker compose -f docker-compose.prod.yml up -d
```

### Kubernetes / Cloud
See [deployment docs](./docs/deployment.md) for Kubernetes, AWS, GCP, Azure guides.

## Tech Stack

- **Backend**: FastAPI, asyncpg, aioredis, pybloom-live
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, shadcn/ui
- **Database**: PostgreSQL 16
- **Cache**: Redis 7
- **Auth**: JWT (backend) + NextAuth (frontend)

## Security

- Passwords are **never** transmitted in plaintext
- SHA-256 hashing happens client-side
- JWT tokens expire after 24 hours
- Rate limiting on all endpoints
- Admin panel requires authentication

## Performance

- **Bloom Filter**: ~100M hashes, 0.1% false positive rate
- **Redis Cache**: 24h TTL, LRU eviction
- **Database**: Indexed hash column, ~1ms lookup
- **Total Lookup**: <10ms for cached results

## License

MIT License - see [LICENSE](./LICENSE)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/BreachVault/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/BreachVault/discussions)
- 📧 **Email**: support@breachvault.dev

---

Built with ❤️ for [kwik.gg](https://kwik.gg) | Securing the web, one password at a time.
