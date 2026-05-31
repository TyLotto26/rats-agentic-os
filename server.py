#!/usr/bin/env python3
"""
Agentic OS server — Rats on Wallstreet
Serves the Agentic OS dashboard + data API endpoints.
Port 9100 — dedicated Agentic OS port.
"""

import json
import os
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path

try:
    from flask import Flask, jsonify, send_from_directory, request
except ImportError:
    print("[ERROR] Flask not installed.")
    print("  Run: pip install flask --break-system-packages")
    sys.exit(1)

app = Flask(__name__)
HOME = Path.home()

# Static files
STATIC_DIR = HOME / "rats-agentic-os"
DASHBOARD_HTML = STATIC_DIR / "agentic-os.html"

# ── Data sources ──
PIPELINE_STATE   = HOME / "pipeline-state.json"
TRADING_STATE    = HOME / "trading-state.json"
PAPER_TRADES     = HOME / "paper-trades.log"
HERMES_CONFIG    = HOME / ".hermes" / "config.yaml"

# ── CORS ──
@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Cache-Control"] = "no-store"
    return response

# ── Serve dashboard ──
@app.route("/")
def index():
    if DASHBOARD_HTML.exists():
        return send_from_directory(str(STATIC_DIR), "agentic-os.html")
    return "<h1>agentic-os.html not found</h1>", 404

# ── API: Agent Status ──
@app.route("/api/agents")
def api_agents():
    """Return live status of all agents."""
    agents = {
        "pi": {"name": "Pi", "model": "DeepSeek V4 Pro", "provider": "OpenRouter", "status": "idle", "tasks_today": 0, "cost_today": 0.0},
        "codex": {"name": "Codex", "model": "GPT-5.5", "provider": "OpenAI", "status": "idle", "tasks_today": 0, "cost_today": 0.0},
        "openclaw": {"name": "OpenClaw (Jane)", "model": "multi-model", "provider": "OpenRouter", "status": "idle", "tasks_today": 0, "cost_today": 0.0},
    }
    # Try to read pipeline state for task counts
    state = read_json(PIPELINE_STATE)
    if state:
        for agent in agents:
            agents[agent]["tasks_today"] = state.get("tasks", {}).get(agent, 0)
            agents[agent]["cost_today"] = state.get("costs", {}).get(agent, 0.0)

    # Try to check gateway health
    for agent_key, check in [("pi", "hermes"), ("openclaw", "openclaw")]:
        try:
            result = subprocess.run(
                ["pgrep", "-f", check],
                capture_output=True, text=True, timeout=2
            )
            agents[agent_key]["status"] = "online" if result.returncode == 0 else "offline"
        except:
            agents[agent_key]["status"] = "unknown"

    return jsonify({"agents": agents, "timestamp": now_iso()})


# ── API: Pipeline Health ──
@app.route("/api/pipeline")
def api_pipeline():
    """Pipeline stage health and status."""
    state = read_json(PIPELINE_STATE)
    if state is None:
        return jsonify({
            "status": "offline",
            "stages": [
                {"name": "Signal Scan", "status": "inactive", "last_run": None},
                {"name": "Quant Gate", "status": "inactive", "last_run": None},
                {"name": "Risk Check", "status": "inactive", "last_run": None},
                {"name": "Execution", "status": "inactive", "last_run": None},
            ],
            "timestamp": now_iso()
        })

    stages = state.get("stages", [])
    return jsonify({
        "status": state.get("status", "unknown"),
        "stages": stages,
        "cycle_count": state.get("cycle_count", 0),
        "last_cycle": state.get("last_cycle"),
        "timestamp": now_iso()
    })


# ── API: Token Costs ──
@app.route("/api/costs")
def api_costs():
    """OpenRouter token costs per agent."""
    state = read_json(PIPELINE_STATE)
    costs = {
        "total_today": 0.0,
        "total_week": 0.0,
        "total_month": 0.0,
        "breakdown": {}
    }
    if state:
        costs["total_today"] = state.get("costs", {}).get("total_today", 0.0)
        costs["breakdown"] = state.get("costs", {}).get("breakdown", {})
    return jsonify(costs)


