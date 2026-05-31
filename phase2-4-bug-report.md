# Phase 2–4 Bug Report — Agentic OS Dashboard

**Reviewed:** `agentic-os.html`, `server.py`  
**Scope:** Phase 2 (live data), Phase 3 (tab system + agent views), Phase 4 (self-improvement loop wiring)  
**Method:** Static code review + live API probes against running server on port 9100

---

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| High     | 3 |
| Medium   | 12 |
| Low      | 7 |

No confirmed JS runtime crashes in the happy path (live pipeline, OpenRouter key present, unified bus OK). Several logic bugs, stale UI wiring, and missing guards will cause wrong data, silent failures, or broken Phase 3 tab UX.

---

## High

### 1. Dual active panels — agent view stacked with Home on load

| | |
|---|---|
| **File:Line** | `agentic-os.html:1183`, `agentic-os.html:1294` |
| **Severity** | High |
| **Category** | Agent view panel / layout |

Both `#panel-agent-view` and `#panel-home` have `class="panel active"`. CSS (`.panel.active { display: block }`) renders **both** panels simultaneously on first load.

**Impact:** Agent view content appears above the Home dashboard instead of replacing it. Confusing layout; undermines Phase 3 tab design.

**Fix:** Remove `active` from `#panel-agent-view` and integrate agent views into Home (or make agent view the sole default active panel). Only one `.panel` should be `active` at a time.

---

### 2. Tab bar switches hidden panel after sidebar navigation

| | |
|---|---|
| **File:Line** | `agentic-os.html:1183`, `agentic-os.html:2057–2064`, `agentic-os.html:2087–2090` |
| **Severity** | High |
| **Category** | Tab system / agent switching |

Tab clicks toggle `.agent-view-panel` elements inside `#panel-agent-view`, but sidebar nav deactivates `#panel-agent-view` when any other panel is selected. After clicking Home (or any nav item), tab switches update DOM that is `display: none`.

**Impact:** Phase 3 “live agent switching” appears broken whenever the user uses sidebar navigation (the normal flow).

**Fix:** Either (a) move agent views into `#panel-home` below the tab bar, or (b) on tab click also activate `#panel-agent-view` and deactivate other panels, or (c) drop the separate `#panel-agent-view` wrapper entirely.

---

### 3. `loadOpenclawView` — falsy `cycle` check + missing `stages` guard

| | |
|---|---|
| **File:Line** | `agentic-os.html:2340–2348` |
| **Severity** | High |
| **Category** | Pipeline live parsing |

```javascript
if (pipe.cycle) {
  cronLog.innerHTML = pipe.stages.map(s => ...
} else {
  cronLog.innerHTML = 'Pipeline offline';
}
```

**Issues:**
1. `cycle === 0` is falsy in JS → valid “no cycles yet” state shows **“Pipeline offline”** even when `stages` array is present (`server.py:99` returns `cycle: 0` on missing state).
2. No `Array.isArray(pipe.stages)` check → if response omits `stages`, `.map` throws **TypeError** and falls through to generic catch message.

**Fix:**
```javascript
if (pipe.status === 'offline' || !Array.isArray(pipe.stages)) {
  cronLog.innerHTML = '<div style="color:var(--orange);">Pipeline offline</div>';
} else {
  cronLog.innerHTML = pipe.stages.map(/* ... */).join('') + /* footer using pipe.cycle ?? 0 */;
}
```

---

## Medium

### 4. Hardcoded OpenRouter balance flash before live data

| | |
|---|---|
| **File:Line** | `agentic-os.html:2212–2213`, `agentic-os.html:2266–2278` |
| **Severity** | Medium |
| **Category** | OpenRouter wiring |

`loadAll()` sets `#openrouterCost` to `'$30.00 left'` unconditionally, then overwrites only if `data.openrouter.remaining !== undefined`. When OpenRouter API fails, the error payload still includes `remaining: 0` (`server.py:142`, `server.py:162`), so UI shows **$0.00 left** instead of an error — or **$30.00** if unified bus omits openrouter entirely.

**Fix:** Remove the hardcoded `$30.00`. Gate on `data.openrouter.error`; show `'—'` or `'API error'` when missing/invalid.

---

### 5. OpenRouter endpoint — weak error handling

| | |
|---|---|
| **File:Line** | `server.py:144–162`, `server.py:181–186` |
| **Severity** | Medium |
| **Category** | OpenRouter API |

`api_openrouter` and `api_costs`:
- Do not check `subprocess` return code or empty `stdout`.
- `json.loads(result.stdout)` on non-JSON curl failures → caught generically.
- OpenRouter error JSON (`{"error": {...}}`) parses successfully but yields `data: {}` → silent zero balances.
- Error schema inconsistent: uses `credits` key on error (`server.py:142`) vs `total_credits` on success (`server.py:155`).

**Fix:** Check `result.returncode`, validate JSON, detect top-level `"error"`, return `{ "error": "...", "ok": false }` with HTTP 502; align response schema.

---

### 6. `dispatchToPi` — literal `\n` in output strings

