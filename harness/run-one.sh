#!/usr/bin/env bash
# Usage: run-one.sh <task_id> <cell> <seed>
# e.g.   run-one.sh T1 B-v1 1
#
# Assumes run-all.sh has already swapped out ~/.claude/CLAUDE.md.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HARNESS="$REPO_ROOT/harness"
TASK_ID="$1"
CELL="$2"
SEED="$3"
RUN_ID="${TASK_ID}__${CELL}__seed${SEED}"
RUN_DIR="$HARNESS/runs/$RUN_ID"

TASK_DIR="$HARNESS/tasks/$TASK_ID"
CELL_DIR="$HARNESS/cells/$CELL"

rm -rf "$RUN_DIR"
mkdir -p "$RUN_DIR/repo"
cp -R "$TASK_DIR/repo/." "$RUN_DIR/repo/"

if [ -f "$CELL_DIR/CLAUDE.md" ]; then
  cp "$CELL_DIR/CLAUDE.md" "$RUN_DIR/repo/CLAUDE.md"
fi

(
  cd "$RUN_DIR/repo"
  git init -q
  git add -A
  GIT_COMMITTER_NAME=h GIT_COMMITTER_EMAIL=h@h GIT_AUTHOR_NAME=h GIT_AUTHOR_EMAIL=h@h \
    git commit -q -m baseline
)

PROMPT=$(cat "$TASK_DIR/prompt.txt")

cd "$RUN_DIR/repo"

set +e
echo "$PROMPT" | claude -p \
  --model claude-opus-4-7 \
  --effort medium \
  --max-budget-usd 2.00 \
  --output-format stream-json \
  --verbose \
  --disable-slash-commands \
  --disallowed-tools "WebSearch,WebFetch,Task,Skill" \
  --permission-mode bypassPermissions \
  --no-session-persistence \
  --setting-sources project,local \
  > "$RUN_DIR/transcript.jsonl" 2> "$RUN_DIR/stderr.log"
EXIT=$?
set -e

(
  cd "$RUN_DIR/repo"
  git add -A
  git diff --cached > "$RUN_DIR/diff.patch"
  git diff --cached --numstat > "$RUN_DIR/numstat.txt"
)

LINES_ADDED=$(awk '{a+=$1} END {print a+0}' "$RUN_DIR/numstat.txt")
LINES_REMOVED=$(awk '{r+=$2} END {print r+0}' "$RUN_DIR/numstat.txt")
FILES_MODIFIED=$(wc -l < "$RUN_DIR/numstat.txt" | tr -d ' ')

cat > "$RUN_DIR/metrics.json" <<EOF
{
  "run_id": "$RUN_ID",
  "task_id": "$TASK_ID",
  "cell": "$CELL",
  "seed": $SEED,
  "exit_code": $EXIT,
  "lines_added": $LINES_ADDED,
  "lines_removed": $LINES_REMOVED,
  "files_modified": $FILES_MODIFIED
}
EOF

printf "[run-one] %-32s  exit=%s  +%s -%s  files=%s\n" "$RUN_ID" "$EXIT" "$LINES_ADDED" "$LINES_REMOVED" "$FILES_MODIFIED"
