"""Deterministic tests - no model, no network."""
from carscout import core

CRIT = core.load_criteria()
BASE = core.load_baselines()


def _score(lid):
    l = next(x for x in core.load_listings() if x["id"] == lid)
    return core.score_listing(l, CRIT, BASE)


def test_fair_price_drops_with_age_and_miles():
    new = core.fair_price("Honda", "Civic", 2024, 10000, BASE)
    old = core.fair_price("Honda", "Civic", 2017, 120000, BASE)
    assert new > old


def test_good_deal_A_is_pursue():
    s = _score("A")
    assert s["meets_criteria"] and s["verdict"] == "pursue"
    assert s["price_delta"] < 0


def test_scam_B_is_flagged_and_skipped():
    s = _score("B")
    assert any("CRITICAL" in f for f in s["red_flags"])
    assert s["verdict"] == "skip" and s["score"] <= 5


def test_rebuilt_title_C_is_critical():
    s = _score("C")
    assert any("rebuilt title" in f for f in s["red_flags"])
    assert s["verdict"] == "skip"


def test_distance_D_fails_criteria():
    s = _score("D")
    assert not s["meets_criteria"]
    assert any("mi away" in m for m in s["criteria_misses"])


def test_over_budget_E_fails():
    assert not _score("E")["meets_criteria"]


def test_too_old_F_fails():
    assert not _score("F")["meets_criteria"]


def test_high_mileage_G_fails():
    assert not _score("G")["meets_criteria"]


def test_dealer_markup_H_matches_but_not_pursue():
    s = _score("H")
    assert s["meets_criteria"] and s["price_delta"] > 0
    assert s["verdict"] != "pursue"


def test_wire_language_K_flagged():
    s = _score("K")
    assert any("friends and family" in f or "scam" in f.lower() for f in s["red_flags"])


def test_rank_shortlist_excludes_criticals():
    r = core.rank()
    ids = {s["id"] for s in r["shortlist"]}
    assert "A" in ids
    assert "B" not in ids and "C" not in ids


def test_draft_outreach_mentions_the_car():
    msg = core.draft_outreach("A")
    assert "2018 Honda Civic" in msg and "inspection" in msg
