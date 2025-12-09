#!/bin/bash
# BreachVault - Automated Breach Database Downloader
# Downloads common password breach datasets for research purposes

set -e

DOWNLOAD_DIR="${1:-$HOME/Downloads/breaches}"
CONTAINER_NAME="breachvault-backend"

echo "🔐 BreachVault Breach Data Downloader"
echo "======================================"
echo "Download directory: $DOWNLOAD_DIR"
echo ""

# Create download directory
mkdir -p "$DOWNLOAD_DIR"
cd "$DOWNLOAD_DIR"

# Function to import into BreachVault
import_to_db() {
    local file=$1
    local source=$2
    echo "📊 Importing $source into BreachVault..."
    
    # Copy to container
    docker cp "$file" $CONTAINER_NAME:/app/breach_data.txt
    
    # Import (run in background with nohup)
    GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
    docker compose -f "$GIT_ROOT/docker-compose.yml" exec -T $CONTAINER_NAME \
        python scripts/seed_rockyou.py /app/breach_data.txt "$source"
    
    # Cleanup
    docker compose -f "$GIT_ROOT/docker-compose.yml" exec -T $CONTAINER_NAME \
        rm /app/breach_data.txt
}

# 1. RockYou (already downloaded)
echo "✅ RockYou (14.3M passwords) - Already imported"

# 2. CrackStation Wordlist (1.5 billion passwords)
echo ""
echo "📥 CrackStation Wordlist (1.5 billion passwords)"
echo "⚠️  Download: 4.2GB | Uncompressed: 15GB | Database: ~40GB"
echo "⚠️  This will take a while to download and import!"
echo ""

if [ ! -f "crackstation.txt" ]; then
    if [ ! -f "crackstation.txt.gz" ]; then
        echo "Downloading crackstation.txt.gz (4.2GB)..."
        wget -c https://crackstation.net/files/crackstation.txt.gz
    fi
    
    echo "Extracting crackstation.txt..."
    gunzip -k crackstation.txt.gz
fi

if [ -f "crackstation.txt" ]; then
    echo "Importing CrackStation to database (this may take 20-30 minutes)..."
    import_to_db "crackstation.txt" "crackstation"
    echo "✅ CrackStation imported successfully!"
else
    echo "⚠️  Skipping CrackStation import"
fi

# 3. SecLists - Common Passwords
echo ""
echo "📥 Downloading SecLists..."
if [ ! -d "SecLists" ]; then
    git clone --depth 1 https://github.com/danielmiessler/SecLists.git
    
    # Combine common passwords
    cat SecLists/Passwords/Common-Credentials/*.txt \
        SecLists/Passwords/darkweb2017-top10000.txt \
        SecLists/Passwords/probable-v2-top1575.txt \
        > seclists-combined.txt 2>/dev/null || true
    
    echo "✅ SecLists downloaded"
    
    read -p "Import SecLists passwords now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        import_to_db "seclists-combined.txt" "seclists"
    fi
else
    echo "✅ SecLists already exists"
fi

# 4. 10 Million Password List Compilation
echo ""
echo "📥 10 Million Password List (~80MB)"
read -p "Download 10M password list? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ ! -f "10-million-password-list-top-1000000.txt" ]; then
        wget https://github.com/danielmiessler/SecLists/raw/master/Passwords/Common-Credentials/10-million-password-list-top-1000000.txt
        echo "✅ 10M list downloaded"
        
        read -p "Import now? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            import_to_db "10-million-password-list-top-1000000.txt" "10million"
        fi
    else
        echo "✅ 10M list already exists"
    fi
fi

echo ""
echo "======================================"
echo "✅ Download complete!"
echo ""
echo "Files in: $DOWNLOAD_DIR"
echo ""
echo "To manually import a file:"
GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
echo "  cd $GIT_ROOT"
echo "  sudo docker cp /path/to/file.txt $CONTAINER_NAME:/app/breach.txt"
echo "  sudo docker compose exec backend python scripts/seed_rockyou.py /app/breach.txt source_name"
echo ""
echo "Check database stats at: http://localhost:3000/stats"
