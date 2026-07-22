"""
AI Provider Auto-Rotator
Ek ka limit khatam ho jaye to next free provider pe shift ho jaye.
Supports: Groq, Gemini, OpenRouter, Cohere, Mistral, Together, HuggingFace
"""

import os
import json
import time
import asyncio
import aiohttp
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

# ============================================================
# CONFIG
# ============================================================

CONFIG_FILE = Path("/root/workspace/ai_config.json")
STATE_FILE = Path("/root/workspace/ai_state.json")

# Free providers (no payment required, just API keys)
PROVIDERS = {
    "groq": {
        "name": "Groq",
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "models": ["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "mixtral-8x7b-32768"],
        "rpm": 30,
        "tpm": 6000,
        "key_env": "GROQ_API_KEY",
        "format": "openai",
        "headers_extra": {},
    },
    "gemini": {
        "name": "Google Gemini",
        "url": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        "models": ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
        "rpm": 15,
        "tpm": 1000000,
        "key_env": "GEMINI_API_KEY",
        "format": "gemini",
        "headers_extra": {},
    },
    "openrouter": {
        "name": "OpenRouter (Free Models)",
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "models": ["meta-llama/llama-3.3-70b-instruct:free", "google/gemini-2.0-flash-exp:free", "qwen/qwen-2.5-72b-instruct:free"],
        "rpm": 20,
        "tpm": 100000,
        "key_env": "OPENROUTER_API_KEY",
        "format": "openai",
        "headers_extra": {"HTTP-Referer": "https://localhost", "X-Title": "ai-rotator"},
    },
    "cohere": {
        "name": "Cohere",
        "url": "https://api.cohere.ai/v1/chat",
        "models": ["command-r-plus", "command-r", "command-light"],
        "rpm": 20,
        "tpm": 100000,
        "key_env": "COHERE_API_KEY",
        "format": "cohere",
        "headers_extra": {},
    },
    "mistral": {
        "name": "Mistral",
        "url": "https://api.mistral.ai/v1/chat/completions",
        "models": ["mistral-large-latest", "mistral-small-latest", "open-mistral-7b"],
        "rpm": 5,
        "tpm": 1000000,
        "key_env": "MISTRAL_API_KEY",
        "format": "openai",
        "headers_extra": {},
    },
    "together": {
        "name": "Together AI",
        "url": "https://api.together.xyz/v1/chat/completions",
        "models": ["meta-llama/Llama-3.3-70B-Instruct-Turbo", "Qwen/Qwen2.5-72B-Instruct-Turbo"],
        "rpm": 60,
        "tpm": 100000,
        "key_env": "TOGETHER_API_KEY",
        "format": "openai",
        "headers_extra": {},
    },
    "huggingface": {
        "name": "HuggingFace Inference",
        "url": "https://api-inference.huggingface.co/models/{model}",
        "models": ["meta-llama/Llama-3.2-3B-Instruct", "microsoft/Phi-3-mini-4k-instruct"],
        "rpm": 10,
        "tpm": 50000,
        "key_env": "HUGGINGFACE_API_KEY",
        "format": "huggingface",
        "headers_extra": {},
    },
}


# ============================================================
# STATE MANAGER
# ============================================================

@dataclass
class ProviderState:
    """Per-provider runtime state"""
    available: bool = True
    cooldown_until: Optional[float] = None  # epoch seconds
    last_error: Optional[str] = None
    total_calls: int = 0
    failed_calls: int = 0
    current_model: Optional[str] = None
    tokens_used: int = 0


class StateManager:
    """Persist provider state to disk so limits survive restarts"""

    def __init__(self, path: Path = STATE_FILE):
        self.path = path
        self.states: Dict[str, ProviderState] = {
            pid: ProviderState() for pid in PROVIDERS
        }
        self.load()

    def load(self):
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text())
                for pid, sd in data.items():
                    if pid in self.states:
                        self.states[pid] = ProviderState(**sd)
            except Exception as e:
                print(f"[StateManager] load failed: {e}")

    def save(self):
        try:
            data = {
                pid: {
                    "available": s.available,
                    "cooldown_until": s.cooldown_until,
                    "last_error": s.last_error,
                    "total_calls": s.total_calls,
                    "failed_calls": s.failed_calls,
                    "current_model": s.current_model,
                    "tokens_used": s.tokens_used,
                }
                for pid, s in self.states.items()
            }
            self.path.write_text(json.dumps(data, indent=2))
        except Exception as e:
            print(f"[StateManager] save failed: {e}")

    def is_available(self, pid: str) -> bool:
        s = self.states[pid]
        if not s.available:
            return False
        if s.cooldown_until and time.time() < s.cooldown_until:
            return False
        return True

    def mark_failed(self, pid: str, error: str, cooldown_seconds: int = 60):
        s = self.states[pid]
        s.last_error = error
        s.failed_calls += 1
        s.cooldown_until = time.time() + cooldown_seconds
        if "401" in error or "invalid" in error.lower():
            s.available = False  # hard disable on auth error
        self.save()

    def mark_success(self, pid: str, tokens: int = 0):
        s = self.states[pid]
        s.total_calls += 1
        s.tokens_used += tokens
        s.cooldown_until = None
        s.last_error = None
        self.save()


