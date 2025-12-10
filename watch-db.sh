#!/bin/bash
# Live database growth monitor with speed calculation

PREV_COUNT=0
PREV_TIME=$(date +%s)

while true; do
    COUNT=$(sudo docker exec breachvault-postgres psql -U breachvault -d breachvault -t -c "SELECT COUNT(*) FROM breached_hashes" 2>/dev/null | tr -d ' ')
    
    if [ -z "$COUNT" ]; then
        echo "Waiting for database..."
        sleep 5
        continue
    fi
    
    NOW=$(date +%s)
    ELAPSED=$((NOW - PREV_TIME))
    
    if [ $PREV_COUNT -gt 0 ] && [ $ELAPSED -ge 5 ]; then
        DIFF=$((COUNT - PREV_COUNT))
        RATE=$((DIFF / ELAPSED))
        TIMESTAMP=$(date '+%H:%M:%S')
        
        echo "[$TIMESTAMP] Total: $COUNT | +$DIFF in ${ELAPSED}s | Speed: $RATE/s"
        
        PREV_COUNT=$COUNT
        PREV_TIME=$NOW
    elif [ $PREV_COUNT -eq 0 ]; then
        TIMESTAMP=$(date '+%H:%M:%S')
        echo "[$TIMESTAMP] Starting count: $COUNT"
        PREV_COUNT=$COUNT
        PREV_TIME=$NOW
    fi
    
    sleep 5
done