| | |
|---|---|
| **File:Line** | `agentic-os.html:2122`, `agentic-os.html:2131` |
| **Severity** | Medium |
| **Category** | Agent view / Pi dispatch |

Uses `'\\n'` (backslash + n) instead of `'\n'`. UI shows `\nWaiting for response...` as literal text in `#piChatLog`.

**Fix:** Replace `'\\n'` with `'\n'` (match `sendCommand` at `agentic-os.html:2148`).

---

### 7. `#totalTasks` shows agent count, not tasks

| | |
|---|---|
| **File:Line** | `agentic-os.html:2208–2209` |
| **Severity** | Medium |
| **Category** | Live data wiring |

```javascript
Object.keys(data.agents.agents).length  // always 3
```

Header **TASKS** displays number of agent keys (3), not `tasks_today` from `/api/agents`.

**Fix:** Sum `tasks_today` across agents, or use pipeline `cycle` / dedicated task counter from API.

---

### 8. `loadCodexView` — wrong data source for “Git Status”

| | |
|---|---|
| **File:Line** | `agentic-os.html:2317–2327` |
| **Severity** | Medium |
| **Category** | Codex agent view |

Phase 3 item claims “terminal + git status”, but `loadCodexView()` fetches `/api/vps` and renders CPU/memory/disk/uptime in `#codexGitStatus`. No git integration exists.

**Fix:** Add `/api/git-status` (or dispatch via Pi) and populate `#codexGitStatus` with real `git status` output; move VPS metrics elsewhere or reuse unified `data.vps`.

---

### 9. Insights panel — unsanitized `innerHTML`

| | |
|---|---|
| **File:Line** | `agentic-os.html:2232–2235` |
| **Severity** | Medium |
| **Category** | XSS / data rendering |

Recommendation `title` and `action` from `/api/insights` are interpolated into `innerHTML` without escaping. Pipeline-derived strings (bankroll, cycle timestamps) flow into titles server-side.

**Fix:** Use `textContent` / DOM APIs, or an escape helper, before inserting API strings.

---

### 10. Tab handler — no null guard on header elements

| | |
|---|---|
| **File:Line** | `agentic-os.html:2074–2084` |
| **Severity** | Medium |
| **Category** | Agent view panel / DOM refs |

```javascript
nameEl.textContent = maps[tabName].name;
modelEl.textContent = maps[tabName].model;
```

If `#activeAgentName` or `#activeAgentModel` were removed/renamed, tab click throws **TypeError**. Elements exist today; guard is missing for robustness.

**Fix:** `if (nameEl) nameEl.textContent = ...` (same for `modelEl`).

---

### 11. `api_costs` — fabricated daily/weekly metrics

| | |
|---|---|
| **File:Line** | `server.py:194–196`, `server.py:199–201` |
| **Severity** | Medium |
| **Category** | OpenRouter / live data |

`total_today = used * 0.01`, `total_week = used * 0.05`, breakdown splits `used * 0.6/0.3/0.1`. These are arbitrary fractions of **lifetime** usage, not real daily costs. Dashboard hero cards and `#piViewCost` label them as “today”.

**Fix:** Use OpenRouter activity/usage endpoints if available, or label honestly as “estimated” / hide until real daily data exists.

---

### 12. `api_insights` — hardcoded cycle in action text

| | |
|---|---|
| **File:Line** | `server.py:481–483` |
| **Severity** | Medium |
| **Category** | Self-improvement / pipeline |

```python
"action": "Cycle 267 reached. Self-improvement loop running nominally."
```

Always says cycle 267 regardless of `state.get("cycle")` used elsewhere in the same function.

**Fix:** `f"Cycle {state.get('cycle', 0)} reached..."`.

---

### 13. `api_insights` — OpenRouter curl missing timeout

| | |
|---|---|
| **File:Line** | `server.py:461–464` |
| **Severity** | Medium |
| **Category** | OpenRouter API |

Unlike `api_openrouter` (`timeout=5`), insights OR call has **no timeout**. Slow/hung OpenRouter can block the insights endpoint (and unified bus worker).

**Fix:** Add `timeout=5` to match other OR calls.

---

### 14. `renderGoals` — incomplete goals endpoint wiring

| | |
|---|---|
| **File:Line** | `agentic-os.html:2357–2366`, `agentic-os.html:1508` |
| **Severity** | Medium |
| **Category** | Goals endpoint |

`renderGoals()` updates `#goalDone`, `#goalTotal`, `#goalPhases` but **never** updates `#goalTotalPhases` from API `total_phases`. DOM refs (`#goalMission`, `#goalBar`, etc.) are used without null checks — throws if Goals panel markup changes.

Also `#missionStatus` (`agentic-os.html:1136`) stays **“Phase 1 active”** while API reports phases 2–4 completed (`server.py:244–284`).

**Fix:** Set `#goalTotalPhases` from `goals.total_phases`; update `#missionStatus` from current in-progress phase; add null guards on all goal DOM refs.

---

### 15. `loadOpenclawView` / `loadCodexView` — no HTTP status check

