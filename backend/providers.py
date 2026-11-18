"""Free data providers for FlashPulse.

Every network function here is *synchronous* (uses `requests`) and returns None / []
on failure: call them with `asyncio.to_thread(...)` from async code. All parsing is done in
small pure functions (`parse_*`) so it can be unit-tested without network access.

Sources (all free):
  - Yahoo Finance chart API (unofficial, no key)  -> indices, gold, oil, BTC quotes + history
  - CoinGecko (no key)                            -> BTC fallback
  - Alpha Vantage (key)                           -> BTC / company overview fallback
  - Finnhub (key)                                 -> general news, company quote + fundamentals
  - NewsAPI (key)                                 -> business / general headlines
  - RSS feeds (no key)                            -> ANSA, BBC, CNBC, Guardian
  - FRED CSV (no key)                             -> US rates, inflation, unemployment, Italian 10Y
  - ECB Data Portal (no key)                      -> ECB deposit rate, euro-area inflation
  - CNN Fear & Greed (unofficial, no key)         -> market sentiment
"""
from __future__ import annotations

import csv
import io
import logging
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from typing import Optional

import requests

log = logging.getLogger("flashpulse.providers")

UA = "Mozilla/5.0 (compatible; FlashPulse/1.0; +https://flashpulse.app)"
TIMEOUT = 12

# ──────────────────────────────────────────────────────────────────────────
# Market assets
# ──────────────────────────────────────────────────────────────────────────

MARKET_ASSETS = [
    {"id": "sp500", "symbol": "S&P 500", "name": "S&P 500", "currency": "USD", "yahoo": "^GSPC"},
    {"id": "nasdaq", "symbol": "NASDAQ", "name": "Nasdaq Composite", "currency": "USD", "yahoo": "^IXIC"},
    {"id": "ftsemib", "symbol": "FTSE MIB", "name": "FTSE MIB (Milano)", "currency": "EUR", "yahoo": "FTSEMIB.MI"},
    {"id": "gold", "symbol": "XAU", "name": "Oro (dollari/oncia)", "currency": "USD", "yahoo": "GC=F"},
    {"id": "oil", "symbol": "WTI", "name": "Petrolio WTI", "currency": "USD", "yahoo": "CL=F"},
    {"id": "btc", "symbol": "BTC", "name": "Bitcoin", "currency": "USD", "yahoo": "BTC-USD"},
]

# range_days requested by the UI -> (yahoo range, number of points to keep)
_YAHOO_RANGES = {7: ("1mo", 7), 30: ("1mo", 31), 90: ("3mo", 95), 365: ("1y", 370)}


def http_get(url: str, params: Optional[dict] = None, headers: Optional[dict] = None, timeout: int = TIMEOUT) -> Optional[requests.Response]:
    try:
        r = requests.get(url, params=params, headers={"User-Agent": UA, **(headers or {})}, timeout=timeout)
        if r.status_code != 200:
            log.warning("GET %s -> HTTP %s", url.split("?")[0], r.status_code)
            return None
        return r
    except Exception as exc:  # network, timeout, DNS…
        log.warning("GET %s failed: %s", url.split("?")[0], exc)
        return None


def _num(x) -> Optional[float]:
    try:
        f = float(x)
        return f if f == f else None  # filters NaN
    except (TypeError, ValueError):
        return None


# ──────────────────────────────────────────────────────────────────────────
# Yahoo Finance
# ──────────────────────────────────────────────────────────────────────────

