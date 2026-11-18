import json
from datetime import datetime, timezone

import providers as p


def _yahoo(ts_days, closes, price, market_time, gmt=0):
    return {"chart": {"result": [{
        "meta": {"regularMarketPrice": price, "regularMarketTime": market_time, "gmtoffset": gmt},
        "timestamp": ts_days,
        "indicators": {"quote": [{"close": closes}]},
    }]}}


def _ts(y, m, d, h=15):
    return int(datetime(y, m, d, h, tzinfo=timezone.utc).timestamp())


def test_yahoo_live_session_uses_previous_bar_as_prev_close():
    # last bar is today's (live) bar -> previous close is the bar before
    payload = _yahoo([_ts(2026, 11, 12), _ts(2026, 11, 13), _ts(2026, 11, 14)], [100.0, 110.0, 121.0], 121.0, _ts(2026, 11, 14, 16))
    r = p.parse_yahoo_chart(payload)
    assert r["price"] == 121.0 and r["prev_close"] == 110.0
    assert r["change"] == 11.0 and r["change_pct"] == 10.0
    assert [s["t"] for s in r["series"]][-1] == "2026-11-14"


def test_yahoo_market_closed_uses_last_bar_as_prev_close():
    # market time is a later day than the last bar (e.g. weekend snapshot)
    payload = _yahoo([_ts(2026, 11, 12), _ts(2026, 11, 13)], [100.0, 110.0], 112.0, _ts(2026, 11, 14, 10))
    r = p.parse_yahoo_chart(payload)
    assert r["prev_close"] == 110.0 and r["change"] == 2.0


def test_yahoo_skips_null_closes_and_handles_empty():
    payload = _yahoo([_ts(2026, 11, 12), _ts(2026, 11, 13)], [None, 50.0], 50.0, _ts(2026, 11, 13))
    assert len(p.parse_yahoo_chart(payload)["series"]) == 1
    assert p.parse_yahoo_chart({"chart": {"result": None}}) is None
    assert p.parse_yahoo_chart({}) is None


def test_fear_greed_parsing_and_estimate():
    assert p.parse_cnn_fear_greed({"fear_and_greed": {"score": 61.7}}) == 62
    assert p.parse_cnn_fear_greed({"x": 1}) is None
    assert p.estimate_fear_greed([]) == 50
    assert p.estimate_fear_greed([-10.0]) == 0 and p.estimate_fear_greed([10.0]) == 100


def test_finnhub_company_revenue_from_per_share():
    r = p.parse_finnhub_company({"c": 120.5, "dp": 1.234}, {"metric": {"peTTM": 37.44, "revenueGrowthTTMYoy": 94.52, "revenuePerShareTTM": 4.8}}, {"shareOutstanding": 24400})
    assert r["pe"] == 37.4 and r["revenue_growth"] == 94.5 and r["revenue_ttm"] == 117.1 and r["price"] == 120.5
    assert p.parse_finnhub_company({}, {}, {}) == {}


def test_alpha_overview():
    r = p.parse_alpha_overview({"PERatio": "31.2", "RevenueTTM": "391000000000", "QuarterlyRevenueGrowthYOY": "0.061"})
    assert r == {"pe": 31.2, "revenue_ttm": 391.0, "revenue_growth": 6.1}
    assert p.parse_alpha_overview({"PERatio": "None"}) == {}


RSS = """<?xml version="1.0"?><rss><channel>
<item><title>Borse &amp; tassi: Wall Street chiude in rialzo</title><link>https://ex.com/a?utm=1</link>
<description>&lt;p&gt;Il Dow sale &lt;b&gt;dell'1%&lt;/b&gt;.&lt;/p&gt;</description><pubDate>Sat, 14 Nov 2026 15:00:00 GMT</pubDate></item>
<item><title></title><link>https://ex.com/empty</link></item>
<item><title>Seconda notizia</title><link>https://ex.com/b</link></item>
</channel></rss>"""


def test_parse_rss_cleans_html_and_dates():
    items = p.parse_rss(RSS, "TEST")
    assert len(items) == 2
    assert items[0]["title"] == "Borse & tassi: Wall Street chiude in rialzo"
    assert items[0]["summary"] == "Il Dow sale dell'1% ."
    assert items[0]["published_at"].startswith("2026-11-14T15:00:00")
    assert p.parse_rss("<not xml", "X") == []


def test_parse_newsapi_skips_removed():
    items = p.parse_newsapi({"articles": [{"title": "[Removed]"}, {"title": "A", "source": {"name": "S"}, "publishedAt": "2026-11-14T10:00:00Z", "url": "u"}]})
    assert len(items) == 1 and items[0]["source"] == "S" and items[0]["published_at"].startswith("2026-11-14T10:00:00")


def test_dedupe_news_by_url_and_title():
    a = {"title": "Fed cuts rates!", "url": "https://x.com/1?utm=a"}
    b = {"title": "Other", "url": "https://x.com/1?utm=b"}
    c = {"title": "FED cuts rates", "url": "https://y.com/2"}
    d = {"title": "Different story", "url": "https://z.com/3"}
    assert providers_titles(p.dedupe_news([a, b, c, d])) == ["Fed cuts rates!", "Different story"]


def providers_titles(items):
    return [i["title"] for i in items]


def test_fred_and_ecb_csv():
    fred = "DATE,DGS10\n2026-11-10,4.40\n2026-11-11,.\n2026-11-12,4.45\n"
    assert p.parse_fred_csv(fred) == [("2026-11-10", 4.40), ("2026-11-12", 4.45)]
    ecb = "KEY,TIME_PERIOD,OBS_VALUE\nX,2026-11-02,2.25\nX,2026-11-01,2.50\nX,2026-11-03,\n"
    assert p.parse_ecb_csv(ecb) == [("2026-11-01", 2.5), ("2026-11-02", 2.25)]


def test_macro_math():
    assert p.last_change([4.5, 4.5, 4.25, 4.25]) == (4.25, -0.25)
    assert p.last_change([3.0]) == (3.0, 0.0)
    idx = [("m", 100 + i) for i in range(14)]  # 14 monthly points
    yoy, delta = p.yoy_from_index(idx)
    assert round(yoy, 2) == 11.88 and delta < 0
    assert p.yoy_from_index(idx[:5]) is None
    assert p.it_num(4.256) == "4,26"
