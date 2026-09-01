"""Deterministic listing scoring. No LLM, no network. All of CarScout's
judgement about price fairness, scam risk and criteria matching lives here."""
from __future__ import annotations

import json

from .config import DATA_DIR

SCAM_UNDERPRICE = 0.30       # priced >=30% below fair value -> scam / hidden-problem risk
GOOD_DEAL_UNDER = 0.06       # >=6% below fair and clean -> worth the buyer's time
STALE_DAYS = 60             # listed this long -> seller likely negotiable
IMPLAUSIBLE_MILES_PER_YEAR = 2500   # far below typical use, paired with underpricing


def _load(name: str) -> dict:
    with open(DATA_DIR / name) as fh:
        return json.load(fh)


def load_listings() -> list[dict]:
    return _load("listings.json")["listings"]


def load_criteria() -> dict:
    return _load("criteria.json")


def load_baselines() -> dict:
    return _load("baselines.json")


def fair_price(make: str, model: str, year: int, mileage: int, baselines: dict) -> float | None:
    key = f"{make} {model}"
    base = baselines["models"].get(key)
    if base is None:
        return None
    age = max(0, baselines["reference_year"] - year)
    value = base - baselines["depreciation_per_year"] * age \
        - baselines["depreciation_per_1k_miles"] * (mileage / 1000)
    return round(max(value, 1500), 0)


def hard_match(listing: dict, criteria: dict) -> tuple[bool, list[str]]:
    fails = []
    wants = {(w["make"], w["model"]) for w in criteria["wants"]}
    if (listing["make"], listing["model"]) not in wants:
        fails.append("not a model on the list")
    if listing["year"] < criteria["year_min"]:
        fails.append(f"older than {criteria['year_min']}")
    if listing["mileage"] > criteria["max_mileage"]:
        fails.append(f"over {criteria['max_mileage']:,} mi")
    if listing["price"] > criteria["max_price"]:
        fails.append(f"over ${criteria['max_price']:,}")
    if listing["distance_mi"] > criteria["max_distance_mi"]:
        fails.append(f"over {criteria['max_distance_mi']} mi away")
    if criteria.get("transmission") and listing.get("transmission") != criteria["transmission"]:
        fails.append("wrong transmission")
    return (not fails), fails


def red_flags(listing: dict, criteria: dict, fair: float | None) -> list[str]:
    flags = []
    title = listing.get("title", "").lower()
    for bad in criteria.get("deal_breakers", []):
        if bad in title:
            flags.append(f"CRITICAL: {bad} title")
    if fair and listing["price"] <= fair * (1 - SCAM_UNDERPRICE):
        flags.append("CRITICAL: priced far below market — scam or hidden problem")
    age = max(1, load_baselines()["reference_year"] - listing["year"])
    if listing["mileage"] / age < IMPLAUSIBLE_MILES_PER_YEAR and fair \
            and listing["price"] < fair * 0.7:
        flags.append("implausibly low miles for the price")
    text = listing.get("description", "").lower()
    for phrase in ("wire", "deposit to hold", "friends and family", "shipping available",
                   "moving overseas", "text only"):
        if phrase in text:
            flags.append(f"scam-pattern language: “{phrase}”")
    return flags


def score_listing(listing: dict, criteria: dict, baselines: dict) -> dict:
    fair = fair_price(listing["make"], listing["model"], listing["year"],
                      listing["mileage"], baselines)
    matched, fails = hard_match(listing, criteria)
    flags = red_flags(listing, criteria, fair)
    critical = [f for f in flags if f.startswith("CRITICAL")]
    delta = round(listing["price"] - fair, 0) if fair else None
    delta_pct = round(delta / fair * 100, 1) if fair else None

    score = 0
    if matched:
        score = 60
        if delta_pct is not None:
            score -= max(-25, min(25, int(delta_pct)))   # cheaper than fair -> higher
        if listing["seller_type"] == "private":
            score += 6
        if listing["days_listed"] >= STALE_DAYS:
            score += 4
        for good in criteria.get("nice_to_have", []):
            if good in listing.get("description", "").lower():
                score += 3
    score -= 15 * len(flags)
    if critical:
        score = min(score, 5)
    score = max(0, min(100, score))

    verdict = "skip"
    if matched and not critical:
        if delta_pct is not None and delta_pct <= -GOOD_DEAL_UNDER * 100 and not flags:
            verdict = "pursue"
        elif score >= 55:
            verdict = "consider"

    return {
        "id": listing["id"],
        "car": f"{listing['year']} {listing['make']} {listing['model']}",
        "price": listing["price"], "mileage": listing["mileage"],
        "fair_price": fair, "price_delta": delta, "price_delta_pct": delta_pct,
        "seller_type": listing["seller_type"], "distance_mi": listing["distance_mi"],
        "days_listed": listing["days_listed"],
        "meets_criteria": matched, "criteria_misses": fails,
        "red_flags": flags, "score": score, "verdict": verdict,
    }


def rank(today_listings=None, criteria=None, baselines=None) -> dict:
    listings = today_listings or load_listings()
    criteria = criteria or load_criteria()
    baselines = baselines or load_baselines()
    scored = [score_listing(l, criteria, baselines) for l in listings]
    scored.sort(key=lambda s: -s["score"])
    shortlist = [s for s in scored if s["verdict"] in ("pursue", "consider")]
    return {
        "as_of": _load("listings.json")["as_of"],
        "reviewed": len(scored),
        "worth_your_time": len(shortlist),
        "shortlist": shortlist,
        "all_scored": scored,
    }


def draft_outreach(listing_id: str) -> str:
    listing = next((l for l in load_listings() if l["id"] == listing_id), None)
    if not listing:
        return f"no listing {listing_id!r}"
    car = f"{listing['year']} {listing['make']} {listing['model']}"
    return (
        f"Hi — I'm interested in your {car} ({listing['mileage']:,} miles). "
        f"Is it still available, and are you the original owner? "
        f"Any accident history or open recalls? "
        f"I can come see it this week and would bring a mechanic for a pre-purchase "
        f"inspection. Would that work? Thanks."
    )