# ============================================================
# PROVIDER CALLERS
# ============================================================

async def call_openai_format(
    session: aiohttp.ClientSession,
    provider_id: str,
    cfg: dict,
    api_key: str,
    model: str,
    messages: List[dict],
    **kwargs,
) -> str:
    """OpenAI-compatible providers (Groq, OpenRouter, Mistral, Together)"""
    url = cfg["url"]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        **cfg["headers_extra"],
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": kwargs.get("temperature", 0.7),
        "max_tokens": kwargs.get("max_tokens", 1024),
    }
    if "stream" in kwargs:
        payload["stream"] = kwargs["stream"]

    async with session.post(url, json=payload, headers=headers, timeout=60) as resp:
        if resp.status != 200:
            body = await resp.text()
            raise Exception(f"HTTP {resp.status}: {body[:300]}")
        data = await resp.json()
        return data["choices"][0]["message"]["content"]


async def call_gemini_format(
    session: aiohttp.ClientSession,
    provider_id: str,
    cfg: dict,
    api_key: str,
    model: str,
    messages: List[dict],
    **kwargs,
) -> str:
    """Google Gemini API"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}

    # Convert messages to Gemini format
    contents = []
    system_instruction = None
    for msg in messages:
        if msg["role"] == "system":
            system_instruction = msg["content"]
        else:
            contents.append({
                "role": "user" if msg["role"] == "user" else "model",
                "parts": [{"text": msg["content"]}],
            })

    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": kwargs.get("temperature", 0.7),
            "maxOutputTokens": kwargs.get("max_tokens", 1024),
        },
    }
    if system_instruction:
        payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

    async with session.post(url, json=payload, headers=headers, timeout=60) as resp:
        if resp.status != 200:
            body = await resp.text()
            raise Exception(f"HTTP {resp.status}: {body[:300]}")
        data = await resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]


async def call_cohere_format(
    session: aiohttp.ClientSession,
    provider_id: str,
    cfg: dict,
    api_key: str,
    model: str,
    messages: List[dict],
    **kwargs,
) -> str:
    """Cohere API"""
    url = cfg["url"]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Cohere v1 chat needs separate message + chat_history
    user_msg = ""
    chat_history = []
    for m in messages:
        if m["role"] == "user":
            user_msg = m["content"]
        elif m["role"] == "assistant":
            chat_history.append({"role": "CHATBOT", "message": m["content"]})
        elif m["role"] == "system":
            chat_history.append({"role": "SYSTEM", "message": m["content"]})

    payload = {
        "model": model,
        "message": user_msg,
        "temperature": kwargs.get("temperature", 0.7),
        "max_tokens": kwargs.get("max_tokens", 1024),
    }
    if chat_history:
        payload["chat_history"] = chat_history

    async with session.post(url, json=payload, headers=headers, timeout=60) as resp:
        if resp.status != 200:
            body = await resp.text()
            raise Exception(f"HTTP {resp.status}: {body[:300]}")
        data = await resp.json()
        return data["text"]


async def call_huggingface_format(
    session: aiohttp.ClientSession,
    provider_id: str,
    cfg: dict,
    api_key: str,
    model: str,
    messages: List[dict],
    **kwargs,
) -> str:
    """HuggingFace Inference API (chat-compatible models)"""
    url = f"https://api-inference.huggingface.co/models/{model}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": kwargs.get("max_tokens", 1024),
        "temperature": kwargs.get("temperature", 0.7),
    }
    async with session.post(url, json=payload, headers=headers, timeout=60) as resp:
        if resp.status != 200:
            body = await resp.text()
            raise Exception(f"HTTP {resp.status}: {body[:300]}")
        data = await resp.json()
        return data["choices"][0]["message"]["content"]


FORMAT_DISPATCH = {
    "openai": call_openai_format,
    "gemini": call_gemini_format,
    "cohere": call_cohere_format,
    "huggingface": call_huggingface_format,
}


# ============================================================
# ROTATOR (the brain)
# ============================================================

class AIRotator:
    """
    Tries providers in priority order. If one fails (rate limit, quota, network, auth),
    it gets put in cooldown and the next available provider is used automatically.
    """

    def __init__(
        self,
        priority: Optional[List[str]] = None,
        config_file: Path = CONFIG_FILE,
    ):
        self.config_file = config_file
        self.state = StateManager()
        self.priority = priority or self._load_priority()
        self.session: Optional[aiohttp.ClientSession] = None

    def _load_priority(self) -> List[str]:
        """Load priority from config or use default"""
        if self.config_file.exists():
            try:
                cfg = json.loads(self.config_file.read_text())
                return cfg.get("priority", list(PROVIDERS.keys()))
            except Exception:
                pass
        return list(PROVIDERS.keys())

    def save_priority(self):
        cfg = {"priority": self.priority}
        self.config_file.write_text(json.dumps(cfg, indent=2))

    def reorder(self, new_priority: List[str]):
        """Change provider priority at runtime"""
        for pid in new_priority:
            if pid not in PROVIDERS:
                raise ValueError(f"Unknown provider: {pid}")
        self.priority = new_priority
        self.save_priority()

    def list_status(self) -> Dict[str, Any]:
        """Return status of all providers"""
        now = time.time()
        out = {}
        for pid, cfg in PROVIDERS.items():
            s = self.state.states[pid]
            has_key = bool(os.getenv(cfg["key_env"]))
            cooldown_left = 0
            if s.cooldown_until and now < s.cooldown_until:
                cooldown_left = int(s.cooldown_until - now)
            out[pid] = {
                "name": cfg["name"],
                "has_api_key": has_key,
                "available": self.state.is_available(pid) if has_key else False,
                "cooldown_seconds": cooldown_left,
                "total_calls": s.total_calls,
                "failed_calls": s.failed_calls,
                "last_error": s.last_error,
                "priority_position": self.priority.index(pid) + 1 if pid in self.priority else None,
            }
        return out

    def _parse_error(self, error_msg: str) -> int:
        """Determine cooldown length from error type"""
        msg = error_msg.lower()
        if "429" in error_msg or "rate" in msg or "quota" in msg:
            return 90
        if "503" in error_msg or "unavailable" in msg or "overload" in msg:
            return 30
        if "500" in error_msg or "502" in error_msg or "504" in error_msg:
            return 15
        if "401" in error_msg or "403" in error_msg:
            return 3600  # 1 hour for auth errors
        if "timeout" in msg or "connection" in msg:
            return 20
        return 60  # default

    async def _try_provider(
        self,
        session: aiohttp.ClientSession,
        pid: str,
        messages: List[dict],
        model_override: Optional[str] = None,
        **kwargs,
    ) -> Optional[str]:
        """Try one provider. Returns text on success, None on failure."""
        cfg = PROVIDERS[pid]
        api_key = os.getenv(cfg["key_env"])
        if not api_key:
            return None

        # pick model: override > previously used > first in list
        state = self.state.states[pid]
        model = model_override or state.current_model or cfg["models"][0]
        state.current_model = model

        # dispatch to correct format
        fn = FORMAT_DISPATCH[cfg["format"]]
        try:
            text = await fn(
                session, pid, cfg, api_key, model, messages, **kwargs
            )
            self.state.mark_success(pid)
            return text
        except Exception as e:
            err = str(e)
            cooldown = self._parse_error(err)
            self.state.mark_failed(pid, err, cooldown)
            print(f"[{pid}] FAILED -> cooldown {cooldown}s | {err[:120]}")
            return None

    async def chat(
        self,
        messages: List[dict],
        model_override: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Main entry point. Tries providers in priority order.
        Returns: {"text": str, "provider": str, "model": str, "attempts": int}
        """
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()

        attempts = []
        # try all available providers in priority order
        for pid in self.priority:
            if not self.state.is_available(pid):
                cfg = PROVIDERS[pid]
                if not os.getenv(cfg["key_env"]):
                    attempts.append({"provider": pid, "error": "no_api_key"})
                else:
                    attempts.append({"provider": pid, "error": "in_cooldown"})
                continue

            result = await self._try_provider(
                self.session, pid, messages, model_override, **kwargs
            )
            if result is not None:
                return {
                    "text": result,
                    "provider": pid,
                    "model": self.state.states[pid].current_model,
                    "attempts": attempts + [{"provider": pid, "ok": True}],
                }
            attempts.append({"provider": pid, "error": "request_failed"})

        # All providers failed
        return {
            "text": None,
            "provider": None,
            "model": None,
            "attempts": attempts,
            "error": "All providers failed. Check API keys or wait for cooldown.",
        }

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()


