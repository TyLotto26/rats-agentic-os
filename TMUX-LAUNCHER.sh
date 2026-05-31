#!/bin/bash
# TMUX-LAUNCHER.sh — Start Pi as the persistent Rats OS wrapper in tmux
# Creates or attaches to the 'agentic-os' tmux session with Pi loaded
# with the Rats OS system prompt.

set -e

SESSION_NAME="agentic-os"
OS_PROMPT="$HOME/rats-agentic-os/PI-OS-PROMPT.md"

case "${1:-}" in
  --kill)
    echo "🛑 Killing tmux session: $SESSION_NAME"
    tmux kill-session -t "$SESSION_NAME" 2>/dev/null && echo "Done." || echo "No session to kill."
    exit 0
    ;;
  --detach)
    DETACH="-d"
    ;;
  *)
    DETACH=""
    ;;
esac

# Check if session already exists
if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
  echo "📡 Session '$SESSION_NAME' already exists."
  if [ -z "$DETACH" ]; then
    echo "→ Attaching..."
    tmux attach-session -t "$SESSION_NAME"
  else
    echo "→ Already running (detached mode)."
    tmux list-sessions | grep "$SESSION_NAME"
  fi
  exit 0
fi

echo "🚀 Starting Pi as Rats OS wrapper in tmux session: $SESSION_NAME"
echo "   Prompt: $OS_PROMPT"
echo ""

# Create the tmux session with Pi running with our OS system prompt
tmux new-session $DETACH -s "$SESSION_NAME" -n "pi-os" \
  "pi --provider openrouter --model deepseek/deepseek-chat --system-prompt \"\$(cat $OS_PROMPT)\" --session rats-os-persistent 2>&1 | tee \"$HOME/rats-agentic-os/pi-os-session.log\""

if [ -z "$DETACH" ]; then
  echo "✅ Session created and attached."
else
  echo "✅ Session created (detached)."
  echo ""
  echo "Commands:"
  echo "  tmux attach -t $SESSION_NAME    # Attach to Pi"
  echo "  tmux detach                     # Detach (Ctrl+B, D)"
  echo "  bash ~/rats-agentic-os/TMUX-LAUNCHER.sh --kill  # Stop session"
fi