# Password Breach Sources

## Legitimate Research Sources

### 1. Have I Been Pwned (HIBP) - Pwned Passwords
- **URL**: https://haveibeenpwned.com/Passwords
- **Size**: 900+ million SHA-1 hashes (Cloudflare-hosted)
- **Download**: https://downloads.pwnedpasswords.com/passwords/
- **Format**: SHA-1 hashes (you'll need to convert or adapt your script)
- **Note**: Download `pwned-passwords-sha1-ordered-by-hash-v8.7z` (~40GB compressed)

### 2. SecLists - Common Passwords
- **URL**: https://github.com/danielmiessler/SecLists
- **Command**: 
  ```bash
  git clone https://github.com/danielmiessler/SecLists.git
  cd SecLists/Passwords
  ```
- **Files**: 
  - `Common-Credentials/` - Top common passwords
  - `Leaked-Databases/` - Various breach compilations
  - `darkweb2017-top10000.txt` - 10k most common

### 3. Weakpass - Password Collections
- **URL**: https://weakpass.com/wordlist
- **Collections**:
  - `rockyou2021.txt` - 8.4 billion passwords (92GB)
  - Various other breach compilations
- **Note**: Register for free downloads

### 4. CrackStation - Password Dictionaries
- **URL**: https://crackstation.net/crackstation-wordlist-password-cracking-dictionary.htm
- **Size**: 15GB uncompressed (1.5 billion unique passwords)
- **Direct**: https://crackstation.net/files/crackstation.txt.gz

### 5. Hashes.org - Leaked Password Lists
- **URL**: https://hashes.org/left.php
- **Note**: Free leaked databases section

### 6. Breach Compilation Collections
- **LinkedIn (2012)**: 164M passwords
- **Adobe (2013)**: 150M passwords  
- **MySpace (2016)**: 360M passwords
- **Various**: Search for "breach compilation torrent" (use caution)

## Quick Import Commands

```bash
# Download CrackStation wordlist
cd ~/Downloads
wget https://crackstation.net/files/crackstation.txt.gz
gunzip crackstation.txt.gz

# Import to BreachVault
cd /home/mmi/kwiklabs/BreachVault
sudo docker cp ~/Downloads/crackstation.txt breachvault-backend:/app/
sudo docker compose exec backend python scripts/seed_rockyou.py /app/crackstation.txt crackstation

# SecLists common passwords
git clone --depth 1 https://github.com/danielmiessler/SecLists.git ~/Downloads/SecLists
cat ~/Downloads/SecLists/Passwords/Common-Credentials/*.txt > ~/Downloads/seclists-combined.txt
sudo docker cp ~/Downloads/seclists-combined.txt breachvault-backend:/app/
sudo docker compose exec backend python scripts/seed_rockyou.py /app/seclists-combined.txt seclists
```

## For Maximum Coverage (Advanced)

### HIBP Pwned Passwords (900M+ passwords)
```bash
# Download HIBP dataset (requires ~40GB storage)
cd ~/Downloads
wget https://downloads.pwnedpasswords.com/passwords/pwned-passwords-sha1-ordered-by-hash-v8.7z
7z x pwned-passwords-sha1-ordered-by-hash-v8.7z

# Note: These are SHA-1 hashes, not plaintext
# You'd need to modify the import script to handle SHA-1 instead of SHA-256
```

## Safety & Legal Notes

⚠️ **Important:**
- Only use for security research and testing YOUR OWN systems
- Don't use these to attack others (illegal)
- Publicly available breach data is legal to download for research
- Store securely and don't redistribute
- Check your local laws regarding data retention

## Current Database Stats
After rockyou.txt: **14.3M passwords**
After adding above sources: **Potentially 1-2 billion unique passwords**
