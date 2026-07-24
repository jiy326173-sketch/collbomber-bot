#!/bin/bash
# Ultimate keep-alive for CollBomber Bot
# Runs every 2 minutes via cron
# Starts bot, supervisord, and monitors everything

cd /root/workspace

# Function to check if bot is alive
check_bot() {
    python3 -c "
import requests
try:
    exec(open('config_token.py').read())
    r = requests.get('https://api.telegram.org/bot' + TOKEN + '/getMe', timeout=8)
    print('alive' if r.json().get('ok') else 'dead')
except:
    print('dead')
" 2>/dev/null
}

BOT_STATUS=$(check_bot)

if [ "$BOT_STATUS" != "alive" ]; then
    echo "$(date): Bot is dead! Restarting..."
    
    # Kill any existing processes
    pkill -9 -f "collbomber_bot.py" 2>/dev/null
    pkill -9 -f "supervisord" 2>/dev/null
    sleep 2
    
    # Start fresh
    nohup supervisord -c supervisord.conf > /dev/null 2>&1 &
    sleep 5
    
    # Verify
    BOT_STATUS=$(check_bot)
    if [ "$BOT_STATUS" = "alive" ]; then
        echo "$(date): ✅ Bot restarted successfully!"
    else
        echo "$(date): ⚠️ Starting directly..."
        nohup python3 -u /root/workspace/collbomber_bot.py > /dev/null 2>&1 &
        echo "$(date): ✅ Direct start done"
    fi
fi