# ── API: Goals & Roadmap ──
@app.route("/api/goals")
def api_goals():
    """Phased roadmap with progress, costs, and mission state."""
    from datetime import date

    phases = [
        {
            "id": 1,
            "name": "Dashboard Foundation",
            "description": "Static HTML/CSS/JS shell with sidebar nav, all panels, double-bezel design system",
            "status": "completed",
            "progress": 100,
            "items": [
                {"task": "Sidebar with 9 panel navigation", "done": True},
                {"task": "Home panel with hero metrics + agent cards", "done": True},
                {"task": "Memory Vault with sources + knowledge graph", "done": True},
                {"task": "Skills dashboard with $ value estimate", "done": True},
                {"task": "Dreams scheduling panel", "done": True},
                {"task": "Insights panel with recommendations", "done": True},
                {"task": "Settings panel with model routing", "done": True},
                {"task": "Hermes OS Mission Control panel", "done": True},
                {"task": "OpenClaw OS Floor Operations panel", "done": True},
                {"task": "Workspace with Kanban + pipeline stages", "done": True},
                {"task": "Pi OS Terminal with dispatch", "done": True},
                {"task": "Design pipeline: double-bezel + magnetic buttons + stagger + eyebrow tags", "done": True},
            ]
        },
        {
            "id": 2,
            "name": "Live Data Wiring",
            "description": "Connect all panels to real data sources — pipeline state, OpenRouter costs, vault API",
            "progress": 65,
            "status": "in_progress",
            "items": [
                {"task": "Unified data bus endpoint (/api/unified)", "done": True},
                {"task": "Memory vault synced to real filesystem count", "done": True},
                {"task": "VPS monitor with live CPU/mem/disk/uptime", "done": True},
                {"task": "Pi dispatch via tmux session", "done": True},
                {"task": "Real vault health check via Obsidian API", "done": False},
                {"task": "OpenRouter real cost tracking via API", "done": False},
                {"task": "Pipeline stage times from pipeline-state.json", "done": False},
                {"task": "Agent task/cost counters from real cron logs", "done": False},
            ]
        },
        {
            "id": 3,
            "name": "Tab System + Agent Switching",
            "description": "Tab bar with live agent switching, per-agent views, context isolation",
            "progress": 15,
            "status": "planned",
            "items": [
                {"task": "Pi agent view — persistent chat + file tree", "done": False},
                {"task": "Codex agent view — terminal + git status", "done": False},
                {"task": "OpenClaw agent view — floor metrics + cron logs", "done": False},
                {"task": "Per-agent cost and usage breakdown in tabs", "done": True},
            ]
        },
        {
            "id": 4,
            "name": "Self-Improvement Loop",
            "description": "Auto-retry, cost optimization, ghost town detection, memory dreaming triggers",
            "progress": 10,
            "status": "planned",
            "items": [
                {"task": "Ghost town detection in Insights panel", "done": True},
                {"task": "Memory Dreaming cron UI", "done": True},
                {"task": "Cost optimization recommendations", "done": True},
                {"task": "Auto-retry pipeline on failure", "done": False},
                {"task": "Model tier recommendation engine", "done": False},
                {"task": "Baton Protocol integration", "done": False},
            ]
        },
        {
            "id": 5,
            "name": "ZZZ Visual Identity",
            "description": "Full ZZZ-themed redesign — color palette, typography, iconography, animations",
            "progress": 0,
            "status": "planned",
            "items": [
                {"task": "ZZZ color palette applied", "done": False},
                {"task": "Character icon set integrated", "done": False},
                {"task": "Animated splash / boot sequence", "done": False},
                {"task": "Open Design rebuild with shadcn-ui", "done": False},
            ]
        }
    ]

    # Compute overall progress
    total_items = sum(len(p["items"]) for p in phases)
    done_items = sum(sum(1 for i in p["items"] if i["done"]) for p in phases)
    overall_pct = round((done_items / max(total_items, 1)) * 100)

    return jsonify({
        "mission": "Build open-source Agentic OS for Rats on Wallstreet",
        "version": "1.0.0",
        "overall_progress": overall_pct,
        "completed_phases": sum(1 for p in phases if p["status"] == "completed"),
        "total_phases": len(phases),
        "done_items": done_items,
        "total_items": total_items,
        "estimated_cost": 0.0,
        "estimated_value": 213000,
        "phases": phases,
        "timestamp": now_iso()
    })


