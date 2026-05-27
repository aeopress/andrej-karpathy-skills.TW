"""Convert a claude -p transcript.jsonl into a compact markdown summary
suitable for feeding to an LLM judge."""

import json
import sys
from pathlib import Path


def truncate(text, n=600):
    if text is None:
        return ''
    s = str(text)
    return s if len(s) <= n else s[:n] + f'... [truncated {len(s) - n} chars]'


def summarize(jsonl_path: Path) -> str:
    out = []
    turn_idx = 0
    pytest_invocations = 0
    final_event = None

    with jsonl_path.open() as f:
        for line in f:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue

            t = d.get('type')

            if t == 'system' and d.get('subtype') == 'init':
                out.append(f"## init\nmodel={d.get('model')}  cwd={d.get('cwd')}")
                continue

            if t == 'assistant':
                msg = d.get('message', {})
                contents = msg.get('content', []) or []
                turn_idx += 1
                turn_lines = [f"\n## turn {turn_idx} (assistant)"]
                for c in contents:
                    ctype = c.get('type')
                    if ctype == 'text':
                        text = c.get('text', '').strip()
                        if text:
                            turn_lines.append(f"text: {truncate(text, 800)}")
                    elif ctype == 'tool_use':
                        name = c.get('name')
                        inp = c.get('input', {})
                        if name == 'Bash':
                            cmd = inp.get('command', '')
                            if 'pytest' in cmd:
                                pytest_invocations += 1
                            turn_lines.append(f"tool_use: Bash `{truncate(cmd, 200)}`")
                        elif name in ('Read', 'Glob', 'Grep'):
                            arg = inp.get('file_path') or inp.get('pattern') or inp.get('path') or str(inp)[:200]
                            turn_lines.append(f"tool_use: {name} `{truncate(arg, 200)}`")
                        elif name == 'Edit':
                            fp = inp.get('file_path', '')
                            old = inp.get('old_string', '')
                            new = inp.get('new_string', '')
                            turn_lines.append(f"tool_use: Edit `{fp}`")
                            turn_lines.append(f"  - old: {truncate(old, 200)}")
                            turn_lines.append(f"  - new: {truncate(new, 200)}")
                        elif name == 'Write':
                            fp = inp.get('file_path', '')
                            content = inp.get('content', '')
                            turn_lines.append(f"tool_use: Write `{fp}` ({len(content)} chars)")
                        else:
                            turn_lines.append(f"tool_use: {name} {truncate(json.dumps(inp), 200)}")
                    elif ctype == 'thinking':
                        pass
                if len(turn_lines) > 1:
                    out.extend(turn_lines)
                continue

            if t == 'user':
                msg = d.get('message', {})
                contents = msg.get('content', []) or []
                for c in contents:
                    if c.get('type') == 'tool_result':
                        content = c.get('content', '')
                        if isinstance(content, list):
                            content = ' '.join(
                                x.get('text', '') if isinstance(x, dict) else str(x) for x in content
                            )
                        out.append(f"tool_result: {truncate(content, 500)}")
                continue

            if t == 'result':
                final_event = d
                continue

    if final_event:
        cost = final_event.get('total_cost_usd', 0)
        duration = final_event.get('duration_ms', 0) / 1000
        is_err = final_event.get('is_error')
        subtype = final_event.get('subtype', '')
        out.append(f"\n## final\ncost=${cost:.3f} duration={duration:.1f}s error={is_err} subtype={subtype}")

    header = f"# Transcript summary\npytest_invocations={pytest_invocations}\n"
    return header + '\n'.join(out)


if __name__ == '__main__':
    runs_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('harness/runs')
    summaries_dir = runs_dir / '_summaries'
    summaries_dir.mkdir(exist_ok=True)
    count = 0
    for jsonl in sorted(runs_dir.glob('*/transcript.jsonl')):
        run_id = jsonl.parent.name
        summary = summarize(jsonl)
        out = summaries_dir / f'{run_id}.md'
        out.write_text(summary)
        count += 1
    print(f'Wrote {count} summaries to {summaries_dir}')
