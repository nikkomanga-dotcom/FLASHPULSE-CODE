import asyncio
import hmac
import json
import logging
import os
import uuid
from contextlib import asynccontextmanager, suppress
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Literal, Optional

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")  # must run before importing llm (reads env at import time)

from fastapi import APIRouter, BackgroundTasks, FastAPI, Header, HTTPException, Request  # noqa: E402
from fastapi.responses import StreamingResponse  # noqa: E402
from motor.motor_asyncio import AsyncIOMotorClient  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402
from pymongo import ASCENDING, DESCENDING, IndexModel  # noqa: E402
from pywebpush import WebPushException, webpush  # noqa: E402
from starlette.middleware.cors import CORSMiddleware  # noqa: E402

import content  # noqa: E402
import enrich  # noqa: E402
import llm  # noqa: E402
import providers  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log = logging.getLogger("flashpulse")

mongo_url = os.environ["MONGO_URL"]
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ["DB_NAME"]]

WEBHOOK_CRON_SECRET = os.environ.get("WEBHOOK_CRON_SECRET")
FINNHUB_API_KEY = os.environ.get("FINNHUB_API_KEY")
NEWSAPI_API_KEY = os.environ.get("NEWSAPI_API_KEY")
ALPHA_VANTAGE_API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")
VAPID_PRIVATE_KEY = os.environ.get("VAPID_PRIVATE_KEY")
VAPID_PUBLIC_KEY = os.environ.get("VAPID_PUBLIC_KEY")
VAPID_SUBJECT = os.environ.get("VAPID_SUBJECT", "mailto:user@flashpulse.app")

NEWS_REFRESH_EVERY_SEC = 15 * 60  # lazy refresh when the feed is older than this
NEWS_TTL_DAYS = 7
MAX_ENRICH_PER_RUN = 10
QUOTE_TTL = 5 * 60
CHART_TTL = 60 * 60
MACRO_TTL = 6 * 60 * 60
FUNDAMENTALS_TTL = 24 * 60 * 60
FEARGREED_TTL = 30 * 60

INDEXES: dict[str, list[IndexModel]] = {
    "copilot_messages": [IndexModel([("session_id", ASCENDING), ("created_at", ASCENDING)], name="session_created")],
    "news_live": [
        IndexModel([("id", ASCENDING)], name="news_id", unique=True),
        IndexModel([("published_at", DESCENDING)], name="published_desc"),
        IndexModel([("expire_at", ASCENDING)], name="news_ttl", expireAfterSeconds=0),
    ],
    "cron_runs": [IndexModel([("run_id", ASCENDING)], name="run_id", unique=True)],
    "push_subscriptions": [IndexModel([("endpoint", ASCENDING)], name="endpoint", unique=True)],
    "market_cache": [IndexModel([("id", ASCENDING)], name="cache_id", unique=True)],
    "user_forecasts": [IndexModel([("device_id", ASCENDING), ("ticker", ASCENDING)], name="dev_ticker")],
    "learn_progress": [IndexModel([("device_id", ASCENDING)], name="learn_dev")],
}


