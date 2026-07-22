# AI Rotator — Setup Guide

## Kya hai ye?

System jo **7 free AI providers** pe kaam karta hai — agar ek ka limit/quota khatam ho jaye, **automatically next provider pe shift** ho jata hai. User ko pata bhi nahi chalta.

## Providers (sab FREE hain)

| Provider | Free RPM | Sign up |
|----------|----------|---------|
| Groq | 30 | https://console.groq.com |
| Gemini | 15 | https://aistudio.google.com/apikey |
| OpenRouter | 20 | https://openrouter.ai |
| Cohere | 20 | https://dashboard.cohere.com |
| Mistral | 5 | https://console.mistral.ai |
| Together AI | 60 | https://api.together.xyz |
| HuggingFace | 10 | https://huggingface.co/settings/tokens |

## Quick start (3 steps)

### 1. API keys daalo

```bash
nano /root/workspace/.env.ai
```

File already template ban chuki hai. Apne keys paste karo:

```
GROQ_API_KEY=gsk_xxxxx
GEMINI_API_KEY=AIzaSy...
OPENROUTER_API_KEY=sk-or-...
# jo chahiye utne bhar do, 1 bhi kaafi
```

### 2. Test karo (terminal se)

```bash
cd /root/workspace
python3 ai_rotator.py
```

Agar keys sahi hain to dikhega: `✓ groq • llama-3.1-8b-instant — Response: ROTATOR_OK`

### 3. Telegram bot chalao (optional)

Bot banana: Telegram pe @BotFather → `/newbot` → token lo

```bash
echo "TELEGRAM_BOT_TOKEN=123456:ABC..." >> /root/workspace/.env.ai
python3 /root/workspace/telegram_ai_bot.py
```

## Bot commands (Telegram pe)

- `/start` — intro
- `/status` — your session
- `/providers` — sab providers ka live status (buttons)
- `/priority` — order change karo (e.g. `/priority set groq,gemini`)
- `/reset` — chat history clear

## Programmatic use (apne code mein)

```python
import asyncio
from ai_rotator import AIRotator

async def main():
    rotator = AIRotator()
    result = await rotator.chat([
        {"role": "system", "content": "Tu Hinglish mein reply karta hai."},
        {"role": "user", "content": "Bhai 2+2 kya hai?"},
    ])
    print(result["provider"], "->", result["text"])
    await rotator.close()

asyncio.run(main())
```

## Priority change (kaunsa pehle try ho)

Default order: `groq, gemini, openrouter, cohere, mistral, together, huggingface`

Code se:
```python
rotator.reorder(["gemini", "groq", "openrouter"])
```

Ya Telegram pe: `/priority set gemini,groq,openrouter`

## Error handling (automatic)

| Error | Cooldown |
|-------|----------|
| 429 rate limit | 90s |
| 503 unavailable | 30s |
| 500/502/504 | 15s |
| 401/403 (auth) | 1 hour + permanently disabled |
| timeout | 20s |

## Files

- `ai_rotator.py` — core engine (provider + state)
- `telegram_ai_bot.py` — Telegram wrapper
- `.env.ai` — API keys (auto-loaded)
- `ai_state.json` — runtime state (auto-managed, restart-safe)
- `telegram_users.json` — per-user chat history (auto-managed)

## Venv setup (first time only)

```bash
cd /root/workspace
python3 -m venv .venv
source .venv/bin/activate
pip install python-telegram-bot==20.7 aiohttp
```

Bina venv ke: `pip install --break-system-packages python-telegram-bot==20.7 aiohttp`
