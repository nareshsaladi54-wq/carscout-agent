# CarScout — Devpost submission

## Elevator pitch
A background agent that hunts used-car listings against your criteria, scores
every one for deal quality and scam risk, and surfaces only the few worth your time.

## Inspiration
Shopping for a used car is a part-time job on the listings' schedule, not yours:
refresh, open twenty tabs, price each against its year and mileage, dodge the
salvage titles and wire-transfer scams, message fast before the good ones go.

## What it does
Runs on a cron, scores every listing against a fair-price estimate, your hard
filters and a red-flag check, and returns a short shortlist with `pursue` /
`consider` verdicts plus an explicit list of the scams and bad-title cars to
avoid. Drafts seller outreach on request. Remembers what you've dismissed.

## How we built it
- **Strands Agents SDK** — one `Agent`, six `@tool`s, a "protect the buyer's
  time" system prompt.
- **Amazon Bedrock** — Claude Haiku 4.5.
- **Amazon Bedrock AgentCore** — `BedrockAgentCoreApp` entrypoint, EventBridge cron.
- **Deterministic core** — fair-price depreciation model, criteria matching and
  scam heuristics in `carscout/core.py`, 12 tests, no model calls.

## Challenges
Scam detection that is strict without being paranoid. A CRITICAL flag (bad title
or a price far below market) hard-caps the score and forces `skip` — the LLM
can't be talked out of it by a persuasive description.

## Accomplishments
The whole valuation and risk layer runs offline (`make demo`). The agent is a
thin triage layer that's easy to trust because it can't do the math wrong.

## What we learned
"Only show me what matters" is a prompt problem *and* a data problem — you need
a `worth_your_time` signal from tested code for the model to lean on.

## What's next
Live marketplace scraping (Playwright, logged-in session), a real valuation API,
VIN history lookups, AgentCore Memory, push delivery.

## Built with
`strands-agents` · `amazon-bedrock` · `amazon-bedrock-agentcore` · `claude-haiku-4.5` ·
`python` · `boto3` · `eventbridge-scheduler`

## Try it out
- Code: https://github.com/nareshsaladi54-wq/carscout-agent
- `make venv && make test && make demo`

## Checklist
- [x] Public GitHub repo, MIT license
- [x] README + architecture diagram
- [x] Built with Strands Agents SDK
- [x] Deployable on Amazon Bedrock AgentCore
- [ ] Demo video (≤5 min)
- [ ] AWS Builder ID
