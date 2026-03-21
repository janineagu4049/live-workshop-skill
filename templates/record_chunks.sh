#!/bin/bash
# Records audio in fixed-duration chunks to chunks/ directory
# Usage: ./record_chunks.sh [duration_sec] [output_dir]
# Requires: sox (brew install sox / apt install sox)

CHUNK_DURATION=${1:-30}
OUTPUT_DIR=${2:-"$(dirname "$0")/chunks"}
mkdir -p "$OUTPUT_DIR"

echo "=== AUDIO RECORDER ==="
echo "Chunk: ${CHUNK_DURATION}s | Output: ${OUTPUT_DIR}"
echo "Ctrl+C to stop"
echo ""

COUNTER=0
while true; do
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    FILENAME="${OUTPUT_DIR}/chunk_${TIMESTAMP}_$(printf '%04d' $COUNTER).wav"
    echo "[$(date +%H:%M:%S)] Recording chunk #${COUNTER} → ${FILENAME}"
    rec -q -r 16000 -c 1 -b 16 "$FILENAME" trim 0 "$CHUNK_DURATION" 2>/dev/null
    COUNTER=$((COUNTER + 1))
done
