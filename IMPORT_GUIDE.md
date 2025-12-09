# 🚀 BreachVault - Quick Setup Guide

## Automated Breach Data Import

### Option 1: Automated Script (Recommended)
```bash
# Run the automated downloader
cd /home/mmi/kwiklabs/BreachVault
./scripts/download-breaches.sh
```

This will download and import:
- ✅ RockYou (14M passwords) - Already done!
- SecLists common passwords (~1M)
- CrackStation (1.5B passwords) - Optional
- 10M password list compilation

### Option 2: Manual via Admin Panel

1. Go to http://localhost:3000/admin/login
2. Login with: `admin` / `changeme2025`
3. Upload any `.txt` file with passwords (one per line)

**File Validation:**
- Must be UTF-8 text
- Allowed extensions: `.txt`, `.lst`, `.dic`, `.wordlist`
- Max size: 100GB
- Files >10MB process in background

### Option 3: Command Line
```bash
# Copy file into container
sudo docker cp /path/to/passwords.txt breachvault-backend:/app/myfile.txt

# Import
sudo docker compose exec backend python scripts/seed_rockyou.py /app/myfile.txt source_name

# For large files, run in background
nohup sudo docker compose exec -T backend python scripts/seed_rockyou.py /app/myfile.txt source_name > ~/import.log 2>&1 &
```

## Current Status

**Database:** 14,343,690 passwords (rockyou.txt)
**Disk Space:** 650GB available
**Can fit:** All recommended datasets!

## Recommended Import Order

1. ✅ **RockYou** (14M) - Done!
2. **SecLists** (~1M) - Quick, high-quality passwords
3. **CrackStation** (1.5B) - Comprehensive coverage
4. **Custom sources** - Upload via admin panel

## Storage Requirements

| Dataset | Download | Extracted | DB Size | Total |
|---------|----------|-----------|---------|-------|
| RockYou | 134MB | 134MB | ~1GB | ✅ Done |
| SecLists | 50MB | 50MB | ~100MB | 200MB |
| CrackStation | 4.2GB | 15GB | ~40GB | ~60GB |
| **Total** | **4.4GB** | **15GB** | **~41GB** | **~60GB** |

**You have 650GB free - plenty of space!**

## After Import

1. Restart backend to update Bloom Filter:
   ```bash
   cd /home/mmi/kwiklabs/BreachVault
   sudo docker compose restart backend
   ```

2. Check stats: http://localhost:3000/stats

3. Test a password: http://localhost:3000

## Security Notes

- Files are validated before import
- Suspicious content is rejected
- Duplicates are automatically skipped
- All passwords are hashed with SHA-256
- Original files can be deleted after import

## Need Help?

- Check import logs: `~/crackstation_import.log`
- View database: `sudo docker compose exec -T postgres psql -U breachvault -d breachvault -c "SELECT COUNT(*) FROM breached_hashes;"`
- Monitor: `tail -f ~/crackstation_import.log`
