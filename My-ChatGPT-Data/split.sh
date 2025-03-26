#!/bin/bash

# Default chunk size (5 MB = 5 * 1024 * 1024 bytes)
CHUNK_SIZE=$((5 * 1024 * 1024))
# Output directory
OUTPUT_DIR="chunks"
# Flag to reassemble (default: off)
REASSEMBLE=false

# Parse command-line flags
while getopts "r" opt; do
    case $opt in
        r) REASSEMBLE=true ;;
        *) echo "Usage: $0 [-r] <file>"; exit 1 ;;
    esac
done

# Shift past the options to get the file argument
shift $((OPTIND-1))

# Check if a file is provided
if [ -z "$1" ]; then
    echo "Error: Please provide a file to split or reassemble (e.g., chat.html or conversation.json)"
    echo "Usage: $0 [-r] <file>"
    exit 1
fi

INPUT_FILE="$1"
BASENAME=$(basename "$INPUT_FILE" | cut -f 1 -d '.') # e.g., "chat" or "conversation"
PREFIX="${BASENAME}_part_"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

if [ "$REASSEMBLE" = false ]; then
    # Split mode
    echo "Splitting $INPUT_FILE into $CHUNK_SIZE-byte chunks..."
    split -b "$CHUNK_SIZE" "$INPUT_FILE" "$OUTPUT_DIR/$PREFIX"
    echo "Split complete! Files are in $OUTPUT_DIR/"
    ls -lh "$OUTPUT_DIR/${PREFIX}"*
else
    # Reassemble mode
    echo "Reassembling chunks into $BASENAME.reassembled..."
    cat "$OUTPUT_DIR/${PREFIX}"* > "$BASENAME.reassembled"
    echo "Reassembly complete! Output: $BASENAME.reassembled"
    ls -lh "$BASENAME.reassembled"
fi
