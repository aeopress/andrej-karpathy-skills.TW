"""Merge T1 verdicts from N=3 (initial run) and N=7 extension, compute statistics."""

import json
import math
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).parent.parent
RUNS = REPO_ROOT / 'harness' / 'runs'

# Load original 36-run verdicts (filter T1)
original = json.loads((RUNS / 'verdicts.json').read_text())
t1_old = [v for v in original['verdicts'] if v['task_id'] == 'T1']
print(f'Original T1 verdicts: {len(t1_old)}')

# Load new 21-run verdicts (from latest workflow output)
new_path = Path('/tmp/t1-extension-verdicts.json')
if not new_path.exists():
    print(f'ERROR: {new_path} does not exist. Save the workflow output there first.')
    raise SystemExit(1)
new_data = json.loads(new_path.read_text())
t1_new = new_data['verdicts'] if 'verdicts' in new_data else new_data
print(f'Extension T1 verdicts: {len(t1_new)}')

t1_all = t1_old + t1_new
print(f'Combined T1 verdicts: {len(t1_all)}')

# Group by cell
by_cell = defaultdict(list)
for v in t1_all:
    by_cell[v['cell']].append(v)

# Per-cell stats
print('\n=== T1 per-cell stats (N=10 each) ===')
print(f"{'cell':<10} {'N':<4} {'correct':<10} {'silent':<10} {'asked_clar':<12} {'over_eng':<10}")
for cell in ['A-none', 'B-v1', 'C-v2']:
    runs = by_cell[cell]
    n = len(runs)
    correct = sum(1 for r in runs if r['final_state_correct'])
    silent = sum(1 for r in runs if r['silent_assumption'])
    asked = sum(1 for r in runs if r['asked_clarification'])
    over_eng_mean = sum(r['over_engineering'] for r in runs) / n if n else 0
    print(f"{cell:<10} {n:<4} {correct}/{n}     {silent}/{n}     {asked}/{n}        {over_eng_mean:.2f}")

# Fisher exact test for B-v1 vs C-v2 on final_state_correct
def fisher_exact_2x2(a, b, c, d):
    """Two-sided Fisher exact for table [[a,b],[c,d]]."""
    n = a + b + c + d
    if n == 0:
        return 1.0

    def lchoose(n, k):
        if k < 0 or k > n:
            return float('-inf')
        return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)

    def hypergeom_logpmf(k, n1, n2, t):
        return lchoose(n1, k) + lchoose(n2, t - k) - lchoose(n1 + n2, t)

    n1 = a + b
    n2 = c + d
    t = a + c
    p_obs = hypergeom_logpmf(a, n1, n2, t)
    k_min = max(0, t - n2)
    k_max = min(t, n1)
    pvalue = 0.0
    for k in range(k_min, k_max + 1):
        lp = hypergeom_logpmf(k, n1, n2, t)
        if lp <= p_obs + 1e-12:
            pvalue += math.exp(lp)
    return min(1.0, pvalue)


print('\n=== Pairwise comparisons (Fisher exact, final_state_correct) ===')
pairs = [('B-v1', 'C-v2'), ('B-v1', 'A-none'), ('A-none', 'C-v2')]
for c1, c2 in pairs:
    r1 = by_cell[c1]
    r2 = by_cell[c2]
    a = sum(1 for r in r1 if r['final_state_correct'])
    b = len(r1) - a
    c = sum(1 for r in r2 if r['final_state_correct'])
    d = len(r2) - c
    p = fisher_exact_2x2(a, b, c, d)
    print(f'  {c1} ({a}/{len(r1)}) vs {c2} ({c}/{len(r2)}): p = {p:.4f}{"  ***" if p < 0.05 else ""}')

# Save combined verdicts for archival
out = RUNS / 't1-combined-verdicts.json'
out.write_text(json.dumps({'t1_verdicts_n30': t1_all, 'by_cell_counts': {k: len(v) for k, v in by_cell.items()}}, indent=2, ensure_ascii=False))
print(f'\nSaved {len(t1_all)} combined verdicts to {out}')
