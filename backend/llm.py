"""Thin LLM layer. Two interchangeable backends:

  1. Emergent universal key (EMERGENT_LLM_KEY) via `emergentintegrations` — as in the original app.
  2. Google Gemini API directly (GEMINI_API_KEY) — free tier, works anywhere, no extra package.

The first configured backend wins. If none is configured `available()` is False and callers
fall back to non-AI behaviour instead of failing.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import AsyncIterator, Optional

import requests

log = logging.getLogger("flashpulse.llm")

EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
EMERGENT_MODEL = os.environ.get("EMERGENT_MODEL", "gemini-3-flash-preview")

_GEN_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:{method}"


def backend() -> Optional[str]:
    if EMERGENT_LLM_KEY:
        return "emergent"
    if GEMINI_API_KEY:
        return "gemini"
    return None


def available() -> bool:
    return backend() is not None


def _payload(system: str, prompt: str, json_mode: bool) -> dict:
    body = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
    }
    if json_mode:
        body["generationConfig"] = {"responseMimeType": "application/json"}
    return body


def _extract_text(data: dict) -> str:
    parts = (((data.get("candidates") or [{}])[0].get("content") or {}).get("parts")) or []
    return "".join(p.get("text", "") for p in parts)


def _gemini_complete_sync(system: str, prompt: str, json_mode: bool) -> str:
    r = requests.post(
        _GEN_URL.format(model=GEMINI_MODEL, method="generateContent"),
        params={"key": GEMINI_API_KEY},
        json=_payload(system, prompt, json_mode),
        timeout=60,
    )
    r.raise_for_status()
    return _extract_text(r.json())


async def complete(system: str, prompt: str, session_id: str = "one-shot", json_mode: bool = False) -> Optional[str]:
    """Single-shot completion. Returns None if no backend is configured or the call fails."""
    b = backend()
    try:
        if b == "emergent":
            from emergentintegrations.llm.chat import LlmChat, UserMessage

            chat = LlmChat(api_key=EMERGENT_LLM_KEY, session_id=session_id, system_message=system).with_model("gemini", EMERGENT_MODEL)
            resp = await chat.send_message(UserMessage(text=prompt))
            return resp if isinstance(resp, str) else getattr(resp, "content", str(resp))
        if b == "gemini":
            return await asyncio.to_thread(_gemini_complete_sync, system, prompt, json_mode)
    except Exception as exc:
        log.warning("llm.complete failed (%s): %s", b, exc)
    return None


async def stream(system: str, prompt: str, session_id: str = "stream") -> AsyncIterator[str]:
    """Yield text chunks. Raises on error so the caller can report it to the user."""
    b = backend()
    if b == "emergent":
        from emergentintegrations.llm.chat import LlmChat, UserMessage, TextDelta, StreamDone

        chat = LlmChat(api_key=EMERGENT_LLM_KEY, session_id=session_id, system_message=system).with_model("gemini", EMERGENT_MODEL)
        async for ev in chat.stream_message(UserMessage(text=prompt)):
            if isinstance(ev, TextDelta):
                yield ev.content
            elif isinstance(ev, StreamDone):
                break
    elif b == "gemini":
        import aiohttp

        url = _GEN_URL.format(model=GEMINI_MODEL, method="streamGenerateContent")
        async with aiohttp.ClientSession() as s:
            async with s.post(url, params={"alt": "sse", "key": GEMINI_API_KEY}, json=_payload(system, prompt, False), timeout=aiohttp.ClientTimeout(total=120)) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"Gemini HTTP {resp.status}")
                buf = ""
                async for chunk in resp.content.iter_any():
                    buf += chunk.decode("utf-8", errors="ignore")
                    while "\n" in buf:
                        line, buf = buf.split("\n", 1)
                        line = line.strip()
                        if not line.startswith("data:"):
                            continue
                        try:
                            text = _extract_text(json.loads(line[5:].strip()))
                        except ValueError:
                            continue
                        if text:
                            yield text
    else:
        raise RuntimeError("Nessun servizio AI configurato (imposta GEMINI_API_KEY o EMERGENT_LLM_KEY)")
