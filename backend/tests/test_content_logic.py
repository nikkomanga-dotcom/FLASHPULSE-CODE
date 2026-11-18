from datetime import datetime, timezone

import content
import enrich


def utc(y, m, d):
    return datetime(y, m, d, tzinfo=timezone.utc)


def test_history_exact_match_comes_first():
    top = content.pick_history(utc(2026, 11, 9))[0]
    assert top["exact"] and top["title"].startswith("Cade il Muro")
    assert top["date"] == "9 novembre 1989"


def test_history_nearest_when_no_exact():
    top = content.pick_history(utc(2026, 11, 15))[0]
    assert not top["exact"] and top["days_ago"] == 6


def test_history_wraps_around_new_year():
    top = content.pick_history(utc(2026, 12, 31))[0]
    assert abs(top["days_ago"]) <= 1 and top["day"] == 1 and top["month"] == 1


def test_event_dates_are_valid():
    for ev in content.HISTORY_EVENTS:
        datetime(ev["year"], ev["month"], ev["day"])


def test_daily_quiz_rotates_and_is_valid():
    a, b = content.daily_quiz(utc(2026, 11, 15)), content.daily_quiz(utc(2026, 11, 16))
    assert len(a) == 5 and a != b
    for q in content.QUIZZES:
        assert 0 <= q["correct"] < len(q["options"])


def test_radar_has_coordinates_for_every_hotspot():
    for h in content.RADAR:
        assert -90 <= h["lat"] <= 90 and -180 <= h["lng"] <= 180 and h["keywords"]


def test_parse_llm_json_handles_fences_and_garbage():
    assert enrich.parse_llm_json('```json\n{"impact": 7}\n```') == {"impact": 7}
    assert enrich.parse_llm_json("nessun json") is None
    assert enrich.parse_llm_json(None) is None


def test_build_item_sanitises_llm_output():
    raw = {"title": "Fed holds", "summary": "x", "source": "BBC", "url": "https://a/b", "published_at": "2026-11-14T10:00:00+00:00"}
    item = enrich.build_item(raw, {"title_it": "La Fed non cambia", "impact": "15", "tags": ["Tassi", "#USA", ""], "ticker": "null", "region": "Marte", "category": "boh", "bullets": ["a", "b", "c", "d"]})
    assert item["impact"] == 10 and item["tags"] == ["#Tassi", "#USA"] and item["ticker"] is None
    assert item["region"] == "Globale" and item["category"] == "macro" and len(item["bullets"]) == 3
    assert item["id"] == enrich.item_id(raw)


def test_heuristic_item_never_invents_analysis():
    raw = {"title": "Oil jumps as OPEC cuts output", "summary": "Crude rose 3%. Analysts expect more. Short.", "source": "CNBC", "url": "u", "published_at": "2026-11-14T10:00:00+00:00"}
    item = enrich.heuristic_item(raw)
    assert item["category"] == "energy" and item["enriched"] is False
    assert item["deep_dive"]["bull"] == "" and item["domino"] == ""


def test_select_for_enrichment_skips_existing_and_prefers_newest():
    raws = [{"title": f"t{i}", "url": f"u{i}", "published_at": f"2026-11-1{i}T00:00:00+00:00"} for i in range(5)]
    known = {enrich.item_id(raws[4])}
    picked = enrich.select_for_enrichment(raws, known, 2)
    assert [r["title"] for r in picked] == ["t3", "t2"]


def test_category_guess_uses_whole_words():
    assert enrich.guess_category("New software update at Las Vegas") == "markets"
    assert enrich.guess_category("Sanctions on Russia widen") == "geopolitics"