async def ensure_indexes() -> None:
    for collection, models in INDEXES.items():
        for model in models:
            try:
                await db[collection].create_indexes([model])
            except Exception as exc:
                log.error("ensure_indexes(%s.%s): %s", collection, model.document["name"], exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.index_task = asyncio.create_task(ensure_indexes())
    app.state.bg_tasks = set()
    schedule_news_refresh(app)  # warm the feed on boot
    yield
    app.state.index_task.cancel()
    with suppress(asyncio.CancelledError):
        await app.state.index_task
    for t in list(app.state.bg_tasks):
        t.cancel()
    client.close()


app = FastAPI(lifespan=lifespan)
api_router = APIRouter(prefix="/api")


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    return now_utc().isoformat()


# ─────────────────────────────────────────────────────────────────────────
# Generic cache (collection market_cache): {id, payload, cached_at}
# ─────────────────────────────────────────────────────────────────────────

async def cache_get(key: str, ttl: Optional[int] = None):
    """Return (payload, is_fresh). payload is None if missing. ttl=None -> always fresh."""
    doc = await db.market_cache.find_one({"id": key}, {"_id": 0})
    if not doc or "payload" not in doc:
        return None, False
    try:
        age = (now_utc() - datetime.fromisoformat(doc["cached_at"])).total_seconds()
    except Exception:
        return doc["payload"], False
    return doc["payload"], (ttl is None or age <= ttl)


async def cache_set(key: str, payload) -> None:
    await db.market_cache.update_one({"id": key}, {"$set": {"id": key, "payload": payload, "cached_at": iso_now()}}, upsert=True)


# ─────────────────────────────────────────────────────────────────────────
# Markets (Yahoo Finance → CoinGecko/Alpha Vantage for BTC → last known value)
# ─────────────────────────────────────────────────────────────────────────

async def _fetch_quote(asset: dict) -> Optional[dict]:
    data = await asyncio.to_thread(providers.fetch_yahoo, asset["yahoo"], "1mo")
    source = "yahoo"
    if not data and asset["id"] == "btc":
        data = await asyncio.to_thread(providers.fetch_coingecko_btc)
        source = "coingecko"
        if not data:
            data = await asyncio.to_thread(providers.fetch_alpha_vantage_btc, ALPHA_VANTAGE_API_KEY)
            source = "alpha_vantage"
    if not data:
        return None
    spark = [p["v"] for p in data.get("series", [])][-24:]
    return {"price": data["price"], "change": data["change"], "change_pct": data["change_pct"], "spark": spark, "source": source}


async def _quote_for(asset: dict) -> Optional[dict]:
    key = f"quote:{asset['id']}"
    cached, fresh = await cache_get(key, QUOTE_TTL)
    if cached and fresh:
        return {**cached, "stale": False}
    q = await _fetch_quote(asset)
    if q:
        await cache_set(key, q)
        return {**q, "stale": False}
    if cached:  # last known value, flagged as stale rather than invented
        return {**cached, "stale": True}
    return None


@api_router.get("/markets")
async def markets():
    quotes = await asyncio.gather(*[_quote_for(a) for a in providers.MARKET_ASSETS])
    out = []
    for a, q in zip(providers.MARKET_ASSETS, quotes):
        if not q:
            continue
        out.append({
            "id": a["id"], "symbol": a["symbol"], "name": a["name"], "currency": a["currency"],
            "price": q["price"], "change": q["change"], "change_pct": q["change_pct"],
            "spark": q.get("spark", []), "source": q["source"], "stale": q.get("stale", False),
        })

    fg, fg_fresh = await cache_get("feargreed", FEARGREED_TTL)
    if fg is None or not fg_fresh:
        live = await asyncio.to_thread(providers.fetch_fear_greed)
        if live is not None:
            fg = {"value": live, "source": "cnn"}
            await cache_set("feargreed", fg)
    if fg is None:
        fg = {"value": providers.estimate_fear_greed([m["change_pct"] for m in out]), "source": "estimate"}

    return {
        "markets": out,
        "fear_greed": fg["value"],
        "fear_greed_source": fg["source"],
        "updated_at": iso_now(),
        "sources": sorted({m["source"] for m in out}),
        "live": bool(out) and not all(m["stale"] for m in out),
    }


@api_router.get("/chart/{asset_id}")
async def chart(asset_id: str, range_days: int = 30):
    asset = next((a for a in providers.MARKET_ASSETS if a["id"] == asset_id), None)
    if not asset:
        raise HTTPException(404, "Asset not found")
    range_days = max(7, min(range_days, 365))
    key = f"chart:{asset_id}:{range_days}"
    cached, fresh = await cache_get(key, CHART_TTL)
    if cached and fresh:
        return {"asset": asset_id, "series": cached, "stale": False}
    series = await asyncio.to_thread(providers.fetch_chart_series, asset["yahoo"], range_days)
    if series:
        await cache_set(key, series)
        return {"asset": asset_id, "series": series, "stale": False}
    if cached:
        return {"asset": asset_id, "series": cached, "stale": True}
    raise HTTPException(503, "Storico non disponibile al momento")


# ─────────────────────────────────────────────────────────────────────────
# News feed
# ─────────────────────────────────────────────────────────────────────────

def _demo_items() -> list[dict]:
    now = now_utc()
    return [{**n, "published_at": (now - timedelta(minutes=n["age_minutes"])).isoformat(), "demo": True} for n in content.DEMO_NEWS]


def _parse_dt(d) -> datetime:
    try:
        dt = datetime.fromisoformat((d or "").replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        return datetime.fromtimestamp(0, tz=timezone.utc)


def _matches_query(n: dict, ql: str) -> bool:
    hay = [n.get("title"), n.get("ticker"), n.get("region"), " ".join(n.get("tags") or []), " ".join(n.get("bullets") or []), " ".join(n.get("sources") or [])]
    return any(ql in (h or "").lower() for h in hay)


@api_router.get("/news")
async def news(
    category: Optional[str] = None,
    min_impact: int = 0,
    max_impact: int = 10,
    q: Optional[str] = None,
    tags: Optional[str] = None,  # comma-separated
    since_hours: Optional[int] = None,
    limit: int = 80,
):
    live = await db.news_live.find({}, {"_id": 0, "expire_at": 0}).sort("published_at", -1).limit(150).to_list(150)
    newest = max((_parse_dt(n.get("fetched_at")) for n in live), default=None)
    stale = newest is None or (now_utc() - newest).total_seconds() > NEWS_REFRESH_EVERY_SEC
    refreshing = schedule_news_refresh(app) if stale else False

    demo = not live
    items = _demo_items() if demo else live
    if category and category != "all":
        items = [n for n in items if n.get("category") == category]
    items = [n for n in items if min_impact <= int(n.get("impact", 0)) <= max_impact]
    if q:
        ql = q.strip().lower()
        items = [n for n in items if _matches_query(n, ql)]
    if tags:
        wanted = {t.strip().lower().lstrip("#") for t in tags.split(",") if t.strip()}
        items = [n for n in items if wanted & {(t or "").lower().lstrip("#") for t in n.get("tags", [])}]
    if since_hours:
        cutoff = now_utc() - timedelta(hours=since_hours)
        items = [n for n in items if _parse_dt(n.get("published_at")) >= cutoff]
    items.sort(key=lambda x: (x.get("impact", 0), x.get("published_at", "")), reverse=True)
    items = items[: max(1, min(limit, 150))]
    return {"items": items, "count": len(items), "demo": demo, "refreshing": refreshing}


@api_router.get("/news/tags")
async def news_tags():
    live = await db.news_live.find({}, {"_id": 0, "tags": 1}).to_list(300)
    source = live if live else content.DEMO_NEWS
    tagset = {(t or "").lstrip("#") for n in source for t in (n.get("tags") or [])}
    return {"tags": sorted(t for t in tagset if t)[:40]}


@api_router.get("/news/{news_id}")
async def news_detail(news_id: str):
    doc = await db.news_live.find_one({"id": news_id}, {"_id": 0, "expire_at": 0})
    if doc:
        return doc
    for n in _demo_items():
        if n["id"] == news_id:
            return n
    raise HTTPException(404, "News not found")


# ─────────────────────────────────────────────────────────────────────────
# News refresh pipeline: fetch → dedupe → enrich with AI (or heuristic) → store
# ─────────────────────────────────────────────────────────────────────────

_refresh_lock = asyncio.Lock()


def _interleave(groups: list[list[dict]]) -> list[dict]:
    """Round-robin across providers so one source cannot flood the feed."""
    out, i = [], 0
    while any(i < len(g) for g in groups):
        for g in groups:
            if i < len(g):
                out.append(g[i])
        i += 1
    return out


async def _enrich_one(raw: dict, sem: asyncio.Semaphore) -> dict:
    if not llm.available():
        return enrich.heuristic_item(raw)
    async with sem:
        text = await llm.complete(enrich.SYSTEM_PROMPT, enrich.build_prompt(raw), session_id=f"enrich-{uuid.uuid4().hex}", json_mode=True)
    data = enrich.parse_llm_json(text)
    return enrich.build_item(raw, data) if data else enrich.heuristic_item(raw)


async def _run_refresh_news(run_id: str) -> None:
    try:
        await db.cron_runs.insert_one({"run_id": run_id, "started_at": iso_now()})
    except Exception:  # duplicate run_id → already handled (idempotent)
        return
    stats = {"fetched": 0, "stored": 0, "critical": 0, "ai": llm.backend()}
    try:
        fin, napi, rss = await asyncio.gather(
            asyncio.to_thread(providers.fetch_finnhub_news, FINNHUB_API_KEY),
            asyncio.to_thread(providers.fetch_newsapi, NEWSAPI_API_KEY),
            asyncio.to_thread(providers.fetch_all_rss),
        )
        by_provider = {}
        for it in providers.dedupe_news(fin + napi + rss):
            by_provider.setdefault(it.get("source") if it["provider"] == "rss" else it["provider"], []).append(it)
        raw_items = _interleave([sorted(g, key=lambda r: r["published_at"], reverse=True) for g in by_provider.values()])[:60]
        stats["fetched"] = len(raw_items)

        existing = {d["id"] async for d in db.news_live.find({"id": {"$in": [enrich.item_id(r) for r in raw_items]}}, {"id": 1, "_id": 0})}
        todo = enrich.select_for_enrichment(raw_items, existing, MAX_ENRICH_PER_RUN)
        sem = asyncio.Semaphore(3)
        items = await asyncio.gather(*[_enrich_one(r, sem) for r in todo])

        expire_at = now_utc() + timedelta(days=NEWS_TTL_DAYS)
        critical = []
        for item in items:
            item["fetched_at"] = iso_now()
            item["expire_at"] = expire_at
            await db.news_live.update_one({"id": item["id"]}, {"$set": item}, upsert=True)
            stats["stored"] += 1
            if item.get("impact", 0) >= 9 and item.get("enriched"):
                critical.append(item)
        stats["critical"] = len(critical)
        for ci in critical:
            await _broadcast_push(f"⚡ Allerta Impact {ci['impact']}/10", ci.get("title") or "", "/")
    except Exception:
        log.exception("refresh_news failed")
        stats["error"] = True
    finally:
        await db.cron_runs.update_one({"run_id": run_id}, {"$set": {"finished_at": iso_now(), **stats}})


def schedule_news_refresh(app_: FastAPI) -> bool:
    """Start a background refresh unless one is already running. Idempotent per 15-min bucket."""
    if _refresh_lock.locked():
        return True
    run_id = f"auto-{int(now_utc().timestamp() // NEWS_REFRESH_EVERY_SEC)}"

    async def _job():
        async with _refresh_lock:
            await _run_refresh_news(run_id)

    task = asyncio.create_task(_job())
    app_.state.bg_tasks.add(task)
    task.add_done_callback(app_.state.bg_tasks.discard)
    return True


@api_router.post("/cron/refresh-news")
async def cron_refresh_news(request: Request, background: BackgroundTasks, authorization: str = Header(default=""), x_webhook_id: str = Header(default="")):
    """Optional: call from any scheduler (cron, GitHub Actions…) with 'Authorization: Bearer <WEBHOOK_CRON_SECRET>'.
    Not required: /api/news refreshes the feed by itself when it is older than 15 minutes."""
    if not WEBHOOK_CRON_SECRET:
        raise HTTPException(500, "cron secret not configured")
    if not hmac.compare_digest(authorization or "", f"Bearer {WEBHOOK_CRON_SECRET}"):
        raise HTTPException(401, "unauthorized")
    try:
        body = await request.json()
    except Exception:
        body = {}
    run_id = x_webhook_id or (body.get("run_id") if isinstance(body, dict) else None) or f"manual-{int(now_utc().timestamp())}"

    async def _job():
        async with _refresh_lock:
            await _run_refresh_news(run_id)

    background.add_task(_job)
    return {"ok": True, "run_id": run_id}


@api_router.get("/live-news-status")
async def live_news_status():
    count = await db.news_live.count_documents({})
    last_run = await db.cron_runs.find_one({}, {"_id": 0}, sort=[("started_at", -1)])
    return {
        "has_keys": {"finnhub": bool(FINNHUB_API_KEY), "newsapi": bool(NEWSAPI_API_KEY), "alpha_vantage": bool(ALPHA_VANTAGE_API_KEY)},
        "rss_feeds": len(providers.RSS_FEEDS),
        "ai_backend": llm.backend(),
        "live_items": count,
        "last_run": last_run,
    }


# ─────────────────────────────────────────────────────────────────────────
# Accadde oggi
# ─────────────────────────────────────────────────────────────────────────

@api_router.get("/history/today")
async def history_today():
    return content.pick_history(now_utc())[0]


@api_router.get("/history/curiosities")
async def history_curiosities(limit: int = 10):
    return {"items": content.pick_history(now_utc())[: max(1, min(limit, 30))]}


# ─────────────────────────────────────────────────────────────────────────
# Geopolitical radar (curated hotspots + live related headlines)
# ─────────────────────────────────────────────────────────────────────────

async def _related_headlines(h: dict, recent: list[dict]) -> list[dict]:
    kws = h["keywords"]
    hits = [n for n in recent if any(k in (n.get("title", "") + " " + " ".join(n.get("bullets") or [])).lower() for k in kws)]
    return [{"id": n["id"], "title": n["title"], "published_at": n.get("published_at"), "impact": n.get("impact")} for n in hits[:3]]


@api_router.get("/radar")
async def radar():
    cutoff = (now_utc() - timedelta(hours=72)).isoformat()
    recent = await db.news_live.find({"published_at": {"$gte": cutoff}}, {"_id": 0, "id": 1, "title": 1, "bullets": 1, "published_at": 1, "impact": 1}).sort("published_at", -1).to_list(200)
    out = []
    for h in content.RADAR:
        item = {k: v for k, v in h.items() if k != "keywords"}
        item["headlines"] = await _related_headlines(h, recent)
        out.append(item)
    return {"hotspots": sorted(out, key=lambda x: -x["severity"])}


@api_router.get("/radar/{hotspot_id}")
async def radar_detail(hotspot_id: str):
    for h in content.RADAR:
        if h["id"] == hotspot_id:
            return {k: v for k, v in h.items() if k != "keywords"}
    raise HTTPException(404, "Hotspot not found")


# ─────────────────────────────────────────────────────────────────────────
# Big Tech (live fundamentals from Finnhub → Alpha Vantage → editorial fallback)
# ─────────────────────────────────────────────────────────────────────────

_fund_sem = asyncio.Semaphore(3)


async def _fundamentals(ticker: str) -> dict:
    key = f"fund:{ticker}"
    cached, fresh = await cache_get(key, FUNDAMENTALS_TTL)
    if cached and fresh:
        return cached
    async with _fund_sem:
        data = await asyncio.to_thread(providers.fetch_finnhub_company, FINNHUB_API_KEY, ticker)
        if not all(k in data for k in ("pe", "revenue_ttm", "revenue_growth")):
            extra = await asyncio.to_thread(providers.fetch_alpha_overview, ALPHA_VANTAGE_API_KEY, ticker)
            data = {**extra, **data}
    if data:
        data["fundamentals_source"] = "live"
        await cache_set(key, data)
        return data
    return cached or {}


async def _enrich_company(base: dict) -> dict:
    live = await _fundamentals(base["ticker"])
    merged = {**base, **{k: v for k, v in live.items() if v is not None}}
    merged["fundamentals_source"] = live.get("fundamentals_source", "static")
    return merged


@api_router.get("/bigtech")
async def bigtech():
    companies = await asyncio.gather(*[_enrich_company(c) for c in content.BIG_TECH])
    return {"companies": companies}


@api_router.get("/bigtech/{ticker}")
async def bigtech_detail(ticker: str):
    base = next((c for c in content.BIG_TECH if c["ticker"] == ticker.upper()), None)
    if not base:
        raise HTTPException(404, "Ticker not found")
    return {**(await _enrich_company(base)), **content.BIG_TECH_DETAIL.get(ticker.upper(), {})}


@api_router.get("/scenarios")
async def scenarios():
    return {"scenarios": content.SCENARIOS}


@api_router.get("/macro")
async def macro():
    cached, fresh = await cache_get("macro", MACRO_TTL)
    if cached and fresh:
        return {"indicators": cached, "source": "live"}
    live = await asyncio.to_thread(providers.build_macro_indicators)
    if live:
        await cache_set("macro", live)
        return {"indicators": live, "source": "live"}
    if cached:
        return {"indicators": cached, "source": "stale"}
    return {"indicators": content.MACRO_FALLBACK, "source": "unavailable"}


# ─────────────────────────────────────────────────────────────────────────
# AI Copilot (streaming SSE, with conversation memory)
# ─────────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    session_id: str = Field(min_length=3, max_length=80)
    message: str = Field(min_length=1, max_length=4000)
    news_context: Optional[dict] = None


SYSTEM_PROMPT = (
    "Sei FlashPulse AI Copilot, un assistente finanziario/geopolitico in italiano. "
    "Il tuo stile: diretto, accessibile a tutti, spieghi i concetti complessi in modo chiaro "
    "con un pizzico di profondità per i curiosi. Usa esempi concreti e catene causa-effetto "
    "(l'effetto domino). Quando possibile cita precedenti storici rilevanti. Evita disclaimer "
    "lunghi: distingui in modo esplicito tra dati oggettivi e opinioni/previsioni. "
    "Formatta con brevi paragrafi e bullet quando serve. Non inventare prezzi o numeri specifici: "
    "se non hai dati certi dì che è una stima qualitativa. Non dare consigli di investimento personalizzati."
)

HISTORY_TURNS = 8


def build_chat_prompt(history: list[dict], message: str, ctx: Optional[dict]) -> str:
    parts = []
    if history:
        convo = "\n".join(f"{'Utente' if m['role'] == 'user' else 'Copilot'}: {m['content']}" for m in history)
        parts.append(f"CONVERSAZIONE PRECEDENTE:\n{convo}\n")
    if ctx:
        parts.append(
            f"CONTESTO NOTIZIA:\nTitolo: {ctx.get('title', '')}\n"
            f"Punti: {' | '.join(ctx.get('bullets') or [])}\n"
            f"Impact: {ctx.get('impact', '?')}/10, Tag: {', '.join(ctx.get('tags') or [])}\n"
            f"Effetto domino: {ctx.get('domino', '')}\n"
        )
    parts.append(f"DOMANDA UTENTE: {message}")
    return "\n".join(parts)


@api_router.post("/copilot/chat")
async def copilot_chat(body: ChatRequest):
    if not llm.available():
        raise HTTPException(503, "Il Copilot non è configurato (manca GEMINI_API_KEY o EMERGENT_LLM_KEY)")

    prev = await db.copilot_messages.find({"session_id": body.session_id}, {"_id": 0, "role": 1, "content": 1}).sort("created_at", -1).limit(HISTORY_TURNS).to_list(HISTORY_TURNS)
    prompt = build_chat_prompt(list(reversed(prev)), body.message, body.news_context)
    await db.copilot_messages.insert_one({"session_id": body.session_id, "role": "user", "content": body.message, "created_at": iso_now()})

    async def event_generator():
        collected: list[str] = []
        try:
            async for delta in llm.stream(SYSTEM_PROMPT, prompt, session_id=f"{body.session_id}-{uuid.uuid4().hex[:8]}"):
                collected.append(delta)
                yield f"data: {json.dumps({'delta': delta})}\n\n"
        except Exception as exc:
            log.exception("copilot stream error")
            yield f"data: {json.dumps({'error': 'Il Copilot non è raggiungibile in questo momento. Riprova tra poco.'})}\n\n"
            log.error("copilot error detail: %s", exc)
        final = "".join(collected).strip()
        if final:
            await db.copilot_messages.insert_one({"session_id": body.session_id, "role": "assistant", "content": final, "created_at": iso_now()})
        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@api_router.get("/copilot/history/{session_id}")
async def copilot_history(session_id: str, limit: int = 50):
    limit = max(1, min(limit, 200))
    msgs = await db.copilot_messages.find({"session_id": session_id}, {"_id": 0}).sort("created_at", 1).limit(limit).to_list(limit)
    return {"messages": msgs}


# ─────────────────────────────────────────────────────────────────────────
# Web Push
# ─────────────────────────────────────────────────────────────────────────

class PushSubscribeBody(BaseModel):
    endpoint: str
    keys: dict
    device_id: str


@api_router.get("/push/public-key")
async def push_public_key():
    return {"public_key": VAPID_PUBLIC_KEY or ""}


@api_router.post("/push/subscribe")
async def push_subscribe(body: PushSubscribeBody):
    doc = {"endpoint": body.endpoint, "keys": body.keys, "device_id": body.device_id, "subscribed_at": iso_now()}
    await db.push_subscriptions.update_one({"endpoint": body.endpoint}, {"$set": doc}, upsert=True)
    return {"ok": True}


@api_router.post("/push/unsubscribe")
async def push_unsubscribe(body: dict):
    ep = body.get("endpoint")
    if ep:
        await db.push_subscriptions.delete_one({"endpoint": ep})
    return {"ok": True}


async def _send_webpush(sub: dict, title: str, body: str, url: str = "/") -> bool:
    if not VAPID_PRIVATE_KEY:
        return False
    try:
        await asyncio.to_thread(
            webpush,
            subscription_info={"endpoint": sub["endpoint"], "keys": sub["keys"]},
            data=json.dumps({"title": title, "body": body, "url": url}),
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims={"sub": VAPID_SUBJECT},
        )
        return True
    except WebPushException as e:
        if e.response is not None and e.response.status_code in (404, 410):
            await db.push_subscriptions.delete_one({"endpoint": sub["endpoint"]})
        return False
    except Exception:
        return False


async def _broadcast_push(title: str, body: str, url: str = "/") -> None:
    async for sub in db.push_subscriptions.find({}):
        await _send_webpush(sub, title, body, url)


@api_router.post("/push/test")
async def push_test(body: dict):
    device_id = body.get("device_id")
    if not device_id:
        raise HTTPException(400, "device_id required")
    sent = 0
    async for sub in db.push_subscriptions.find({"device_id": device_id}):
        if await _send_webpush(sub, "⚡ Test FlashPulse", "Le notifiche critiche sono attive. Ti avviserò per Impact ≥ 9.", "/"):
            sent += 1
    return {"sent": sent}


# ─────────────────────────────────────────────────────────────────────────
# User forecasts (per device)
# ─────────────────────────────────────────────────────────────────────────

class ForecastBody(BaseModel):
    device_id: str = Field(min_length=3, max_length=80)
    ticker: str = Field(pattern=r"^[A-Za-z0-9.\-]{1,10}$")
    direction: Literal["bullish", "neutral", "bearish"]
    target_price: Optional[float] = Field(default=None, gt=0, lt=1e9)
    horizon_months: int = Field(default=6, ge=1, le=60)
    thesis: str = Field(min_length=1, max_length=500)


@api_router.post("/forecasts")
async def create_forecast(body: ForecastBody):
    doc = {
        "device_id": body.device_id, "ticker": body.ticker.upper(), "direction": body.direction,
        "target_price": body.target_price, "horizon_months": body.horizon_months,
        "thesis": body.thesis.strip(), "created_at": iso_now(),
    }
    res = await db.user_forecasts.insert_one(doc)
    doc["id"] = str(res.inserted_id)
    doc.pop("_id", None)
    return doc


@api_router.get("/forecasts")
async def list_forecasts(device_id: str):
    cur = db.user_forecasts.find({"device_id": device_id}, {"_id": 0}).sort("created_at", -1)
    return {"forecasts": await cur.to_list(50)}


@api_router.delete("/forecasts/{ticker}")
async def delete_forecast(ticker: str, device_id: str):
    res = await db.user_forecasts.delete_many({"device_id": device_id, "ticker": ticker.upper()})
    return {"deleted": res.deleted_count}


# ─────────────────────────────────────────────────────────────────────────
# Learn
# ─────────────────────────────────────────────────────────────────────────

@api_router.get("/learn/word-of-day")
async def learn_word_of_day():
    return content.LEARN_TERMS[now_utc().toordinal() % len(content.LEARN_TERMS)]


@api_router.get("/learn/terms")
async def learn_terms():
    return {"terms": content.LEARN_TERMS}


@api_router.get("/learn/quiz")
async def learn_quiz():
    return {"questions": content.daily_quiz(now_utc())}


def _bounded_int(v, lo: int, hi: int) -> int:
    try:
        return max(lo, min(hi, int(v)))
    except (TypeError, ValueError):
        return lo


@api_router.post("/learn/progress")
async def learn_progress(body: dict):
    device_id = body.get("device_id")
    if not device_id or not isinstance(device_id, str) or len(device_id) > 80:
        raise HTTPException(400, "device_id required")
    inc = {"xp": _bounded_int(body.get("xp", 0), 0, 50), "correct": _bounded_int(body.get("correct", 0), 0, 1), "wrong": _bounded_int(body.get("wrong", 0), 0, 1)}
    await db.learn_progress.update_one({"device_id": device_id}, {"$inc": inc, "$set": {"updated_at": iso_now()}}, upsert=True)
    return await db.learn_progress.find_one({"device_id": device_id}, {"_id": 0}) or {}


@api_router.get("/learn/progress")
async def learn_progress_get(device_id: str):
    return await db.learn_progress.find_one({"device_id": device_id}, {"_id": 0}) or {}


@api_router.get("/")
async def root():
    return {"app": "FlashPulse", "status": "ok"}


app.include_router(api_router)

_origins = [o.strip() for o in os.environ.get("CORS_ORIGINS", "*").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_credentials="*" not in _origins,  # credentials + wildcard origin is invalid per the CORS spec
    allow_origins=_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