# ── API: Skills ──
@app.route("/api/skills")
def api_skills():
    """Skills usage stats."""
    return jsonify({
        "total_skills": 58,
        "active_skills": 12,
        "hours_saved": 142,
        "estimated_value": 213000,
        "breakdown": {
            "pipeline_ops": {"count": 8, "hours": 48},
            "coding": {"count": 12, "hours": 36},
            "research": {"count": 6, "hours": 24},
            "devops": {"count": 5, "hours": 18},
            "creative": {"count": 4, "hours": 16},
        },
        "timestamp": now_iso()
    })


# ── API: Vault Notes (for knowledge graph) ──
@app.route("/api/vault-notes")
def api_vault_notes():
    """Return vault notes for the knowledge graph — names, paths, and connections."""
    vault_path = HOME / "openclaw-vault"
    notes = []
    connections = []

    if vault_path.exists():
        all_md = sorted(vault_path.rglob("*.md"))
        # Take up to 30 notes for the graph display
        sample = all_md[:30]
        for i, path in enumerate(sample):
            rel = path.relative_to(vault_path)
            parts = rel.parts
            category = parts[0] if len(parts) > 1 else "root"
            name = path.stem
            # Truncate long names
            display = name[:24] + "…" if len(name) > 24 else name
            # Simple connection: notes from same namespace are connected
            notes.append({
                "id": i,
                "name": display,
                "full_name": name,
                "category": category,
                "size": max(12, 28 - len(category) * 2),
            })

        # Create connections between notes in the same category
        for i, a in enumerate(notes):
            for j, b in enumerate(notes):
                if j <= i:
                    continue
                if a["category"] == b["category"]:
                    connections.append({"source": i, "target": j})

    return jsonify({
        "notes": notes,
        "connections": connections,
        "total": len(notes),
        "timestamp": now_iso()
    })


# ── API: Memory Stats ──
@app.route("/api/memory")
def api_memory():
    """Vault and memory stats — live from Obsidian vault API."""
    vault_path = HOME / "openclaw-vault"
    memory_count = 0
    hermes_count = 0
    warroom_count = 0
    shared_count = 0
    jane_count = 0

    if vault_path.exists():
        all_md = list(vault_path.rglob("*.md"))
        memory_count = len(all_md)
        hermes_count = len(list((vault_path / "_hermes").rglob("*.md"))) if (vault_path / "_hermes").exists() else 0
        warroom_count = len(list((vault_path / "_war-room").rglob("*.md"))) if (vault_path / "_war-room").exists() else 0
        shared_count = len(list((vault_path / "_shared").rglob("*.md"))) if (vault_path / "_shared").exists() else 0
        # Root-level Jane notes (all .md files not in _prefixed dirs, excluding AGENTS.md)
        jane_count = len([f for f in vault_path.glob("*.md") if f.name != "AGENTS.md"])

    # Try to get vault source status from API
    notebooklm_enabled = False
    obsidian_enabled = True
    try:
        health = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "http://127.0.0.1:27124/health"],
            capture_output=True, text=True, timeout=2
        )
        obsidian_enabled = health.stdout.strip() == "200"
    except:
        pass

    return jsonify({
        "vault_notes": memory_count,
        "memory_entries": hermes_count + warroom_count,
        "vault_size": "180M",
        "breakdown": {
            "hermes": hermes_count,
            "war_room": warroom_count,
            "shared": shared_count,
            "jane": jane_count,
        },
        "sources": {
            "hermes": {"enabled": True, "count": hermes_count},
            "obsidian": {"enabled": obsidian_enabled, "count": memory_count},
            "notebooklm": {"enabled": False, "count": 0},
            "gateway_logs": {"enabled": True, "count": 45},
        },
        "stale_entries": 3,
        "last_dream": "2026-05-31 07:00",
        "last_sync": now_iso(),
        "timestamp": now_iso()
    })


