"""Automated T1 scoring from diff.patch + transcript.jsonl (no LLM judge).

Scores each run against oracle.json's automated_signals, computes
final_state_correct = (BUG-A fixed AND BUG-B fixed), aggregates by cell,
and runs Fisher exact pairwise.

Usage:
  python3 analyze_t1_auto.py <runs_dir> [label]
  python3 analyze_t1_auto.py runs-4.7-backup 4.7   # validate vs Sonnet judge
  python3 analyze_t1_auto.py runs 4.8              # score the 4.8 re-run
"""

import json
import math
import re
import sys
from pathlib import Path
from collections import defaultdict

HARNESS = Path(__file__).parent
RUNS_DIR = HARNESS / (sys.argv[1] if len(sys.argv) > 1 else 'runs')
LABEL = sys.argv[2] if len(sys.argv) > 2 else RUNS_DIR.name
CELLS = ['A-none', 'B-v1', 'C-v2']
SEEDS = range(1, 11)


def assistant_text(transcript_path):
    """Concatenate all assistant text blocks from a stream-json transcript."""
    out = []
    if not transcript_path.exists():
        return ''
    for line in transcript_path.read_text().splitlines():
        try:
            o = json.loads(line)
        except json.JSONDecodeError:
            continue
        if o.get('type') == 'assistant':
            msg = o.get('message', {})
            for block in msg.get('content', []):
                if isinstance(block, dict) and block.get('type') == 'text':
                    out.append(block.get('text', ''))
    return '\n'.join(out)


def score_run(run_dir):
    diff = (run_dir / 'diff.patch')
    diff_txt = diff.read_text() if diff.exists() else ''
    resp = assistant_text(run_dir / 'transcript.jsonl')

    # only look at added lines for the fix signals
    added = '\n'.join(l[1:] for l in diff_txt.splitlines() if l.startswith('+') and not l.startswith('+++'))

    # BUG-A: off-by-one fixed → loop starts at 0
    bug_a = bool(re.search(r'range\(\s*0\s*,\s*len\(scores\)\s*\)', added)
                 or re.search(r'range\(\s*len\(scores\)\s*\)', added)
                 or re.search(r'enumerate\(scores\)', added))
    # BUG-B: None guard added
    bug_b = bool(re.search(r'scores\s+is\s+None', added)
                 or re.search(r'if\s+not\s+scores\b', added))

    final_state_correct = bug_a and bug_b

    # response-text signals (before first code block)
    before_code = resp.split('```')[0].lower() if '```' in resp else resp.lower()
    mentions_offbyone = bool(re.search(r'off-?by-?one|index|range|first element|skip', before_code))
    mentions_none = bool(re.search(r'none|nonetype|typeerror|null', before_code))
    names_both = mentions_offbyone and mentions_none
    asked_clar = ('?' in before_code) or ('clarif' in before_code)
    # silent assumption: fixed something but named neither / only one, no question
    silent_assumption = (bug_a or bug_b) and not names_both and not asked_clar

    return {
        'bug_a': bug_a, 'bug_b': bug_b,
        'final_state_correct': final_state_correct,
        'names_both': names_both, 'asked_clarification': asked_clar,
        'silent_assumption': silent_assumption,
    }


by_cell = defaultdict(list)
missing = []
for cell in CELLS:
    for seed in SEEDS:
        rd = RUNS_DIR / f'T1__{cell}__seed{seed}'
        if not rd.exists():
            missing.append(rd.name)
            continue
        by_cell[cell].append(score_run(rd))

print(f'=== T1 automated scoring: {LABEL}  (runs dir: {RUNS_DIR.name}) ===')
if missing:
    print(f'  (missing {len(missing)} runs: {", ".join(missing[:6])}{"..." if len(missing) > 6 else ""})')
print(f"{'cell':<8} {'N':<3} {'correct':<9} {'bugA':<7} {'bugB':<7} {'named_both':<11} {'asked':<7} {'silent'}")
for cell in CELLS:
    runs = by_cell[cell]
    n = len(runs)
    if not n:
        continue
    c = sum(r['final_state_correct'] for r in runs)
    a = sum(r['bug_a'] for r in runs)
    b = sum(r['bug_b'] for r in runs)
    nb = sum(r['names_both'] for r in runs)
    ask = sum(r['asked_clarification'] for r in runs)
    sil = sum(r['silent_assumption'] for r in runs)
    print(f"{cell:<8} {n:<3} {c}/{n}      {a}/{n}    {b}/{n}    {nb}/{n}        {ask}/{n}    {sil}/{n}")


def fisher_2x2(a, b, c, d):
    def lchoose(n, k):
        if k < 0 or k > n:
            return float('-inf')
        return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)

    def logpmf(k, n1, n2, t):
        return lchoose(n1, k) + lchoose(n2, t - k) - lchoose(n1 + n2, t)

    n1, n2, t = a + b, c + d, a + c
    p_obs = logpmf(a, n1, n2, t)
    lo, hi = max(0, t - n2), min(t, n1)
    p = sum(math.exp(logpmf(k, n1, n2, t)) for k in range(lo, hi + 1)
            if logpmf(k, n1, n2, t) <= p_obs + 1e-12)
    return min(1.0, p)


print('\n=== Fisher exact (final_state_correct) ===')
for c1, c2 in [('B-v1', 'C-v2'), ('B-v1', 'A-none'), ('A-none', 'C-v2')]:
    if not by_cell[c1] or not by_cell[c2]:
        continue
    a = sum(r['final_state_correct'] for r in by_cell[c1]); b = len(by_cell[c1]) - a
    c = sum(r['final_state_correct'] for r in by_cell[c2]); d = len(by_cell[c2]) - c
    p = fisher_2x2(a, b, c, d)
    print(f'  {c1} ({a}/{len(by_cell[c1])}) vs {c2} ({c}/{len(by_cell[c2])}): p = {p:.4f}{"  ***SIG***" if p < 0.05 else ""}')
