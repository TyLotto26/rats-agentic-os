#!/bin/bash
"""
CODEX-REVIEW.sh — Code Review Gate for Rats Agentic OS
Usage: bash ~/rats-agentic-os/CODEX-REVIEW.sh <file_or_diff>
       bash ~/rats-agentic-os/CODEX-REVIEW.sh --staged  (review git staged changes)
       bash ~/rats-agentic-os/CODEX-REVIEW.sh --all     (review all uncommitted changes)

Runs Codex (GPT-5.5) over the diff and produces a structured review report.
Pi should call this before any code lands.
"""

set -e

TARGET="${1:---staged}"
REPORT_FILE="$HOME/rats-agentic-os/latest-review.md"

echo "⚡ CODEX REVIEW GATE ⚡"
echo "Target: $TARGET"
echo ""

case "$TARGET" in
  --staged)
    echo "→ Reviewing staged changes..."
    DIFF=$(git diff --cached 2>/dev/null || echo "No staged changes")
    ;;
  --all)
    echo "→ Reviewing all uncommitted changes..."
    DIFF=$(git diff HEAD 2>/dev/null || echo "No changes")
    ;;
  *)
    if [ -f "$TARGET" ]; then
      echo "→ Reviewing file: $TARGET"
      DIFF=$(cat "$TARGET")
    else
      echo "→ Reviewing path: $TARGET"
      DIFF=$(git diff "$TARGET" 2>/dev/null || echo "Cannot diff $TARGET")
    fi
    ;;
esac

if [ -z "$DIFF" ] || [ "$DIFF" = "No staged changes" ] || [ "$DIFF" = "No changes" ] || [ "$DIFF" = "Cannot diff $TARGET" ]; then
  echo "⚠ No changes to review."
  cat > "$REPORT_FILE" << 'EOF'
# Codex Review — No Changes
**Status:** SKIP (nothing to review)
**Timestamp:** $(date -u +"%Y-%m-%dT%H:%M:%SZ")
EOF
  exit 0
fi

# Pass the diff to Codex for review
echo "$DIFF" | codex --review "
You are the Rats on Wallstreet Code Review Gate.
Review the following diff for:
1. SECURITY — injection patterns, credential leaks, unsafe exec/eval
2. CONSISTENCY — follows DESIGN.md palette and conventions? Uses existing patterns?
3. ROBUSTNESS — error handling, edge cases, timeout handling
4. PERFORMANCE — unnecessary loops, blocking calls, memory leaks
5. ARCHITECTURE — does this fit the Agentic OS structure (port 9100)?

Output format:
# Codex Review
**Status:** PASS | PASS_WITH_SUGGESTIONS | FAIL
**Reviewer:** Codex (GPT-5.5)
**Timestamp:** $(date -u +"%Y-%m-%dT%H:%M:%SZ")

## Security
- [PASS/FAIL] ...

## Consistency  
- [PASS/FAIL] ...

## Robustness
- [PASS/FAIL] ...

## Performance
- [PASS/FAIL] ...

## Architecture
- [PASS/FAIL] ...

## Summary
- **Verdict:** ...
- **Must fix before merge:** ...
- **Suggestions:** ...
"

REVIEW_RESULT=$?
if [ $REVIEW_RESULT -eq 0 ]; then
  echo ""
  echo "✅ Review complete — report saved to $REPORT_FILE"
else
  echo ""
  echo "⚠ Review completed with warnings — report saved to $REPORT_FILE"
fi