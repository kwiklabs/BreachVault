#!/bin/bash
# Process chunks and DELETE when done - simple auto-resume

CHUNK_DIR="$HOME/Downloads/weakpass_chunks"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKERS=3  # Reduced to avoid "too many clients"

if [ ! -d "$CHUNK_DIR" ]; then
    echo "Error: $CHUNK_DIR not found"
    echo "Run ./split-wordlist.sh first"
    exit 1
fi

echo "═══════════════════════════════════════════════════════════"
echo "  DATASEED MASTER-9000: Auto-Delete Chunk Processing"
echo "═══════════════════════════════════════════════════════════"
echo ""

while true; do
    # Find remaining chunks
    CHUNKS=($(ls "$CHUNK_DIR"/chunk_*.txt 2>/dev/null))
    
    if [ ${#CHUNKS[@]} -eq 0 ]; then
        echo ""
        echo "✅ All chunks processed!"
        break
    fi
    
    echo "Remaining chunks: ${#CHUNKS[@]}"
    echo ""
    
    # Process next batch in parallel
    printf '%s\n' "${CHUNKS[@]:0:$WORKERS}" | \
        parallel -j $WORKERS \
        "python3 -u $SCRIPT_DIR/process-chunk.py {} weakpass_4 && rm -f {}"
    
    echo ""
    echo "Batch complete, checking for more..."
    sleep 1
done

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  🏆 ALL CHUNKS COMPLETE"
echo "═══════════════════════════════════════════════════════════"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  ✅ ALL CHUNKS COMPLETE"
echo "═══════════════════════════════════════════════════════════"