def parse_yahoo_chart(payload: dict) -> Optional[dict]:
    """Return {price, prev_close, change, change_pct, series:[{t,v}]} from a Yahoo v8 chart payload."""
    try:
        res = (payload.get("chart") or {}).get("result") or []
        if not res:
            return None
        res = res[0]
        meta = res.get("meta") or {}
        ts = res.get("timestamp") or []
        closes = ((res.get("indicators") or {}).get("quote") or [{}])[0].get("close") or []
        offset = int(meta.get("gmtoffset") or 0)
        series = []
        for t, c in zip(ts, closes):
            c = _num(c)
            if c is None:
                continue
            day = datetime.fromtimestamp(int(t) + offset, tz=timezone.utc).date().isoformat()
            series.append({"t": day, "v": round(c, 2)})
        if not series:
            return None
        price = _num(meta.get("regularMarketPrice"))
        if price is None:
            price = series[-1]["v"]
        # Previous close: if the last bar is the live session's bar, use the bar before it.
        mkt_t = meta.get("regularMarketTime")
        today = datetime.fromtimestamp(int(mkt_t) + offset, tz=timezone.utc).date().isoformat() if mkt_t else series[-1]["t"]
        if series[-1]["t"] == today and len(series) >= 2:
            prev = series[-2]["v"]
        else:
            prev = series[-1]["v"]
        change = price - prev
        pct = (change / prev * 100) if prev else 0.0
        return {
            "price": round(price, 2),
            "prev_close": round(prev, 2),
            "change": round(change, 2),
            "change_pct": round(pct, 2),
            "series": series,
        }
    except Exception as exc:
        log.warning("parse_yahoo_chart: %s", exc)
        return None


def fetch_yahoo(symbol: str, range_: str = "1mo") -> Optional[dict]:
    for host in ("query1", "query2"):
        r = http_get(
            f"https://{host}.finance.yahoo.com/v8/finance/chart/{requests.utils.quote(symbol, safe='')}",
            params={"range": range_, "interval": "1d"},
        )
        if r is not None:
            try:
                parsed = parse_yahoo_chart(r.json())
            except ValueError:
                parsed = None
            if parsed:
                return parsed
    return None


def fetch_chart_series(symbol: str, range_days: int) -> Optional[list[dict]]:
    key = min(_YAHOO_RANGES, key=lambda k: abs(k - range_days))
    yr, keep = _YAHOO_RANGES[key]
    data = fetch_yahoo(symbol, yr)
    return data["series"][-keep:] if data else None


def fetch_coingecko_btc() -> Optional[dict]:
    r = http_get("https://api.coingecko.com/api/v3/simple/price", params={"ids": "bitcoin", "vs_currencies": "usd", "include_24hr_change": "true"})
    if r is None:
        return None
    try:
        b = r.json()["bitcoin"]
        price, pct = float(b["usd"]), float(b.get("usd_24h_change") or 0.0)
        return {"price": round(price, 2), "change": round(price * pct / 100, 2), "change_pct": round(pct, 2), "series": []}
    except Exception:
        return None


def fetch_alpha_vantage_btc(key: Optional[str]) -> Optional[dict]:
    if not key:
        return None
    r = http_get("https://www.alphavantage.co/query", params={"function": "CURRENCY_EXCHANGE_RATE", "from_currency": "BTC", "to_currency": "USD", "apikey": key})
    try:
        price = float(r.json()["Realtime Currency Exchange Rate"]["5. Exchange Rate"]) if r else None
    except Exception:
        price = None
    return {"price": round(price, 2), "change": 0.0, "change_pct": 0.0, "series": []} if price else None


# ──────────────────────────────────────────────────────────────────────────
# Fear & Greed
# ──────────────────────────────────────────────────────────────────────────

def parse_cnn_fear_greed(payload: dict) -> Optional[int]:
    try:
        score = float(payload["fear_and_greed"]["score"])
        return max(0, min(100, int(round(score))))
    except Exception:
        return None


def fetch_fear_greed() -> Optional[int]:
    r = http_get("https://production.dataviz.cnn.io/index/fearandgreed/graphdata", headers={"Accept": "application/json", "Referer": "https://edition.cnn.com/"})
    if r is None:
        return None
    try:
        return parse_cnn_fear_greed(r.json())
    except ValueError:
        return None


def estimate_fear_greed(changes_pct: list[float]) -> int:
    """Rough 0-100 estimate from today's average move. Always labelled 'stimato' in the UI."""
    if not changes_pct:
        return 50
    avg = sum(changes_pct) / len(changes_pct)
    return max(0, min(100, int(round(50 + avg * 12))))


# ──────────────────────────────────────────────────────────────────────────
# Fundamentals (Finnhub / Alpha Vantage)
# ──────────────────────────────────────────────────────────────────────────

