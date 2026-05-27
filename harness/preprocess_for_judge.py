"""Bundle 36 runs' (oracle, summary, diff, metrics) into a single JSON payload
that the judge workflow consumes."""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
RUNS = REPO_ROOT / 'harness' / 'runs'
TASKS = REPO_ROOT / 'harness' / 'tasks'
SUMMARIES = RUNS / '_summaries'

# Cache oracles per task_id.
oracles = {p.parent.name: json.loads(p.read_text()) for p in TASKS.glob('*/oracle.json')}

payloads = []
for run_dir in sorted(RUNS.iterdir()):
    metrics_path = run_dir / 'metrics.json'
    if not run_dir.is_dir() or not metrics_path.exists():
        continue
    metrics = json.loads(metrics_path.read_text())
    task_id = metrics['task_id']
    diff = (run_dir / 'diff.patch').read_text()
    summary_path = SUMMARIES / f'{run_dir.name}.md'
    summary = summary_path.read_text() if summary_path.exists() else '(no summary)'
    payloads.append({
        'run_id': metrics['run_id'],
        'task_id': task_id,
        'cell': metrics['cell'],
        'metrics': metrics,
        'oracle': oracles[task_id],
        'diff': diff,
        'summary': summary,
    })

out = RUNS / 'judge_payload.json'
out.write_text(json.dumps(payloads, ensure_ascii=False, indent=2))
print(f'wrote {len(payloads)} payloads to {out}')
print(f'total size: {out.stat().st_size:,} bytes')
