#!/bin/bash
# Auto-restart script for CollBomber Bot
# Checks every 5 minutes if bot is running, restarts if not

cd /root/workspace
BOT_PID=$(pgrep -f "collbomber_bot.py" | head -1)

if [ -z "$BOT_PID" ]; then
    echo "$(date): Bot not running, starting supervisord..."
    supervisord -c supervisord.conf 2>/dev/null
    sleep 3
    BOT_PID=$(pgrep -f "collbomber_bot.py" | head -1)
    if [ -n "$BOT_PID" ]; then
        echo "$(date): ✅ Bot started successfully (PID: $BOT_PID)"
    else
        echo "$(date): ❌ Bot failed to start"
    fi
else
    echo "$(date): ✅ Bot running (PID: $BOT_PID)"
fi