def parse_finnhub_company(quote: dict, metric: dict, profile: dict) -> dict:
    m = (metric or {}).get("metric") or {}
    pe = _num(m.get("peTTM")) or _num(m.get("peBasicExclExtraTTM")) or _num(m.get("peNormalizedAnnual"))
    growth = _num(m.get("revenueGrowthTTMYoy"))
    rps = _num(m.get("revenuePerShareTTM"))
    shares = _num((profile or {}).get("shareOutstanding"))  # millions
    revenue_b = round(rps * shares / 1000, 1) if rps and shares else None
    out = {}
    if pe is not None:
        out["pe"] = round(pe, 1)
    if growth is not None:
        out["revenue_growth"] = round(growth, 1)
    if revenue_b is not None:
        out["revenue_ttm"] = revenue_b
    price = _num((quote or {}).get("c"))
    if price:
        out["price"] = round(price, 2)
        out["day_change_pct"] = round(_num((quote or {}).get("dp")) or 0.0, 2)
    return out


def fetch_finnhub_company(key: Optional[str], ticker: str) -> dict:
    if not key:
        return {}
    base = "https://finnhub.io/api/v1"
    out = {}
    try:
        q = http_get(f"{base}/quote", {"symbol": ticker, "token": key})
        mt = http_get(f"{base}/stock/metric", {"symbol": ticker, "metric": "all", "token": key})
        pf = http_get(f"{base}/stock/profile2", {"symbol": ticker, "token": key})
        out = parse_finnhub_company(q.json() if q else {}, mt.json() if mt else {}, pf.json() if pf else {})
    except Exception as exc:
        log.warning("finnhub company %s: %s", ticker, exc)
    return out


def parse_alpha_overview(d: dict) -> dict:
    out = {}
    pe = _num(d.get("PERatio"))
    rev = _num(d.get("RevenueTTM"))
    g = _num(d.get("QuarterlyRevenueGrowthYOY"))
    if pe is not None:
        out["pe"] = round(pe, 1)
    if rev is not None:
        out["revenue_ttm"] = round(rev / 1e9, 1)
    if g is not None:
        out["revenue_growth"] = round(g * 100, 1)
    return out


def fetch_alpha_overview(key: Optional[str], ticker: str) -> dict:
    if not key:
        return {}
    r = http_get("https://www.alphavantage.co/query", {"function": "OVERVIEW", "symbol": ticker, "apikey": key})
    try:
        return parse_alpha_overview(r.json()) if r else {}
    except ValueError:
        return {}


# ──────────────────────────────────────────────────────────────────────────
# News: Finnhub, NewsAPI, RSS
# ──────────────────────────────────────────────────────────────────────────

RSS_FEEDS = [
    {"source": "ANSA Economia", "url": "https://www.ansa.it/sito/notizie/economia/economia_rss.xml", "lang": "it"},
    {"source": "ANSA Mondo", "url": "https://www.ansa.it/sito/notizie/mondo/mondo_rss.xml", "lang": "it"},
    {"source": "BBC Business", "url": "https://feeds.bbci.co.uk/news/business/rss.xml", "lang": "en"},
    {"source": "BBC World", "url": "https://feeds.bbci.co.uk/news/world/rss.xml", "lang": "en"},
    {"source": "CNBC", "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html", "lang": "en"},
    {"source": "The Guardian", "url": "https://www.theguardian.com/business/rss", "lang": "en"},
]

_TAG_RE = re.compile(r"<[^>]+>")


def strip_html(s: Optional[str]) -> str:
    return re.sub(r"\s+", " ", unescape(_TAG_RE.sub(" ", s or ""))).strip()


def _iso(dt_str: Optional[str]) -> str:
    if dt_str:
        try:
            d = parsedate_to_datetime(dt_str)
            if d.tzinfo is None:
                d = d.replace(tzinfo=timezone.utc)
            return d.astimezone(timezone.utc).isoformat()
        except Exception:
            try:
                return datetime.fromisoformat(dt_str.replace("Z", "+00:00")).astimezone(timezone.utc).isoformat()
            except Exception:
                pass
    return datetime.now(timezone.utc).isoformat()


