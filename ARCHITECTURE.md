# RATS ON WALLSTREET — Agentic OS Architecture

## 1-to-1 Mirror of Jack Roberts' Agentic OS (Open-Source Stack)

### Jack's Stack (Proprietary)
```
┌─────────────────────────────────────────────────┐
│           VISUAL OS DASHBOARD (localhost:8081)    │
│  ┌──────┬──────┬──────┐  ┌────────────────────┐ │
│  │ HOME │MEMORY│SKILLS│  │  GOAL + COST BAR   │ │
│  │WORKSP│DREAM │INSIGHT│  │  INFORGAPHIC       │ │
│  │SETTNG│      │      │  │                    │ │
│  └──────┴──────┴──────┘  └────────────────────┘ │
│  ┌────────────────────────────────────────────┐ │
│  │  TAB SYSTEM: Claude │ Hermes │ OpenClaw    │ │
│  │  ┌──────────────────────────────────────┐  │ │
│  │  │  AGENT VIEW / CHAT / LOGS           │  │ │
│  │  └──────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
                         │ (wraps)
┌─────────────────────────────────────────────────┐
│        CLAUDE CODE (persistent tmux agent)       │
│  - Goals loaded at session start                 │
│  - Self-improvement loop (error→retry)           │
│  - Cost tracking per turn                        │
│  - Proactive recommendations                     │
└─────────────────────────────────────────────────┘
```

### Rats on Wallstreet Stack (Open-Source → Better)
```
┌─────────────────────────────────────────────────┐
│     RATS AGENTIC OS DASHBOARD (port 9100)        │
│  ┌──────┬──────┬──────┐  ┌────────────────────┐ │
│  │ HOME │MEMORY│SKILLS│  │  MISSION + $ COST  │ │
│  │WORKSP│DREAMS│INSIGHT│  │  PIPELINE HEALTH   │ │
│  │SETTNG│      │      │  │  INFORGAPHIC       │ │
│  └──────┴──────┴──────┘  └────────────────────┘ │
│  ┌────────────────────────────────────────────┐ │
│  │  TAB SYSTEM: 🐀 Pi │ ⚡ Codex │ 🐁 OpenClaw │ │
│  │  ┌──────────────────────────────────────┐  │ │
│  │  │  AGENT VIEW / CHAT / LOGS / METRICS │  │ │
│  │  └──────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
                         │ (wraps)
┌─────────────────────────────────────────────────┐
│  HERMES GATEWAY (always-on daemon)               │
│  ├── Pi (DeepSeek V4 Pro) — persistent agent     │
│  ├── Codex (GPT-5.5) — heavy coding             │
│  ├── OpenClaw (Jane) — floor operations          │
│  └── Gateway Logs MCP — full observability      │
│                                                   │
│  PERSISTENT LAYER:                                │
│  ├── OpenRouter API → cost tracking              │
│  ├── Obsidian Vault → durable memory             │
│  ├── NotebookLM → long-term context              │
│  └── Pipeline crons → market data                │
└─────────────────────────────────────────────────┘
```

---

## Component Mapping (1-to-1 + Improvements)

### LAYER 1: Persistent Agent OS

| Jack (Claude Code) | Rats (Open-Source) | Why Better |
|---|---|---|
| Claude Code in tmux | **Pi (DeepSeek V4 Pro) in Hermes `hermes chat`** | Open-source model, 80%+ cheaper, no Claude lock-in |
| Single model only | **Multi-model routing** — Pi for cheap tasks, Codex for heavy | Cost optimization per task type |
| Manual self-improvement | **Memory Dreaming cron** + **Baton Protocol** — automated | Already built and running |

### LAYER 2: Visual OS Dashboard

| Jack's Feature | Our Implementation | Open-Source Tool |
|---|---|---|
| **Home** — agent status, goal, costs | **Command Center** — live agent health, mission goal, token meter, pipeline health graph | Vanilla HTML/CSS/JS (0 framework debt) |
| **Memory Core** — source toggles (Claude/ChatGPT/Obsidian/Pinecone) | **Memory Vault** — toggles (Hermes/Obsidian/NotebookLM/Gateway Logs) | Obsidian API + Hermes memory API |
| **Workspace** — active projects | **War Room** — pipeline stages, Kanban view, active trades | Hermes Kanban + Gateway Logs |
| **Skills** — hours saved, $ value, breakdown | **Skills** — real pipeline metrics, hours saved, cost savings | Hermes skill_view + pipeline data |
| **+Dream** — daily/weekly scheduling | **Dreams** — Memory Dreaming cron UI + scheduling panel | memory_dreaming.py (already built) |
| **Insights** — improvement recommendations | **Insights** — pipeline analysis, cost optimization suggestions | Gateway Logs MCP + pipeline data |
| **Settings** — model config, API keys | **Settings** — model routing, provider config, key management | Hermes config API |

### LAYER 3: Tab System (Runtime Switching)

| Jack's Tabs | Our Tabs |
|---|---|
| Claude | **Pi (🐀 DeepSeek V4 Pro)** — persistent agent view |
| Hermes | **Codex (⚡ GPT-5.5)** — heavy coding agent view |
| OpenClaw | **OpenClaw (🐁 Jane)** — floor operations view |

### LAYER 4: Self-Improvement Loop

Jack: "When errors hit → reads error → generates new thought process → retries"
- Single loop, single agent

Rats: **Multi-loop, multi-signal**
1. Pipeline failures → retry with different model routing
2. Empty pipeline cycles → broaden scan parameters (ghost town discipline)
3. Token cost spikes → shift to cheaper model tier
4. Memory growth → auto-curation via Vault Framework
5. Agent conflicts → Baton Protocol resolution

---

## Infrastructure

| Component | Location | Open-Source? |
|---|---|---|
| Hermes Dashboard | Port 9119 | ✅ Yes (Nous Research) |
| Rats Agentic OS | **Port 9100** (NEW) | ✅ Built by us |
| Gateway Logs | Port 3142 | ✅ Built by us |
| OpenClaw Gateway | Dynamic port | ✅ Yes |
| Obsidian Vault | ~/openclaw-vault/ | ✅ Yes |
| NotebookLM | Google (free tier) | ✅ Free |

---

## Build Order

1. **Phase 1** — Static HTML/CSS/JS dashboard shell (this session ✅)
2. **Phase 2** — Connect to live data (Hermes status, pipeline state, OpenRouter costs)
3. **Phase 3** — Tab system with real agent switching
4. **Phase 4** — Self-improvement loop integration (Memory Dreaming, Pipeline triggers)
5. **Phase 5** — ZZZ visual identity + Open Design polish