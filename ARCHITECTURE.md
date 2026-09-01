# CarScout — Architecture

## Overview

A **single Strands agent** over a deterministic scoring core. The agent never
estimates a car's value; it triages the core's output and writes the brief.

```mermaid
flowchart TD
    SCHED[EventBridge Scheduler\nhourly] -->|invoke_agent_runtime| RT
    subgraph RT["Amazon Bedrock AgentCore Runtime (ARM64)"]
        APP["agentcore_app.py\nBedrockAgentCoreApp\n/invocations · /ping"]
        AGENT["Strands Agent 'carscout'\nClaude Haiku 4.5 on Bedrock\nprompt: protect the buyer's time"]
        APP --> AGENT
        AGENT -->|tool calls| TOOLS
        subgraph TOOLS["carscout/tools.py — @tool"]
            T1[scan_listings]
            T2[get_criteria]
            T3[explain_listing]
            T4[draft_message]
            T5[remember_note]
            T6[recall_notes]
        end
        T1 --> CORE["carscout/core.py (tested)\n• fair_price (depreciation model)\n• hard_match (criteria)\n• red_flags (scam / title / mileage)\n• score_listing + rank\n• draft_outreach"]
        T5 --> MEM["memory.py — readable notes\n(AgentCore Memory in prod)"]
        T6 --> MEM
    end
    CORE --> DATA[("data/listings.json → marketplace scraper / feed\ndata/criteria.json → buyer profile\ndata/baselines.json → valuation API")]
    AGENT --> OUT["shortlist + warnings\n(push / email)"]
```

## Components

| File | Responsibility |
|---|---|
| `agentcore_app.py` | AgentCore Runtime contract. `{prompt, actor_id}` → `{result}`. |
| `carscout/agent.py` | System prompt: lead with the shortlist, name the scams, don't list the misses. |
| `carscout/tools.py` | Six `@tool` wrappers — no logic. |
| `carscout/core.py` | **Correctness layer.** Fair price, criteria, red flags, ranking, outreach draft. |
| `carscout/memory.py` | Buyer decisions as one-line facts, namespaced by `actor_id`. |
| `tests/test_core.py` | 12 deterministic tests. |
| `run_demo.py` | Offline ranking dump. |

## How it meets the three hackathon requirements

| Requirement | Where |
|---|---|
| **Built with Strands Agents SDK** | `carscout/agent.py` — `strands.Agent` + `@tool`. |
| **Routine/repetitive background work** | The "check the marketplace, price everything, spot the scams" loop, run on a cron, output only when something is worth pursuing. |
| **Deployable on Amazon Bedrock AgentCore** | `agentcore_app.py` + `DEPLOY.md`. |

## Scoring model (in `core.py`)

- `fair_price` = model baseline − (age × per-year depreciation) − (miles × per-1k depreciation).
- `score` starts at 60 for a criteria match, adjusts ±25 for price vs fair,
  +6 private seller, +4 stale (negotiable), +3 per nice-to-have, −15 per red flag.
- A **CRITICAL** flag (bad title, scam-level underpricing) caps score at 5 and
  forces `verdict: skip` regardless of everything else.

## Model

`us.anthropic.claude-haiku-4-5-20251001-v1:0` by default (`MODEL_ID` to override), temp 0.2.