def parse_rss(xml_text: str, source: str, limit: int = 8) -> list[dict]:
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []
    out = []
    for item in root.iter("item"):
        title = strip_html(item.findtext("title"))
        if not title:
            continue
        out.append({
            "source": source,
            "title": title,
            "summary": strip_html(item.findtext("description"))[:500],
            "url": (item.findtext("link") or "").strip() or None,
            "published_at": _iso(item.findtext("pubDate")),
            "provider": "rss",
        })
        if len(out) >= limit:
            break
    return out


def fetch_rss(feed: dict, limit: int = 8) -> list[dict]:
    r = http_get(feed["url"], timeout=10)
    return parse_rss(r.text, feed["source"], limit) if r is not None else []


def fetch_all_rss(limit_per_feed: int = 6) -> list[dict]:
    items = []
    for f in RSS_FEEDS:
        items.extend(fetch_rss(f, limit_per_feed))
    return items


def fetch_finnhub_news(key: Optional[str], limit: int = 15) -> list[dict]:
    if not key:
        return []
    r = http_get("https://finnhub.io/api/v1/news", {"category": "general", "token": key})
    if r is None:
        return []
    try:
        items = r.json() or []
    except ValueError:
        return []
    out = []
    for a in items[:limit]:
        if not a.get("headline"):
            continue
        ts = a.get("datetime") or 0
        out.append({
            "source": a.get("source") or "Finnhub",
            "title": a["headline"],
            "summary": a.get("summary") or "",
            "url": a.get("url"),
            "published_at": datetime.fromtimestamp(ts, tz=timezone.utc).isoformat() if ts else datetime.now(timezone.utc).isoformat(),
            "provider": "finnhub",
        })
    return out


def parse_newsapi(payload: dict, limit: int = 15) -> list[dict]:
    out = []
    for a in (payload or {}).get("articles") or []:
        title = a.get("title") or ""
        if not title or title == "[Removed]":
            continue
        out.append({
            "source": (a.get("source") or {}).get("name") or "NewsAPI",
            "title": title,
            "summary": a.get("description") or "",
            "url": a.get("url"),
            "published_at": _iso(a.get("publishedAt")),
            "provider": "newsapi",
        })
        if len(out) >= limit:
            break
    return out


def fetch_newsapi(key: Optional[str]) -> list[dict]:
    if not key:
        return []
    out = []
    for params in (
        {"category": "business", "country": "us", "pageSize": 15},
        {"category": "general", "language": "en", "pageSize": 10},
    ):
        r = http_get("https://newsapi.org/v2/top-headlines", {**params, "apiKey": key})
        if r is not None:
            try:
                out.extend(parse_newsapi(r.json()))
            except ValueError:
                pass
    return out


def dedupe_news(items: list[dict]) -> list[dict]:
    """Drop duplicates by URL or by normalised title, keeping the first occurrence."""
    seen, out = set(), []
    for it in items:
        k1 = (it.get("url") or "").split("?")[0]
        k2 = re.sub(r"[^a-z0-9]+", "", (it.get("title") or "").lower())[:60]
        if (k1 and k1 in seen) or (k2 and k2 in seen):
            continue
        if k1:
            seen.add(k1)
        if k2:
            seen.add(k2)
        out.append(it)
    return out


# ──────────────────────────────────────────────────────────────────────────
# Macro: FRED + ECB
# ──────────────────────────────────────────────────────────────────────────

def parse_fred_csv(text: str) -> list[tuple[str, float]]:
    """FRED fredgraph.csv: header 'DATE,<ID>' (or 'observation_date,<ID>'); missing values are '.'"""
    out = []
    reader = csv.reader(io.StringIO(text))
    next(reader, None)
    for row in reader:
        if len(row) < 2:
            continue
        v = _num(row[1])
        if v is not None:
            out.append((row[0], v))
    return out


def parse_ecb_csv(text: str) -> list[tuple[str, float]]:
    out = []
    for row in csv.DictReader(io.StringIO(text)):
        v = _num(row.get("OBS_VALUE"))
        if v is not None and row.get("TIME_PERIOD"):
            out.append((row["TIME_PERIOD"], v))
    return sorted(out)


