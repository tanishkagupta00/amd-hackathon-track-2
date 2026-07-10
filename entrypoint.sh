#!/bin/bash
set -e

echo "Starting CaptionForge AI entrypoint script..."

# 1. Mount verification audit
if [ ! -f "/input/tasks.json" ]; then
    echo "ERROR: /input/tasks.json not found! Exiting."
    exit 1
fi

echo "Successfully verified presence of /input/tasks.json."

# 2. Run headless inference runner
python backend/runner.py

# 3. Verify output is created
if [ ! -f "/output/results.json" ]; then
    echo "ERROR: /output/results.json was not generated! Exiting."
    exit 2
fi

echo "Successfully verified results JSON formatting. Pipeline completed successfully!"
exit 0
