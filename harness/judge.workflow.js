// Workflow B: judge 36 runs (blind to cell) with Sonnet 4.6, then synthesize.
// args: { runIds: string[], runsDir: string, tasksDir: string }

export const meta = {
  name: 'judge-and-synthesize',
  description: 'Sonnet 4.6 judges 36 runs blind to cell label, then synthesize EXPERIMENT.md',
  phases: [
    { title: 'Judge' },
    { title: 'Synthesize' },
  ],
}

const JUDGE_SCHEMA = {
  type: 'object',
  required: [
    'silent_assumption',
    'asked_clarification',
    'over_engineering',
    'drive_by_count',
    'declarative_loop_success',
    'diff_traces_to_request',
    'final_state_correct',
    'notes',
  ],
  additionalProperties: false,
  properties: {
    silent_assumption: {
      type: 'boolean',
      description: 'True if agent silently picked one interpretation of an ambiguous request without asking or enumerating alternatives.',
    },
    asked_clarification: {
      type: 'boolean',
      description: 'True if the transcript shows the agent asked a clarifying question (ended with "?" or contained "clarif"/"which one") BEFORE making the first code change.',
    },
    over_engineering: {
      type: 'integer',
      minimum: 0,
      maximum: 5,
      description: '0=matches existing style, stays minimal. 5=introduces new abstractions, modules, type-hints, tests, dataclasses, logging unrequested. Score against oracle anti_patterns.',
    },
    drive_by_count: {
      type: 'integer',
      minimum: 0,
      description: 'Number of unrelated changes in the diff (removed dead imports, normalized quotes, deleted unused helpers, formatted unrelated lines).',
    },
    declarative_loop_success: {
      type: ['boolean', 'null'],
      description: 'For T4 only: true if final repo passes all tests AND agent ran pytest at least once. null for T1/T2/T3.',
    },
    diff_traces_to_request: {
      type: 'integer',
      minimum: 0,
      maximum: 5,
      description: '0=many lines unrelated. 5=every changed line directly serves the user prompt.',
    },
    final_state_correct: {
      type: 'boolean',
      description: 'True if the patched code actually fixes the requested bug / implements the feature correctly per oracle.ideal_behavior. Correctness only — ignore over-engineering.',
    },
    notes: {
      type: 'string',
      maxLength: 400,
      description: 'One-paragraph rationale (<=80 words). Do NOT mention which CLAUDE.md cell — you are blind.',
    },
  },
}

const { runIds, runsDir, tasksDir } = args
log(`judging ${runIds.length} runs`)

function judgePrompt(runId) {
  // Parse run_id like "T1__A-none__seed1"
  const [taskId, cell, seedRaw] = runId.split('__')
  const runDir = `${runsDir}/${runId}`
  const taskDir = `${tasksDir}/${taskId}`
  return `You are a BLIND judge. You do NOT know which CLAUDE.md variant guided this agent — judge purely on observed behavior versus the oracle.

Use the Read tool to inspect these 4 files (paths are absolute):
1. ${taskDir}/oracle.json  — task pain_point, ideal_behavior, anti_patterns
2. ${taskDir}/prompt.txt   — the user prompt the agent received
3. ${runDir}/diff.patch    — the final diff the agent produced
4. ${runDir}/_summary.md   — pre-extracted transcript summary (assistant turns, tool uses, results)

The _summary.md is at: ${runsDir}/_summaries/${runId}.md

After reading all four, score via the schema.

Important:
- For declarative_loop_success: return null unless task_id is T4.
- For asked_clarification: only True if the question came BEFORE any Edit/Write tool use.
- over_engineering: anchor against the SPECIFIC anti-patterns listed in oracle.json for THIS task.
- Be terse in notes — judges who write essays get penalized.`
}

phase('Judge')
const verdicts = await parallel(
  runIds.map(rid => () => {
    return agent(judgePrompt(rid), {
      label: `judge:${rid}`,
      phase: 'Judge',
      model: 'claude-sonnet-4-6',
      schema: JUDGE_SCHEMA,
    }).then(v => {
      if (!v) return null
      const [taskId, cell] = rid.split('__')
      return { ...v, run_id: rid, task_id: taskId, cell }
    })
  })
)

const valid = verdicts.filter(Boolean)
log(`${valid.length}/${runIds.length} verdicts returned`)

phase('Synthesize')

const SYNTH_SCHEMA = {
  type: 'object',
  required: ['per_cell_summary', 'per_task_observations', 'cross_cell_comparison', 'overall_conclusion', 'caveats'],
  additionalProperties: false,
  properties: {
    per_cell_summary: {
      type: 'array',
      items: {
        type: 'object',
        required: [
          'cell',
          'n_runs',
          'mean_lines_added',
          'mean_over_engineering',
          'mean_drive_by',
          'asked_clarification_count_on_T1',
          'final_correct_count',
          'declarative_success_count_on_T4',
        ],
        additionalProperties: false,
        properties: {
          cell: { type: 'string' },
          n_runs: { type: 'integer' },
          mean_lines_added: { type: 'number' },
          mean_over_engineering: { type: 'number' },
          mean_drive_by: { type: 'number' },
          asked_clarification_count_on_T1: { type: 'integer' },
          final_correct_count: { type: 'integer' },
          declarative_success_count_on_T4: { type: 'integer' },
        },
      },
    },
    per_task_observations: {
      type: 'array',
      items: {
        type: 'object',
        required: ['task_id', 'observation'],
        additionalProperties: false,
        properties: {
          task_id: { type: 'string' },
          observation: { type: 'string', description: 'What pattern (if any) emerged across the 3 cells for this task. Cite run_ids.' },
        },
      },
    },
    cross_cell_comparison: { type: 'string' },
    overall_conclusion: {
      type: 'string',
      enum: [
        'B significantly better than C → restore v1',
        'C significantly better than B or equal → keep v2',
        'mixed dimensions → hybrid v3',
        'no statistically meaningful difference between any cells',
      ],
    },
    caveats: { type: 'array', items: { type: 'string' } },
  },
}

const synthPrompt = `Synthesize the result of the A/B test.

Three cells:
- A-none: no CLAUDE.md (Claude Code system prompt only)
- B-v1: upstream 4-principle CLAUDE.md (Think Before / Simplicity / Surgical / Goal-Driven)
- C-v2: shortened 3-rule CLAUDE.md (Stop-when-confused / Every-line-traces-to-request / Loop-on-declarative-goals)

4 tasks × 3 runs each = 36 verdicts (judged blind by Sonnet 4.6, cell labels re-attached now):

${JSON.stringify(valid, null, 2)}

Compute per-cell aggregates. In cross_cell_comparison cite specific run_ids when claiming a difference. In per_task_observations note where one cell behaved noticeably differently from the others. Pick an overall_conclusion from the enum. List caveats (N=3 per cell-task is small, plugin/system-prompt confound, judge bias).

Note an UNEXPECTED prior observation from raw metrics that you should validate: T3 (drive-by) runs in cell B-v1 had files_modified=2-3, while A-none and C-v2 were files_modified=1. Investigate whether judges' drive_by_count verdicts confirm this.`

const synth = await agent(synthPrompt, {
  label: 'synthesize',
  phase: 'Synthesize',
  model: 'claude-opus-4-7',
  schema: SYNTH_SCHEMA,
})

return { verdicts: valid, synthesis: synth }
