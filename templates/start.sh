#!/bin/bash
# Launch full pipeline: recording + live transcription
#
# Usage:
#   ./start.sh                    # defaults (small model, 30s chunks)
#   ./start.sh turbo 45           # turbo model, 45s chunks
#   ./start.sh tiny 15            # tiny model (fast), 15s chunks
#   ./start.sh small 30 en        # small model, 30s, English
#   ./start.sh medium 60 de       # medium model, 60s, German

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MODEL=${1:-small}
CHUNK_SEC=${2:-30}
LANG=${3:-en}
TITLE=${4:-"Workshop"}

echo "========================================"
echo "  LIVE PROMPTER"
echo "========================================"
echo ""
echo "  Whisper model:  $MODEL"
echo "  Chunk duration: ${CHUNK_SEC}s"
echo "  Language:       $LANG"
echo "  Title:          $TITLE"
echo "  Chunks:         $SCRIPT_DIR/chunks/"
echo "  Transcripts:    $SCRIPT_DIR/transcripts/"
echo "  Log:            $SCRIPT_DIR/live_log.jsonl"
echo "  Summary:        $SCRIPT_DIR/live_summary.md"
echo ""
echo "  Ctrl+C to stop both processes"
echo ""

# Start recorder in background
bash "$SCRIPT_DIR/record_chunks.sh" "$CHUNK_SEC" "$SCRIPT_DIR/chunks" &
RECORDER_PID=$!
sleep 1

# Start transcriber in background
python3 "$SCRIPT_DIR/transcribe_live.py" \
    --model "$MODEL" \
    --lang "$LANG" \
    --chunks-dir "$SCRIPT_DIR/chunks" \
    --title "$TITLE" &
TRANSCRIBER_PID=$!

cleanup() {
    echo ""
    echo "Stopping recorder (PID $RECORDER_PID) and transcriber (PID $TRANSCRIBER_PID)..."
    kill $RECORDER_PID 2>/dev/null
    kill $TRANSCRIBER_PID 2>/dev/null
    wait $RECORDER_PID 2>/dev/null
    wait $TRANSCRIBER_PID 2>/dev/null
    echo "Done. Check: $SCRIPT_DIR/live_summary.md"
}
trap cleanup EXIT INT TERM

wait
