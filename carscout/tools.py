"""Strands tools for CarScout. Thin wrappers over the deterministic core."""
from __future__ import annotations

from strands import tool

from . import core, memory


@tool
def scan_listings() -> dict:
    """Score every current listing against the buyer's criteria and return the
    ranked result with a shortlist of the ones worth pursuing."""
    return core.rank()


@tool
def get_criteria() -> dict:
    """The buyer's saved search: models, year, mileage, price, distance, deal-breakers."""
    return core.load_criteria()


@tool
def explain_listing(listing_id: str) -> dict:
    """Full scoring detail for one listing id (A-K): fair price, delta, red flags, verdict."""
    for l in core.load_listings():
        if l["id"] == listing_id:
            return {"listing": l,
                    "score": core.score_listing(l, core.load_criteria(), core.load_baselines())}
    return {"error": f"no listing {listing_id!r}"}


@tool
def draft_message(listing_id: str) -> str:
    """Draft a first-contact message to the seller of a listing (does not send)."""
    return core.draft_outreach(listing_id)


@tool
def remember_note(actor_id: str, note: str) -> str:
    """Save a durable buyer preference or decision (e.g. 'passed on listing J, too far in practice')."""
    return memory.remember(actor_id, note)


@tool
def recall_notes(actor_id: str, about: str = "") -> list[str]:
    """Recall durable buyer preferences/decisions, optionally filtered by topic."""
    return memory.recall(actor_id, about)


TOOLS = [scan_listings, get_criteria, explain_listing, draft_message,
         remember_note, recall_notes]