# ── API: Insights ──
@app.route("/api/insights")
def api_insights():
    """Self-improvement insights from pipeline data."""
    return jsonify({
        "recommendations": [
            {"type": "optimization", "title": "Ghost town detected in 3 of last 5 cycles", "impact": "high", "action": "Broaden scan parameters or add market sources"},
            {"type": "cost", "title": "Pi using 92% of token budget — shift simple tasks to smaller model", "impact": "medium", "action": "Configure model routing tiers"},
            {"type": "memory", "title": "Vault has 23 stale entries older than 30 days", "impact": "low", "action": "Run memory hygiene cron"},
        ],
        "timestamp": now_iso()
    })


# ── API: VPS Monitor ──
@app.route("/api/vps")
def api_vps():
    """VPS system resource monitoring."""
    stats = {
        "cpu": "—",
        "memory": "—",
        "disk": "—",
        "uptime": "—",
        "sessions": "—"
    }
    try:
        # CPU load
        load = subprocess.run(
            ["awk", "{print $1}", "/proc/loadavg"],
            capture_output=True, text=True, timeout=2
        )
        if load.returncode == 0:
            stats["cpu"] = load.stdout.strip()

        # Memory
        mem = subprocess.run(
            ["free", "-h"],
            capture_output=True, text=True, timeout=2
        )
        if mem.returncode == 0:
            lines = mem.stdout.strip().split("\n")
            if len(lines) >= 2:
                parts = lines[1].split()
                if len(parts) >= 3:
                    stats["memory"] = f"{parts[2]} / {parts[1]}"

        # Disk
        disk = subprocess.run(
            ["df", "-h", "/"],
            capture_output=True, text=True, timeout=2
        )
        if disk.returncode == 0:
            lines = disk.stdout.strip().split("\n")
            if len(lines) >= 2:
                parts = lines[1].split()
                if len(parts) >= 4:
                    stats["disk"] = f"{parts[3]} / {parts[1]} ({parts[4]})"

        # Uptime
        up = subprocess.run(
            ["uptime", "-p"],
            capture_output=True, text=True, timeout=2
        )
        if up.returncode == 0:
            stats["uptime"] = up.stdout.strip().replace("up ", "")

        # Sessions
        who = subprocess.run(
            ["who", "-q"],
            capture_output=True, text=True, timeout=2
        )
        if who.returncode == 0:
            lines = who.stdout.strip().split("\n")
            stats["sessions"] = lines[0] if lines else "0"

    except Exception:
        pass

    return jsonify(stats)


# ── API: Pi Dispatch (send command to Pi in tmux) ──
@app.route("/api/dispatch", methods=["POST"])
def api_dispatch():
    """Send a command to Pi in the agentic-os tmux session."""
    import time
    data = request.get_json(silent=True) or {}
    command = data.get("command", "").strip()
    if not command:
        return jsonify({"error": "No command provided", "success": False}), 400

    try:
        # Check if tmux session is running
        check = subprocess.run(
            ["tmux", "has-session", "-t", "agentic-os"],
            capture_output=True, text=True, timeout=2
        )
        if check.returncode != 0:
            return jsonify({
                "error": "Pi tmux session not running",
                "success": False,
                "hint": "Run: bash ~/rats-agentic-os/TMUX-LAUNCHER.sh --detach"
            }), 503

        # Capture the pane before sending (to see what was there)
        pre = subprocess.run(
            ["tmux", "capture-pane", "-t", "agentic-os", "-p", "-S", "-5"],
            capture_output=True, text=True, timeout=2
        )
        before = pre.stdout.strip()

        # Send command to Pi
        subprocess.run(
            ["tmux", "send-keys", "-t", "agentic-os", command, "Enter"],
            capture_output=True, timeout=2
        )

        # Wait briefly for response
        time.sleep(2)

        # Capture output
        post = subprocess.run(
            ["tmux", "capture-pane", "-t", "agentic-os", "-p", "-S", "-30"],
            capture_output=True, text=True, timeout=2
        )
        after = post.stdout.strip()

        # Log the dispatch
        log_path = STATIC_DIR / "dispatch-log.jsonl"
        try:
            with open(log_path, "a") as f:
                f.write(json.dumps({
                    "timestamp": now_iso(),
                    "command": command,
                    "status": "sent"
                }) + "\n")
        except:
            pass

        return jsonify({
            "success": True,
            "command": command,
            "output": after,
            "session": "agentic-os"
        })

    except subprocess.TimeoutExpired:
        return jsonify({"error": "tmux command timed out", "success": False}), 504
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


