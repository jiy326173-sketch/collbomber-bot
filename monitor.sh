#!/bin/bash
# 🔥 Ultimate Monitor — keeps cron AND bot running 24/7
# Runs in background, checks every 60 seconds
# No dependencies on cron daemon

BOT_DIR="/root/workspace"
PID_FILE="/tmp/collbomber_bot.pid"
LOG_FILE="$BOT_DIR/monitor.log"

cd "$BOT_DIR" || exit 1

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

ensure_cron() {
    pgrep -a cron >/dev/null 2>&1 || {
        log "⚠️ Cron dead. Restarting..."
        service cron start 2>/dev/null
        sleep 2
        pgrep -a cron >/dev/null 2>&1 && log "✅ Cron restarted" || log "❌ Cron failed to start"
    }
}

ensure_bot() {
    # Check by PID file
    if [ -f "$PID_FILE" ]; then
        pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            # Process exists, verify via Telegram API
            local token
            token=$(python3 -c "exec(open('config_token.py').read()); print(TOKEN)" 2>/dev/null)
            if [ -n "$token" ]; then
                local alive
                alive=$(curl -s --connect-timeout 5 --max-time 8 \
                    "https://api.telegram.org/bot${token}/getMe" 2>/dev/null | \
                    python3 -c "import sys,json; d=json.load(sys.stdin); print('ok' if d.get('ok') else 'no')" 2>/dev/null)
                if [ "$alive" = "ok" ]; then
                    return 0  # Bot is alive
                fi
            fi
            # Process exists but unresponsive - kill it
            log "⚠️ Bot process $pid exists but unresponsive. Killing..."
            kill -9 "$pid" 2>/dev/null
            rm -f "$PID_FILE"
        else
            log "⚠️ PID file stale. Removing..."
            rm -f "$PID_FILE"
        fi
    fi
    
    # Start bot
    log "🔄 Starting bot..."
    pkill -9 -f "collbomber_bot.py" 2>/dev/null
    sleep 2
    nohup python3 -u "$BOT_DIR/collbomber_bot.py" >> "$BOT_DIR/bot_output.log" 2>> "$BOT_DIR/bot_error.log" &
    local pid=$!
    echo $pid > "$PID_FILE"
    sleep 8
    log "✅ Bot started! PID: $pid"
    
    # Verify
    local token
    token=$(python3 -c "exec(open('config_token.py').read()); print(TOKEN)" 2>/dev/null)
    if [ -n "$token" ]; then
        local alive
        alive=$(curl -s --connect-timeout 5 --max-time 8 \
            "https://api.telegram.org/bot${token}/getMe" 2>/dev/null | \
            python3 -c "import sys,json; d=json.load(sys.stdin); print('ok' if d.get('ok') else 'no')" 2>/dev/null)
        [ "$alive" = "ok" ] && log "✅ Bot verified online" || log "⚠️ Bot may not be online yet"
    fi
}

# Also clean log files >10MB
clean_logs() {
    for f in "$BOT_DIR/bot_output.log" "$BOT_DIR/bot_error.log" "$LOG_FILE"; do
        if [ -f "$f" ] && [ "$(stat -c%s "$f" 2>/dev/null)" -gt 10485760 ]; then
            tail -2000 "$f" > "${f}.tmp" && mv "${f}.tmp" "$f"
            log "📋 Trimmed $f"
        fi
    done
}

# Main loop
log "🚀 Ultimate Monitor started"
while true; do
    ensure_cron
    ensure_bot
    clean_logs
    sleep 60
done