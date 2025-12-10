#!/bin/bash
# Split weakpass_4.txt into 1M line chunks (smaller = faster feedback)

INPUT="$HOME/Downloads/weakpass_4.txt"
OUTPUT_DIR="$HOME/Downloads/weakpass_chunks"

mkdir -p "$OUTPUT_DIR"

echo "Splitting $INPUT into 1M line chunks..."
echo "Output: $OUTPUT_DIR"
echo ""

cd "$OUTPUT_DIR"
split -l 1000000 -d --additional-suffix=.txt "$INPUT" chunk_

echo ""
echo "Done! Chunks created:"
ls -lh chunk_*.txt