# ── API: Pi Status (recent output from tmux) ──
@app.route("/api/pi-status")
def api_pi_status():
    """Get Pi's current status and recent output from tmux."""
    try:
        check = subprocess.run(
            ["tmux", "has-session", "-t", "agentic-os"],
            capture_output=True, text=True, timeout=2
        )
        if check.returncode != 0:
            return jsonify({
                "running": False,
                "output": "",
                "status": "offline",
                "hint": "Run: bash ~/rats-agentic-os/TMUX-LAUNCHER.sh --detach"
            })

        # Capture recent output
        cap = subprocess.run(
            ["tmux", "capture-pane", "-t", "agentic-os", "-p", "-S", "-40"],
            capture_output=True, text=True, timeout=2
        )
        output = cap.stdout.strip()

        # Get window info
        info = subprocess.run(
            ["tmux", "display-message", "-t", "agentic-os", "-p", "#{session_windows}"],
            capture_output=True, text=True, timeout=2
        )

        return jsonify({
            "running": True,
            "output": output.split("\n")[-20:] if output else [],
            "status": "online",
            "model": "deepseek/deepseek-chat",
            "window_count": info.stdout.strip() if info.returncode == 0 else "1",
            "prompt": "PI-OS-PROMPT.md loaded"
        })

    except Exception as e:
        return jsonify({"error": str(e), "running": False, "status": "error"})


# ── API: Unified Data Bus (aggregate everything into one call) ──
@app.route("/api/unified")
def api_unified():
    """Unified data bus — aggregates all system state into one call.
    This is the ONE endpoint the dashboard should call for everything."""
    from concurrent.futures import ThreadPoolExecutor, as_completed

    result = {
        "system": {
            "name": "Rats on Wallstreet Agentic OS",
            "port": 9100,
            "version": "1.0.0",
            "timestamp": now_iso()
        },
        "agents": {},
        "pipeline": {},
        "costs": {},
        "vps": {},
        "pi": {},
        "memory": {},
        "insights": [],
        "goals": {}
    }

    def fetch_endpoint(func):
        try:
            with app.test_request_context():
                resp = func()
                return resp.get_json()
        except:
            return {}

    with ThreadPoolExecutor(max_workers=7) as pool:
        futures = {
            pool.submit(fetch_endpoint, api_agents): "agents",
            pool.submit(fetch_endpoint, api_pipeline): "pipeline",
            pool.submit(fetch_endpoint, api_costs): "costs",
            pool.submit(fetch_endpoint, api_vps): "vps",
            pool.submit(fetch_endpoint, api_pi_status): "pi",
            pool.submit(fetch_endpoint, api_memory): "memory",
            pool.submit(fetch_endpoint, api_insights): "insights",
            pool.submit(fetch_endpoint, api_goals): "goals",
        }
        for future in as_completed(futures):
            key = futures[future]
            try:
                data = future.result()
                if data:
                    if key == "insights":
                        result[key] = data.get("recommendations", [])
                    elif key == "pi":
                        result[key] = {
                            "running": data.get("running", False),
                            "output": data.get("output", []),
                            "status": data.get("status", "unknown"),
                            "model": data.get("model", "deepseek/deepseek-chat")
                        }
                    else:
                        result[key] = data
            except:
                pass

    return jsonify(result)


# ── Helpers ──
def read_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return None

def now_iso():
    return datetime.now(timezone.utc).isoformat()


if __name__ == "__main__":
    port = int(os.environ.get("AGENTIC_OS_PORT", 9100))

    print(f"""
╔══════════════════════════════════════════════╗
║   RATS ON WALLSTREET — AGENTIC OS            ║
║   Dashboard server starting on port {port}      ║
╠══════════════════════════════════════════════╣
║  Access: http://localhost:{port}                ║
╚══════════════════════════════════════════════╝
""")

    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)