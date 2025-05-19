#!/bin/bash

# This script runs the Telegram verification bot in the background
# and makes sure it restarts if it crashes

echo "Starting UMFST Campus Verification Bot..."

# Check if TELEGRAM_TOKEN is set
if [ -z "$TELEGRAM_TOKEN" ]; then
    echo "ERROR: TELEGRAM_TOKEN environment variable is not set."
    echo "Please set it first with: export TELEGRAM_TOKEN=your_bot_token"
    exit 1
fi

# Function to run the bot
run_bot() {
    echo "Starting bot at $(date)"
    python3 telegram_bot.py
    echo "Bot exited at $(date) with status $?"
    echo "Restarting in 5 seconds..."
    sleep 5
}

# Keep running the bot even if it crashes
while true; do
    run_bot
done