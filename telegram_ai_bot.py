"""
Telegram Bot powered by AI Rotator.
- Har user ke liye independent chat history
- Auto provider fallback (Groq → Gemini → OpenRouter → Cohere → Mistral → Together → HF)
- /status, /providers, /reset, /priority commands
- Per-user rate limiting
"""

import os
import json
import asyncio
import logging
import time
from pathlib import Path
from typing import Dict, List
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass, field

from ai_rotator import (
    AIRotator,
    PROVIDERS,
    StateManager,
)

# Telegram lib — install: pip install python-telegram-bot==20.7 (in venv)
try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (
        Application,
        CommandHandler,
        MessageHandler,
        CallbackQueryHandler,
        ContextTypes,
        filters,
    )
    from telegram.constants import ParseMode, ChatAction
except ImportError:
    print("Install: pip install python-telegram-bot==20.7")
    raise

# ============================================================
# CONFIG
# ============================================================

USERS_FILE = Path("/root/workspace/telegram_users.json")
DEFAULT_HISTORY_LIMIT = 20  # messages kept per user
RATE_LIMIT_PER_MIN = 30  # per user

# Load /root/workspace/.env.ai if present (auto-load user API keys)
_ENV_FILE = Path("/root/workspace/.env.ai")
if _ENV_FILE.exists():
    for _line in _ENV_FILE.read_text().splitlines():
        _line = _line.strip()
        if not _line or _line.startswith("#") or "=" not in _line:
            continue
        _k, _v = _line.split("=", 1)
        _k, _v = _k.strip(), _v.strip().strip('"').strip("'")
        if _k and _v:
            os.environ.setdefault(_k, _v)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
log = logging.getLogger("ai-bot")


# ============================================================
# USER SESSION
# ============================================================

@dataclass
class UserSession:
    user_id: int
    history: List[dict] = field(default_factory=list)
    last_seen: float = 0.0
    request_count: int = 0
    window_start: float = 0.0
    preferred_priority: List[str] = field(default_factory=list)


class SessionManager:
    def __init__(self, path: Path = USERS_FILE):
        self.path = path
        self.sessions: Dict[int, UserSession] = {}
        self.load()

    def load(self):
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text())
                for uid_str, s in data.items():
                    self.sessions[int(uid_str)] = UserSession(**s)
            except Exception as e:
                log.warning(f"session load failed: {e}")

    def save(self):
        try:
            data = {
                str(uid): {
                    "user_id": s.user_id,
                    "history": s.history[-DEFAULT_HISTORY_LIMIT * 2:],
                    "last_seen": s.last_seen,
                    "request_count": s.request_count,
                    "window_start": s.window_start,
                    "preferred_priority": s.preferred_priority,
                }
                for uid, s in self.sessions.items()
            }
            self.path.write_text(json.dumps(data, indent=2))
        except Exception as e:
            log.warning(f"session save failed: {e}")

    def get(self, user_id: int) -> UserSession:
        if user_id not in self.sessions:
            self.sessions[user_id] = UserSession(user_id=user_id)
        return self.sessions[user_id]

    def allow_request(self, user_id: int) -> bool:
        """Per-user rate limiter"""
        s = self.get(user_id)
        now = time.time()
        if now - s.window_start > 60:
            s.window_start = now
            s.request_count = 0
        if s.request_count >= RATE_LIMIT_PER_MIN:
            return False
        s.request_count += 1
        return True


# ============================================================
# BOT
# ============================================================

