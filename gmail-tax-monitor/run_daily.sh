#!/bin/bash

# Daily runner for Gmail Tax Monitor

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Run setup.sh first."
    exit 1
fi

# Run the monitor
echo "📧 Running Gmail Tax Monitor - $(date)"
python3 tax_monitor.py

# Check for errors
if [ $? -eq 0 ]; then
    echo "✅ Monitor completed successfully"
else
    echo "❌ Monitor encountered errors"
    exit 1
fi