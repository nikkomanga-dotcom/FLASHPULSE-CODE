"""News enrichment helpers (pure functions, no I/O) — used by the refresh pipeline in server.py."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Optional

REGIONS = ["USA", "Europa", "Eurozona", "Asia", "Cina", "Medio Oriente", "Globale"]
CATEGORIES = ["macro", "markets", "energy", "geopolitics"]

_CATEGORY_KEYWORDS = {
    "energy": ["oil", "opec", "gas", "petrol", "energy", "crude", "lng", "greggio", "energia"],
    "geopolitics": ["war", "sanction", "military", "nato", "ukraine", "russia", "china", "taiwan", "iran", "israel", "gaza", "missile", "guerra", "sanzioni", "dazi", "tariff", "election", "elezioni"],
    "macro": ["fed", "ecb", "bce", "inflation", "inflazione", "interest rate", "tassi", "gdp", "pil", "jobs", "unemployment", "cpi", "recession", "central bank"],
}

# whole-word match (optional plural "s"), so "war" does not fire on "software" nor "gas" on "Vegas"
_CATEGORY_RE = {cat: re.compile(r"\b(?:" + "|".join(re.escape(k) for k in kws) + r")s?\b") for cat, kws in _CATEGORY_KEYWORDS.items()}

SYSTEM_PROMPT = "Sei un analista finanziario che scrive per il grande pubblico. Rispondi sempre e solo con JSON valido, in italiano semplice."


def item_id(raw: dict) -> str:
    key = (raw.get("url") or raw.get("title") or "").split("?")[0]
    return "live-" + hashlib.md5(key.encode()).hexdigest()[:16]


def guess_category(text: str) -> str:
    t = (text or "").lower()
    for cat in ("energy", "geopolitics", "macro"):
        if _CATEGORY_RE[cat].search(t):
            return cat
    return "markets"


def build_prompt(raw: dict) -> str:
    return (
        "Analizza questa notizia e genera un oggetto JSON con ESATTAMENTE questi campi:\n"
        '{"title_it": "titolo italiano chiaro, max 110 caratteri",'
        ' "bullets": ["3 punti brevi e comprensibili a chi non è esperto"],'
        ' "impact": "intero 1-10 (1-3 rumore, 4-6 rilevante, 7-8 importante per i mercati, 9-10 evento eccezionale)",'
        ' "tags": ["#Tag1", "#Tag2", "#Tag3"],'
        ' "domino": "catena causa-effetto in una riga con frecce →",'
        f' "category": "uno tra {"|".join(CATEGORIES)}",'
        ' "ticker": "simbolo azionario principale oppure null",'
        f' "region": "uno tra {"|".join(REGIONS)}",'
        ' "analysis": "2 frasi semplici: cosa è successo e perché conta",'
        ' "bull": "scenario positivo in 1 frase", "bear": "scenario negativo in 1 frase",'
        ' "history_title": "precedente storico pertinente", "history_body": "parallelo storico in 2 frasi"}\n\n'
        "Regole: usa solo fatti presenti nella notizia, non inventare cifre; se un dato manca, resta qualitativo.\n\n"
        f"NOTIZIA ({raw.get('source', '')}): {raw.get('title', '')} — {raw.get('summary', '')}\n\n"
        "Rispondi SOLO con il JSON."
    )


def parse_llm_json(text: Optional[str]) -> Optional[dict]:
    if not text:
        return None
    text = text.strip()
    m = re.search(r"\{.*\}", text, flags=re.S)
    if not m:
        return None
    try:
        data = json.loads(m.group(0))
        return data if isinstance(data, dict) else None
    except ValueError:
        return None


def _clean_tags(tags) -> list[str]:
    out = []
    for t in tags or []:
        t = str(t).strip().lstrip("#").replace(" ", "")
        if t:
            out.append("#" + t)
    return out[:4]


def _clamp_impact(v) -> int:
    try:
        return max(1, min(10, int(round(float(v)))))
    except (TypeError, ValueError):
        return 5


def build_item(raw: dict, data: dict) -> dict:
    ticker = data.get("ticker")
    if not ticker or str(ticker).lower() in ("null", "none", "n/a", ""):
        ticker = None
    category = data.get("category") if data.get("category") in CATEGORIES else guess_category(raw.get("title", ""))
    region = data.get("region") if data.get("region") in REGIONS else "Globale"
    return {
        "id": item_id(raw),
        "title": data.get("title_it") or raw.get("title"),
        "bullets": [str(b) for b in (data.get("bullets") or [])][:3] or [raw.get("summary", "")[:160]],
        "impact": _clamp_impact(data.get("impact")),
        "tags": _clean_tags(data.get("tags")),
        "domino": data.get("domino") or "",
        "sources": [raw.get("source")],
        "ticker": str(ticker).upper() if ticker else None,
        "region": region,
        "category": category,
        "published_at": raw.get("published_at"),
        "url": raw.get("url"),
        "deep_dive": {
            "analysis": data.get("analysis") or raw.get("summary", ""),
            "bull": data.get("bull") or "",
            "bear": data.get("bear") or "",
            "history": {"title": data.get("history_title") or "", "body": data.get("history_body") or ""},
        },
        "enriched": True,
        "enriched_at": datetime.now(timezone.utc).isoformat(),
    }


def heuristic_item(raw: dict) -> dict:
    """Basic card when no AI is available: honest, minimal, never fabricates analysis."""
    summary = (raw.get("summary") or "").strip()
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", summary) if len(s.strip()) > 20][:3]
    category = guess_category(raw.get("title", "") + " " + summary)
    return {
        "id": item_id(raw),
        "title": raw.get("title"),
        "bullets": sentences or ["Apri l'articolo originale per i dettagli."],
        "impact": 4,
        "tags": ["#" + category.capitalize()],
        "domino": "",
        "sources": [raw.get("source")],
        "ticker": None,
        "region": "Globale",
        "category": category,
        "published_at": raw.get("published_at"),
        "url": raw.get("url"),
        "deep_dive": {"analysis": summary, "bull": "", "bear": "", "history": {"title": "", "body": ""}},
        "enriched": False,
        "enriched_at": datetime.now(timezone.utc).isoformat(),
    }


def select_for_enrichment(raw_items: list[dict], existing_ids: set[str], limit: int) -> list[dict]:
    """Newest-first, skipping items already stored (saves LLM quota)."""
    fresh = [r for r in raw_items if item_id(r) not in existing_ids]
    fresh.sort(key=lambda r: r.get("published_at") or "", reverse=True)
    return fresh[:limit]
