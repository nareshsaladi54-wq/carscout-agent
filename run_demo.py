#!/usr/bin/env python3
"""No-model demo: run the deterministic ranking and print CarScout's view."""
import json

from carscout import core

if __name__ == "__main__":
    result = core.rank()
    print(f"Reviewed {result['reviewed']} listings, {result['worth_your_time']} worth your time.\n")
    print("== SHORTLIST ==")
    for s in result["shortlist"]:
        delta = f"${s['price_delta']:+,.0f} vs fair" if s["price_delta"] is not None else "n/a"
        print(f"[{s['verdict'].upper():8}] {s['car']}  ${s['price']:,}  "
              f"{s['mileage']:,} mi  {delta}  {s['distance_mi']}mi away  (score {s['score']})")
        for f in s["red_flags"]:
            print(f"           flag: {f}")
    print("\n== WARNINGS (critical flags) ==")
    for s in result["all_scored"]:
        crit = [f for f in s["red_flags"] if f.startswith("CRITICAL")]
        if crit:
            print(f"{s['car']} ${s['price']:,} — {'; '.join(crit)}")
    print("\n== full ==")
    print(json.dumps(result["all_scored"], indent=2))
