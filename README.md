# CarScout

**A background agent that hunts used-car listings against your criteria, scores
every one for deal quality and risk, and surfaces only the few worth your time.**

Track: **Everyday Agents** · Built with the [Strands Agents SDK](https://strandsagents.com) · Deploys to **Amazon Bedrock AgentCore**

---

## The problem

Buying a used car is a part-time job: refresh the marketplace, open twenty
listings, mentally price each one against its year and mileage, spot the salvage
titles and the too-good-to-be-true scams, and message sellers before the good
ones vanish. It is repetitive, it is judgement-heavy, and it happens on the
listings' schedule, not yours.

CarScout watches the feed for you. It runs on a schedule, scores everything, and
brings back a two-line shortlist plus a list of what to avoid.

## What it does

1. **Scores every listing** (`scan_listings`) against a fair-price estimate
   (depreciation model over a public-knowledge baseline), your hard criteria,
   and a red-flag check.
2. **Flags risk**: salvage/rebuilt titles, prices far below market, wire-transfer
   and "friends and family" scam language, implausible mileage.
3. **Returns a shortlist** with verdicts (`pursue` / `consider` / `skip`), each
   with price-vs-fair in dollars, mileage, distance, and the one reason it stands out.
4. **Drafts seller outreach** on request (`draft_message`) — never sends.
5. **Remembers** your decisions so it stops re-showing dismissed cars.

## Design principle: the LLM never prices a car

Fair-price math, criteria matching, scam heuristics and ranking are all in
`carscout/core.py` with 12 tests (`tests/test_core.py`), no model, no network.
`python run_demo.py` runs the whole thing offline. The agent owns triage and
phrasing only.

## Run it

```bash
make venv
make test     # 12 deterministic tests
make demo     # offline ranking of the sample listings
make agent    # one real Bedrock turn
make serve    # AgentCore contract on :8080
```

Live output:

```
PURSUE   2018 Honda Civic  $12,900  62k mi  $1,320 under fair  18mi away
PURSUE   2019 Mazda 3      $13,200  51k mi  $1,910 under fair  34mi away
CONSIDER 2018 Honda Civic  $13,900  71k mi  fair price, listed 95 days (negotiable)

WARNINGS
  Listing B — $7,500, 54% below market, wire-transfer + "moving overseas"
  Listing C — rebuilt title (deal-breaker)
  Listing K — 45% below market, "friends and family" payment

6 others didn't meet your filters.
```

## Deploy to Amazon Bedrock AgentCore

See [DEPLOY.md](DEPLOY.md).

```bash
.venv/bin/agentcore configure -e agentcore_app.py -n carscout -rf requirements.txt
.venv/bin/agentcore deploy
.venv/bin/agentcore invoke '{"prompt": "What is worth my time today?"}'
```

Schedule it hourly with EventBridge to get the background watch.

## Data

`carscout/data/` is synthetic — 11 listings, a criteria file, a baseline table.
In production `core.load_listings` swaps for a marketplace scraper (the author's
`car_buy` Playwright tool drives a logged-in Facebook Marketplace session) or a
Cars.com / Autotrader feed, behind the same shape. `baselines.json` swaps for a
real valuation API.

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md).

## License

MIT — see [LICENSE](LICENSE).