| | |
|---|---|
| **File:Line** | `agentic-os.html:2321–2322`, `agentic-os.html:2338–2339` |
| **Severity** | Medium |
| **Category** | Agent view loaders |

`fetch()` only rejects on network error, not 4xx/5xx. Error HTML bodies may be passed to `.json()` and produce confusing partial UI.

**Fix:** `if (!res.ok) throw new Error(res.status);` before parsing JSON (same pattern as `fetchJSON`).

---

## Low

### 16. `loadPiView` — chat log stuck on “Loading…” when output empty

| | |
|---|---|
| **File:Line** | `agentic-os.html:2284–2287` |
| **Severity** | Low |
| **Category** | Pi agent view |

Updates `#piChatLog` only when `data.pi.output.length > 0`. Offline session or empty tmux pane leaves initial placeholder forever.

**Fix:** Else branch: show offline hint or “No recent output”.

---

### 17. `loadPiView` — redundant `/api/pi-status` fetch

| | |
|---|---|
| **File:Line** | `agentic-os.html:2301–2303` |
| **Severity** | Low |
| **Category** | Performance |

Unified bus already includes `data.pi` (`server.py:711`, `server.py:724–729`). File tree block re-fetches `/api/pi-status` every 30s refresh.

**Fix:** Reuse `data.pi` for session status; only fetch on demand.

---

### 18. `api_pipeline` — `targets` field `or`-chain treats zero as missing

| | |
|---|---|
| **File:Line** | `server.py:112` |
| **Severity** | Low |
| **Category** | Pipeline parsing |

```python
s.get("targets_count") or s.get("proposal_count") or s.get("executed", 0)
```

Legitimate `0` targets falls through to next field. Observed: Whalewatch returns `targets: 0` when all counts absent (acceptable) but Polyscan with `targets_count: 0` would incorrectly show proposal/executed counts.

**Fix:** Use explicit `is not None` checks instead of `or`.

---

### 19. `api_pipeline` — coarse online/idle status

| | |
|---|---|
| **File:Line** | `server.py:116` |
| **Severity** | Low |
| **Category** | Pipeline parsing |

`status: "online" if state.get("last_cycle_complete") else "idle"` — any truthy timestamp marks online even if pipeline is stale or stages failed.

**Fix:** Derive status from stage statuses + recency of `last_cycle_complete`.

---

### 20. `api_agents` — hardcoded OpenClaw task count

| | |
|---|---|
| **File:Line** | `server.py:80` |
| **Severity** | Low |
| **Category** | Agent status |

`agents["openclaw"]["tasks_today"] = 5  # 5 crons` when pipeline state exists — not read from cron/runtime.

**Fix:** Query `openclaw cron list` or read gateway state for live count.

---

### 21. `api_goals` — unused import

| | |
|---|---|
| **File:Line** | `server.py:216` |
| **Severity** | Low |
| **Category** | Code hygiene |

`from datetime import date` is imported but never used.

**Fix:** Remove unused import.

---

### 22. Agent cost rings never updated from live data

| | |
|---|---|
| **File:Line** | `agentic-os.html:1402–1431`, `agentic-os.html:2185–2280` |
| **Severity** | Low |
| **Category** | Phase 3 per-agent cost breakdown |

`#piRing`, `#codexRingPct`, `#openclawMeterDetail`, etc. remain static HTML placeholders. `loadAll()` / agent loaders do not update them despite Phase 3 “per-agent cost and usage breakdown” marked done in goals.

**Fix:** Wire rings/meters from `data.costs.breakdown` and agent status in `loadAll()` or per-agent loaders.

---

## Verified OK (no bug filed)

| Area | Notes |
|------|-------|
| `loadPiView` DOM refs | `#piChatLog`, `#piViewStatus`, `#piViewCost`, `#piFileTree` all exist in markup |
| Tab → panel ID mapping | `pi` → `#piAgentView`, `codex` → `#codexAgentView`, `openclaw` → `#openclawAgentView` — IDs correct |
| `/api/goals` response shape | Matches `renderGoals()` expectations (`phases`, `overall_progress`, `done_items`, etc.) |
| `/api/pipeline` live parse (server) | Correctly reads `pipeline-state.json` stages, cycle 267, bankroll in live test |
| `/api/openrouter` happy path | Returns `total_credits`, `total_usage`, `remaining`, `pct_used` — consumed by `loadAll()` block |
| Unified bus | Aggregates `goals`, `openrouter`, `insights`, `pi` — keys match frontend usage |

---

## Recommended fix order

1. **Panel / tab architecture** (issues #1, #2) — unblocks Phase 3 UX  
2. **Pipeline parsing guard** (#3) — prevents false offline + potential TypeError  
3. **OpenRouter error handling** (#4, #5) — accurate cost display  
4. **Goals + mission header sync** (#14) — Phase 2–4 roadmap accuracy  
5. **Codex git status** (#8) — complete Phase 3 deliverable  
6. Remaining medium/low items

---

*Generated: 2026-05-31 — code review of uncommitted Phase 2–4 upgrades in `agentic-os.html` + `server.py`*
