#!/usr/bin/env bash
# Runs the 3 cells × N tasks × K seeds matrix via GNU parallel.
# Swaps out ~/.claude/CLAUDE.md for the duration (auto-restored on exit).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HARNESS="$REPO_ROOT/harness"
GLOBAL_MD="$HOME/.claude/CLAUDE.md"
BACKUP="$GLOBAL_MD.harness.bak.$$"

cleanup() {
  if [ -f "$BACKUP" ]; then
    mv -f "$BACKUP" "$GLOBAL_MD"
    echo "[run-all] restored $GLOBAL_MD"
  fi
}
trap cleanup EXIT INT TERM

if [ -f "$GLOBAL_MD" ]; then
  mv "$GLOBAL_MD" "$BACKUP"
  echo "[run-all] swapped out global CLAUDE.md -> $BACKUP"
fi

read -r -a TASKS <<< "${TASKS:-T1 T2 T3 T4}"
read -r -a CELLS <<< "${CELLS:-A-none B-v1 C-v2}"
read -r -a SEEDS <<< "${SEEDS:-1 2 3}"
JOBS="${JOBS:-4}"

mkdir -p "$HARNESS/runs"

COMBOS=()
for T in "${TASKS[@]}"; do
  for C in "${CELLS[@]}"; do
    for S in "${SEEDS[@]}"; do
      COMBOS+=("$T $C $S")
    done
  done
done

echo "[run-all] ${#COMBOS[@]} combos, parallelism=$JOBS"

printf '%s\n' "${COMBOS[@]}" | \
  parallel --colsep ' ' -j "$JOBS" --joblog "$HARNESS/runs/joblog.tsv" \
  "bash $HARNESS/run-one.sh {1} {2} {3}"

echo "[run-all] all done. Results in $HARNESS/runs/"