# ============================================================
# CONFIG WIZARD
# ============================================================

def write_env_template():
    """Write a .env template file the user can fill in"""
    template = "# AI Rotator — API keys (at least one required, more = better failover)\n\n"
    for pid, cfg in PROVIDERS.items():
        template += f"# {cfg['name']} — {cfg['rpm']} req/min free\n"
        template += f"{cfg['key_env']}=\n\n"
    Path("/root/workspace/.env.ai").write_text(template)
    print("Template written to /root/workspace/.env.ai")


# ============================================================
# DEMO
# ============================================================

async def demo():
    rotator = AIRotator()
    print("Provider status:")
    for pid, st in rotator.list_status().items():
        flag = "✓" if st["available"] else "✗"
        print(f"  {flag} {st['name']:<25} key={st['has_api_key']} cooldown={st['cooldown_seconds']}s")

    print("\nSending test prompt...")
    result = await rotator.chat([
        {"role": "user", "content": "Reply with exactly: ROTATOR_OK"}
    ])

    if result["text"]:
        print(f"\n✓ {result['provider']} / {result['model']}")
        print(f"  Response: {result['text'][:200]}")
        print(f"  Attempts: {len(result['attempts'])}")
    else:
        print(f"\n✗ FAILED: {result.get('error')}")
        print("  Set at least one API key in /root/workspace/.env.ai")

    await rotator.close()


if __name__ == "__main__":
    write_env_template()
    print()
    asyncio.run(demo())