class AIBot:
    def __init__(self, token: str):
        self.token = token
        self.rotator = AIRotator()
        self.sessions = SessionManager()
        self.app = Application.builder().token(token).build()
        self._register_handlers()

    def _register_handlers(self):
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("help", self.cmd_help))
        self.app.add_handler(CommandHandler("status", self.cmd_status))
        self.app.add_handler(CommandHandler("providers", self.cmd_providers))
        self.app.add_handler(CommandHandler("priority", self.cmd_priority))
        self.app.add_handler(CommandHandler("reset", self.cmd_reset))
        self.app.add_handler(CommandHandler("clear", self.cmd_reset))
        self.app.add_handler(CallbackQueryHandler(self.on_callback))
        self.app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.on_message)
        )

    # ----- commands -----

    async def cmd_start(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🤖 **AI Rotator Bot** ready.\n\n"
            "Mujhe kuch bhi pucho — main 7 free providers pe auto-fallback kar sakta hoon.\n\n"
            "Commands:\n"
            "/status — current provider + tokens\n"
            "/providers — all providers status\n"
            "/priority — change provider order\n"
            "/reset — clear chat history\n"
            "/help — ye message",
            parse_mode=ParseMode.MARKDOWN,
        )

    async def cmd_help(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self.cmd_start(update, ctx)

    async def cmd_status(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        s = self.sessions.get(update.effective_user.id)
        msg = (
            f"📊 **Your Session**\n"
            f"Messages in history: {len(s.history)}\n"
            f"Requests this minute: {s.request_count}/{RATE_LIMIT_PER_MIN}\n"
        )
        await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

    async def cmd_providers(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        kb = []
        for pid, st in self.rotator.list_status().items():
            flag = "✅" if st["available"] else "❌"
            cd = f" ({st['cooldown_seconds']}s)" if st["cooldown_seconds"] else ""
            kb.append([
                InlineKeyboardButton(
                    f"{flag} {st['name']}{cd}",
                    callback_data=f"info:{pid}",
                )
            ])
        await update.message.reply_text(
            "**Provider Status** (tap for details):",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(kb),
        )

    async def cmd_priority(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        s = self.sessions.get(update.effective_user.id)
        priority = s.preferred_priority or self.rotator.priority
        text = "**Current Priority Order:**\n\n"
        for i, pid in enumerate(priority, 1):
            text += f"{i}. {PROVIDERS[pid]['name']}\n"
        text += "\nChange order: /priority set groq,gemini,openrouter"
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

    async def cmd_reset(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        s = self.sessions.get(update.effective_user.id)
        s.history.clear()
        self.sessions.save()
        await update.message.reply_text("🧹 Chat history cleared.")

    # ----- callbacks -----

    async def on_callback(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        await q.answer()
        if q.data.startswith("info:"):
            pid = q.data.split(":", 1)[1]
            st = self.rotator.list_status().get(pid, {})
            text = (
                f"**{st.get('name', pid)}**\n"
                f"API key set: {st.get('has_api_key')}\n"
                f"Available: {st.get('available')}\n"
                f"Cooldown: {st.get('cooldown_seconds', 0)}s\n"
                f"Total calls: {st.get('total_calls', 0)}\n"
                f"Failed calls: {st.get('failed_calls', 0)}\n"
                f"Last error: `{st.get('last_error') or 'none'}`"
            )
            await q.edit_message_text(text, parse_mode=ParseMode.MARKDOWN)

    # ----- main message handler -----

    async def on_message(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        text = update.message.text.strip()
        if not text:
            return

        # rate limit
        if not self.sessions.allow_request(user.id):
            await update.message.reply_text(
                f"⏳ Rate limit: {RATE_LIMIT_PER_MIN} req/min. Thoda ruko."
            )
            return

        session = self.sessions.get(user.id)
        session.history.append({"role": "user", "content": text})
        # trim
        if len(session.history) > DEFAULT_HISTORY_LIMIT * 2:
            session.history = session.history[-DEFAULT_HISTORY_LIMIT:]

        # typing indicator
        await ctx.bot.send_chat_action(update.effective_chat.id, ChatAction.TYPING)

        # call rotator
        result = await self.rotator.chat(session.history)

        if not result["text"]:
            err = result.get("error", "unknown")
            attempts = ", ".join(
                a["provider"] for a in result.get("attempts", [])
            )
            await update.message.reply_text(
                f"❌ All providers failed.\n"
                f"Tried: {attempts}\n"
                f"Error: {err[:200]}\n\n"
                f"Set API keys in `.env.ai` ya owner se bolo."
            )
            return

        # store reply
        session.history.append({"role": "assistant", "content": result["text"]})
        self.sessions.save()

        # send
        header = f"_{result['provider']} • {result['model']}_"
        reply_text = f"{header}\n\n{result['text']}"
        if len(reply_text) > 4000:
            reply_text = reply_text[:4000] + "\n\n[truncated]"

        await update.message.reply_text(
            reply_text, parse_mode=ParseMode.MARKDOWN
        )

    # ----- run -----

    def run(self):
        log.info("Starting bot...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("Set TELEGRAM_BOT_TOKEN env var first.")
        print("Get one from @BotFather on Telegram.")
        raise SystemExit(1)
    AIBot(BOT_TOKEN).run()
