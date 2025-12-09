#!/bin/bash
# Real-time import monitoring for BreachVault

set -e

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}BreachVault Import Monitor${NC}"
echo "Press Ctrl+C to stop monitoring"
echo ""

LAST_COUNT=0
START_TIME=$(date +%s)

while true; do
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))
    
    # Get current count
    CURRENT_COUNT=$(sudo docker compose exec -T postgres psql -U breachvault -d breachvault -t -c "SELECT COUNT(*) FROM breached_hashes;" 2>/dev/null | xargs || echo "0")
    
    # Handle empty/non-numeric values
    if [ -z "$CURRENT_COUNT" ] || ! [[ "$CURRENT_COUNT" =~ ^[0-9]+$ ]]; then
        CURRENT_COUNT=0
    fi
    
    # Calculate rate
    if [ "$ELAPSED" -gt 0 ]; then
        TOTAL_RATE=$((CURRENT_COUNT / ELAPSED))
    else
        TOTAL_RATE=0
    fi
    
    # Calculate recent rate (since last check)
    if [ -n "$LAST_COUNT" ] && [ "$LAST_COUNT" -gt 0 ]; then
        RECENT_RATE=$((CURRENT_COUNT - LAST_COUNT))
    else
        RECENT_RATE=0
    fi
    
    # Format numbers with commas
    FORMATTED_COUNT=$(printf "%'d" $CURRENT_COUNT)
    FORMATTED_TOTAL_RATE=$(printf "%'d" $TOTAL_RATE)
    FORMATTED_RECENT_RATE=$(printf "%'d" $RECENT_RATE)
    
    # Clear line and print stats
    echo -ne "\r${GREEN}📊 Total: ${FORMATTED_COUNT}${NC} | "
    echo -ne "${CYAN}⚡ Avg: ${FORMATTED_TOTAL_RATE}/sec${NC} | "
    echo -ne "${YELLOW}Current: ${FORMATTED_RECENT_RATE}/sec${NC} | "
    echo -ne "⏱️  ${ELAPSED}s elapsed     "
    
    LAST_COUNT=$CURRENT_COUNT
    
    sleep 1
done
