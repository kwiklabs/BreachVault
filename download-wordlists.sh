#!/bin/bash
# Download massive password wordlists for BreachVault

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

DOWNLOAD_DIR="$HOME/Downloads"
cd "$DOWNLOAD_DIR"

echo ""
echo -e "${BOLD}${CYAN}╔════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${CYAN}║      Massive Wordlist Downloader          ║${NC}"
echo -e "${BOLD}${CYAN}╚════════════════════════════════════════════╝${NC}"
echo ""

# Function to extract weakpass_4.txt.7z
extract_weakpass() {
    if [ -f "weakpass_4.txt" ]; then
        echo -e "${GREEN}✓ weakpass_4.txt already extracted${NC}"
        return 0
    fi
    
    if [ ! -f "weakpass_4.txt.7z" ]; then
        echo -e "${RED}✗ weakpass_4.txt.7z not found${NC}"
        return 1
    fi
    
    echo -e "${CYAN}📦 Extracting weakpass_4.txt.7z (5.1GB)...${NC}"
    echo -e "${YELLOW}   This may take 5-10 minutes${NC}"
    
    # Try different extraction methods
    if command -v 7z &> /dev/null; then
        7z x weakpass_4.txt.7z
    elif command -v 7za &> /dev/null; then
        7za x weakpass_4.txt.7z
    else
        echo -e "${YELLOW}⚠️  Installing p7zip-full...${NC}"
        # Try different package managers
        if command -v apt &> /dev/null; then
            sudo apt update && sudo apt install -y p7zip-full
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y p7zip p7zip-plugins
        elif command -v pacman &> /dev/null; then
            sudo pacman -S --noconfirm p7zip
        else
            echo -e "${RED}✗ Cannot install 7zip. Please install manually:${NC}"
            echo -e "   Ubuntu/Debian: sudo apt install p7zip-full"
            echo -e "   Fedora: sudo dnf install p7zip"
            echo -e "   Arch: sudo pacman -S p7zip"
            return 1
        fi
        7z x weakpass_4.txt.7z
    fi
    
    echo -e "${GREEN}✅ Extracted weakpass_4.txt${NC}"
    ls -lh weakpass_4.txt
}

# Download CrackStation
download_crackstation() {
    if [ -f "crackstation.txt" ]; then
        echo -e "${GREEN}✓ crackstation.txt already exists${NC}"
        return 0
    fi
    
    echo -e "${CYAN}📥 Downloading CrackStation wordlist${NC}"
    echo -e "${BOLD}   • 1.5 billion passwords${NC}"
    echo -e "${BOLD}   • 15GB compressed → 64GB uncompressed${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  This is a HUGE download${NC}"
    read -p "Continue? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        return 1
    fi
    
    echo -e "${CYAN}⬇️  Downloading (this will take a while)...${NC}"
    wget -c https://crackstation.net/files/crackstation.txt.gz
    
    echo -e "${CYAN}📦 Extracting...${NC}"
    gunzip crackstation.txt.gz
    
    echo -e "${GREEN}✅ Downloaded crackstation.txt${NC}"
    ls -lh crackstation.txt
}

# Show current status
echo -e "${BOLD}Current wordlists:${NC}"
echo ""

if [ -f "rockyou.txt" ]; then
    size=$(du -sh rockyou.txt | cut -f1)
    lines=$(wc -l < rockyou.txt)
    echo -e "  ${GREEN}✓${NC} rockyou.txt ($size, $(printf "%'d" $lines) passwords)"
fi

if [ -f "weakpass_4.txt" ]; then
    size=$(du -sh weakpass_4.txt | cut -f1)
    lines=$(wc -l < weakpass_4.txt 2>/dev/null || echo "?")
    echo -e "  ${GREEN}✓${NC} weakpass_4.txt ($size, $(printf "%'d" $lines) passwords)"
elif [ -f "weakpass_4.txt.7z" ]; then
    size=$(du -sh weakpass_4.txt.7z | cut -f1)
    echo -e "  ${YELLOW}⏳${NC} weakpass_4.txt.7z ($size, needs extraction)"
fi

if [ -f "crackstation.txt" ]; then
    size=$(du -sh crackstation.txt | cut -f1)
    lines=$(wc -l < crackstation.txt 2>/dev/null || echo "?")
    echo -e "  ${GREEN}✓${NC} crackstation.txt ($size, $(printf "%'d" $lines) passwords)"
fi

echo ""
echo -e "${BOLD}Available actions:${NC}"
echo -e "  ${CYAN}1${NC} - Extract weakpass_4.txt.7z"
echo -e "  ${CYAN}2${NC} - Download CrackStation wordlist"
echo -e "  ${CYAN}3${NC} - Do both"
echo -e "  ${CYAN}q${NC} - Quit"
echo ""
read -p "Choose: " choice

case $choice in
    1)
        extract_weakpass
        ;;
    2)
        download_crackstation
        ;;
    3)
        extract_weakpass
        download_crackstation
        ;;
    q)
        echo "Exiting"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${BOLD}${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${GREEN}║            All Done! 🎉                   ║${NC}"
echo -e "${BOLD}${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Now run:${NC} ${BOLD}cd /home/mmi/kwiklabs/BreachVault && ./import-all.sh${NC}"
echo ""
