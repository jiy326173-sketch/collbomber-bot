#!/usr/bin/env python3
"""
🔥 CollBomber Render Entry Point
Combined Telegram Bot + Flask Health Server
— No sleep, 24/7 uptime, auto-restart on failure
"""
import os
import sys
import threading
import time

# ============================================================
# Bot Token — env var first, then config_token.py fallback
# ============================================================
if not os.environ.get("BOT_TOKEN"):
    try:
        from config_token import TOKEN
        os.environ["BOT_TOKEN"] = TOKEN
    except ImportError:
        print("❌ ERROR: BOT_TOKEN env variable not set!")
        print("   Set it in Render dashboard → Environment Variables")
        sys.exit(1)

# Import main bot — this registers all handlers, creates bot object
from collbomber_bot import bot, bomber, admin_db, ALL_APIS, CALL_APIS, SMS_APIS, WHATSAPP_APIS

# ============================================================
# Flask Health Server — keeps Render awake, no sleep mode
# ============================================================
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

bot_healthy = False
bot_start_time = None
bot_restart_count = 0

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "service": "🔥 CollBomber Telegram Bot",
        "bot_healthy": bot_healthy,
        "uptime": str(time.time() - bot_start_time).split('.')[0] if bot_start_time else "0s",
        "restarts": bot_restart_count,
        "apis": {
            "total": len(ALL_APIS),
            "call": len(CALL_APIS),
            "sms": len(SMS_APIS),
            "whatsapp": len(WHATSAPP_APIS)
        }
    })

@app.route('/health')
def health():
    if bot_healthy:
        return jsonify({"status": "ok", "bot": "alive"})
    return jsonify({"status": "degraded", "bot": "starting"}), 503

@app.route('/api/ping')
def ping():
    return jsonify({"pong": True, "time": time.time()})

# ============================================================
# Bot Worker Thread — auto-restart on crash
# ============================================================
def run_bot():
    global bot_healthy, bot_start_time, bot_restart_count
    while True:
        try:
            bot_start_time = time.time()
            bot_healthy = True
            print(f"🤖 Bot polling started! 📊 {len(ALL_APIS)} APIs")
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            bot_healthy = False
            bot_restart_count += 1
            print(f"⚠️ Bot error #{bot_restart_count}: {e}")
            print(f"🔄 Restarting in 5s...")
            time.sleep(5)

# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    # Start bot in background
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    time.sleep(3)  # Let bot initialize

    # Flask health server on Render's $PORT
    port = int(os.environ.get('PORT', 8080))
    print(f"🚀 Health server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
