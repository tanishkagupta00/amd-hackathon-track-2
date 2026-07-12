#!/bin/bash
set -e

MODE="${1:-cli}"  # Default to CLI mode if no argument

echo "==================================================="
echo "  CaptionForge AI - Starting in $MODE mode"
echo "==================================================="

# Verify API key
if [ -z "$FIREWORKS_API_KEY" ]; then
    echo "ERROR: FIREWORKS_API_KEY is not set."
    echo "Run with: -e FIREWORKS_API_KEY=<your_key>"
    exit 1
fi
echo "[OK] FIREWORKS_API_KEY is present."

# â”€â”€ Mode 1: CLI (Headless for hackathon evaluation) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if [ "$MODE" = "cli" ]; then
    echo "Mode: CLI (Batch Processing)"

    # Verify input file
    if [ ! -f "/input/tasks.json" ]; then
        echo "ERROR: /input/tasks.json not found."
        echo "Mount your input directory with: -v /path/to/input:/input"
        exit 1
    fi
    echo "[OK] /input/tasks.json found."

    # Run the headless pipeline
    echo "Starting inference pipeline..."
    cd /app
    PYTHONPATH=/app/backend python /app/backend/runner.py

    # Verify output
    if [ ! -f "/output/results.json" ]; then
        echo "ERROR: /output/results.json was not created."
        exit 2
    fi

    echo "[OK] /output/results.json written successfully."
    echo "==================================================="
    echo "  Pipeline completed successfully!"
    echo "==================================================="
    exit 0

# â”€â”€ Mode 2: Web (For manual demo/testing) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
elif [ "$MODE" = "web" ]; then
    echo "Mode: Web Server"
    echo "Starting FastAPI server on port 8000..."
    echo "API endpoints: http://localhost:8000/api/v1/"
    echo "Frontend UI:   http://localhost:8000/"
    echo "==================================================="

    cd /app
    export PYTHONPATH=/app/backend
    exec uvicorn backend.main:app --host 0.0.0.0 --port 8000

else
    echo "ERROR: Invalid mode '$MODE'. Use 'cli' or 'web'."
    exit 1
fi