def fetch_fred(series_id: str) -> list[tuple[str, float]]:
    r = http_get("https://fred.stlouisfed.org/graph/fredgraph.csv", {"id": series_id})
    return parse_fred_csv(r.text) if r is not None else []


def fetch_ecb(flow_key: str, last_n: int = 400) -> list[tuple[str, float]]:
    r = http_get(f"https://data-api.ecb.europa.eu/service/data/{flow_key}", {"lastNObservations": last_n, "format": "csvdata"})
    return parse_ecb_csv(r.text) if r is not None else []


def it_num(x: float, dec: int = 2) -> str:
    return f"{x:.{dec}f}".replace(".", ",")


def _trend(delta: float, eps: float = 1e-9) -> str:
    return "up" if delta > eps else "down" if delta < -eps else "flat"


def last_change(values: list[float]) -> tuple[float, float]:
    """(latest value, change versus the previous *different* value)"""
    cur = values[-1]
    for v in reversed(values[:-1]):
        if abs(v - cur) > 1e-9:
            return cur, cur - v
    return cur, 0.0


def yoy_from_index(series: list[tuple[str, float]]) -> Optional[tuple[float, float]]:
    """Monthly price index -> (latest YoY %, change vs previous month's YoY in pp)"""
    if len(series) < 14:
        return None
    vals = [v for _, v in series]
    yoy_now = (vals[-1] / vals[-13] - 1) * 100
    yoy_prev = (vals[-2] / vals[-14] - 1) * 100
    return yoy_now, yoy_now - yoy_prev


def build_macro_indicators() -> list[dict]:
    """Assemble the macro cards from live data. Indicators whose source fails are skipped."""
    out: list[dict] = []

    def add(_id, name, value, delta_txt, delta):
        out.append({"id": _id, "name": name, "value": value, "delta": delta_txt, "trend": _trend(delta), "source": "live"})

    # Fed target range
    up, lo = fetch_fred("DFEDTARU"), fetch_fred("DFEDTARL")
    if up and lo:
        u, du = last_change([v for _, v in up])
        l = lo[-1][1]
        add("fedfunds", "Tassi Fed (USA)", f"{it_num(l)}–{it_num(u)}%", f"{du * 100:+.0f} pb".replace("+0 pb", "0 pb"), du)

    ecb = fetch_ecb("FM/B.U2.EUR.4F.KR.DFR.LEV")
    if ecb:
        v, d = last_change([x for _, x in ecb])
        add("ecb", "Tasso BCE (deposito)", f"{it_num(v)}%", f"{d * 100:+.0f} pb".replace("+0 pb", "0 pb"), d)

    cpi = yoy_from_index(fetch_fred("CPIAUCSL"))
    if cpi:
        add("cpi_us", "Inflazione USA", f"{it_num(cpi[0], 1)}%", f"{cpi[1]:+.1f} pp".replace(".", ","), cpi[1])

    hicp = fetch_ecb("ICP/M.U2.N.000000.4.ANR", 4)
    if len(hicp) >= 2:
        add("hicp_ea", "Inflazione Eurozona", f"{it_num(hicp[-1][1], 1)}%", f"{hicp[-1][1] - hicp[-2][1]:+.1f} pp".replace(".", ","), hicp[-1][1] - hicp[-2][1])

    t10 = fetch_fred("DGS10")
    if len(t10) >= 6:
        v = t10[-1][1]
        d = v - t10[-6][1]  # change over ~1 week
        add("ust10", "Rendimento Treasury 10Y", f"{it_num(v)}%", f"{d * 100:+.0f} pb (7g)", d)

    btp = fetch_fred("IRLTLT01ITM156N")
    if len(btp) >= 2:
        v, d = btp[-1][1], btp[-1][1] - btp[-2][1]
        add("btp10", "Rendimento BTP 10Y", f"{it_num(v)}%", f"{d * 100:+.0f} pb (mese)", d)

    un = fetch_fred("UNRATE")
    if len(un) >= 2:
        v, d = un[-1][1], un[-1][1] - un[-2][1]
        add("unrate", "Disoccupazione USA", f"{it_num(v, 1)}%", f"{d:+.1f} pp".replace(".", ","), d)
    return out
