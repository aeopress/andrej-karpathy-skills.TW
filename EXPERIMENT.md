# A/B 實證：CLAUDE.md v1 vs v2 vs 無

2026-05-27 跑的兩階段實證。Phase 1 是 4 tasks × 3 seeds × 3 cells = 36 runs，Phase 2 在最區分維度 T1 加碼到 10 seeds × 3 cells = 30 runs。受測 model：Opus 4.7（200K context）。Judge model：Sonnet 4.6（blind to cell label）。

## TL;DR

**沒有任何 cell 顯著優於其他**。Phase 1 N=3 上看到的「B-v1 在 T1 上 3/3 vs C-v2 1/3」純粹是 sampling noise——Phase 2 加碼到 N=10 後三 cell 全部打平 7/10、Fisher exact p=1.00。

**正確結論**：在這個 task set 上、Opus 4.7 自身約 70% T1 正確率，CLAUDE.md（不論 v1 或 v2）**沒有可測量的效應**。維持 v2 不需要被 v1 取代、但要在 README 誠實標示「實證未顯示 v2 比 v1 更差也沒更好」。

## 後續：Opus 4.8 re-run（2026-05-29、T1 N=10）

Opus 4.8 出後（lean system prompt 設 default、把原 prompt 裡的 explicit guardrail 全部移除、見 [`archived/observed-system-prompts/2026-05-29-opus-4.8-cli.md`](./archived/observed-system-prompts/2026-05-29-opus-4.8-cli.md)），用同一套 harness 重跑 T1 N=10 三 cell。**這次用 automated scorer（[`harness/analyze_t1_auto.py`](./harness/analyze_t1_auto.py)、純 diff grep + response text、非 Sonnet judge）**——嚴格定義「兩 bug 都修才算 correct」，絕對值與 Phase 2 的 Sonnet judge 不可直接比，但 4.7↔4.8 用同一把尺有效。

### 結果（兩 bug 都修率）

| Cell | 4.7（同 scorer 重算 baseline）| 4.8 |
|---|---|---|
| A-none | 3/10 | **8/10** |
| B-v1（65 行）| 4/10 | **9/10** |
| C-v2（19 行）| 3/10 | **10/10** |

### 兩個判定

1. **Model-level：4.8 顯著優於 4.7**。pooled「兩 bug 都修」33% → 90%、Fisher exact p = 1.1e-5、漏修率 67% → 10%（**少漏 6.7 倍**）——比 Anthropic 官方「4.8 比 4.7 漏放程式碼瑕疵機率低約 4 倍」還強。
2. **Cell-level：CLAUDE.md flavor 在 4.8 仍無顯著差異**。B-v1(9) vs C-v2(10) p=1.0、B-v1(9) vs A-none(8) p=1.0、A-none(8) vs C-v2(10) p=0.47——全部 > 0.05。

### 對 Reading A / B 的判定

4.8 snapshot 檔列了兩種解讀，本次數據做出判定：

- **Reading B 否定**：若「4.8 lean prompt 移除 guardrail → v1 完整規則重新有用」，B-v1 應明顯領先——但 B-v1(9) 沒優於 C-v2(10) 或 A-none(8)，19 行精簡版甚至略高。
- **Reading A 強力支持**：4.8 移除 explicit guardrail 文字、但抓 bug 行為**不降反升**（33% → 90%）——guardrail 移到了 post-training（model weights），CLAUDE.md 重述它們仍無邊際效應。thesis 在 4.8 上更成立。

### caveat

1. **automated scorer 非 Sonnet judge**——只信 diff-based 的 bug_a / bug_b / final_state_correct（純 grep、deterministic）；response-text signals（asked_clarification / silent_assumption）在 4.7 backup 上有 false positive（算出 asked 3/1/3、但原 Sonnet judge 是 0），**不採信**。
2. 只跑 **T1、N=10**；effort=medium（與 4.7 baseline 一致、非 4.8 default 的 high）；未重跑 T2/T3/T4。
3. 4.8 raw runs 在 `harness/runs-4.8-T1/`、4.7 baseline 在 `harness/runs-4.7-backup/`（皆 local、未進 git——同原實驗 `runs/` 慣例）。任何人可 `MODEL=claude-opus-4-8 TASKS=T1 CELLS="A-none B-v1 C-v2" SEEDS="1 2 3 4 5 6 7 8 9 10" bash harness/run-all.sh` 後 `python3 harness/analyze_t1_auto.py runs` 重現。

## 重大教訓

**N=3 sample 反向翻盤**——這是 plan-stage 就列為 caveat 的風險，加碼後成真。任何只有 N=3 的 LLM A/B 結論都應該預設為 **uncertain until N ≥ 10 confirmed**。

## Phase 2 結果（N=10 T1）

| Cell | N | final_state_correct | silent_assumption | asked_clarification | over_engineering 平均 |
|---|---|---|---|---|---|
| A-none | 10 | **7/10** | 8/10 | 0/10 | 0.10 |
| B-v1 | 10 | **7/10** | 8/10 | 0/10 | 0.20 |
| C-v2 | 10 | **7/10** | 7/10 | 0/10 | 0.30 |

Fisher exact (final_state_correct):
- B-v1 vs C-v2: p = 1.000
- B-v1 vs A-none: p = 1.000
- A-none vs C-v2: p = 1.000

**沒有 cell 達到統計顯著**。over_engineering 上 C-v2 略高 (0.3 vs 0.1)、但 N=10 仍小、不該過度解讀。

### asked_clarification 零次的意義

30 個 T1 runs 中**沒有一次** agent 在 edit 前問 clarification——不論有沒有 CLAUDE.md、不論哪一版。Opus 4.7 在這個 task 上的 default 行為是「直接動工」、CLAUDE.md 三條/四條規則都壓不下去。

「Stop when confused」與「Think Before Coding — present multiple interpretations」都未能可靠觸發。Opus 4.7 對「a bug」這種看似單純的 prompt 不會主動判定為「ambiguous」、所以兩個規則的觸發前置條件都沒滿足。

## Phase 1 結果（N=3，4 tasks）

僅作紀錄、結論已被 Phase 2 推翻。

| 指標 | A-none | B-v1 | C-v2 |
|---|---|---|---|
| 整體 final_correct | 10/12 | 12/12 | 10/12 |
| T1 correctness | 2/3 | 3/3 | 1/3 |
| T2 correctness | 2/3 | 3/3 | 3/3 |
| T3 correctness | 3/3 | 3/3 | 3/3 |
| T4 declarative loop | 1/3 | 2/3 | 1/3 |

Phase 1 Workflow B 的 synthesizer 給出「B significantly better than C → restore v1」結論——**但 Phase 2 N=10 推翻**這個 T1 上的差距。T2/T3/T4 N 仍是 3、保留 caveat（見下）。

## 實驗設計

### Cells (3)

| Cell | CLAUDE.md 內容 |
|---|---|
| A-none | 無（Claude Code 系統提示詞 only） |
| B-v1 | upstream 4 原則版（65 行）— Think Before Coding / Simplicity First / Surgical Changes / Goal-Driven Execution |
| C-v2 | 我們現版（19 行）— Stop when confused / Every changed line traces to request / Loop on declarative goals |

### Tasks (4)

| ID | 名稱 | 誘發痛點 |
|---|---|---|
| T1 | ambiguous-bug | wrong assumption / no clarification |
| T2 | feature-bloat | overcomplication |
| T3 | drive-by | surgical changes |
| T4 | declarative-loop | goal-driven autonomous loop |

### 環境隔離

- `~/.claude/CLAUDE.md` 整段 swap 出（trap restore on exit），避免 user 全域 80 行內容污染。
- 每次 invocation 用獨立 tmp dir、`git init` 後 baseline commit、跑完 diff。
- `claude -p --model claude-opus-4-7 --effort medium --max-budget-usd 2.00 --disable-slash-commands --disallowed-tools "WebSearch,WebFetch,Task,Skill" --permission-mode bypassPermissions --no-session-persistence --setting-sources project,local`
- 未隔離：Claude Code 系統提示詞 + user plugins (codex-orchestrator、web-access) 三 cell 都載入、作為常數。

## Cost 與時間

| 階段 | 內容 | 時間 | 成本 |
|---|---|---|---|
| Workflow A | 4 task designer + 1 reviewer | ~3 min | ~$1 |
| Phase 1 runs | 36 × claude -p (Opus 4.7) | ~25 min | ~$20 |
| Phase 1 judge | 36 Sonnet 4.6 + 1 Opus synth | ~3 min | ~$5 |
| Phase 2 runs | 21 × claude -p (T1 extension) | ~10 min | ~$10 |
| Phase 2 judge | 21 Sonnet 4.6 | ~1 min | ~$2 |
| **總計** | | ~42 min | ~$38 |

仍低於原 plan 預估 $50。

## 限制

1. **T2/T3/T4 仍是 N=3**。Phase 2 只加碼 T1。但既然 T1 在 N=10 上翻盤，預設 T2/T3/T4 的 N=3 觀察也不可信。
2. **Judge bias**：Sonnet 4.6 評 Opus 4.7、雖然不同 model 但都是 Claude 系列。
3. **System prompt + plugins 不可控**：三 cell 都會被 Claude Code 內建系統提示詞、user plugins (codex-orchestrator、web-access) 影響。我們測的是「邊際效應」、不是「CLAUDE.md 純效果」。系統提示詞本身可能已涵蓋大部分 Karpathy 痛點、進而稀釋 CLAUDE.md 效果。
4. **T3 ceiling effect**：N=9 全 surgical、無區分能力。
5. **T4 環境 confound**：pytest module-not-found 干擾絕對成功率。
6. **Task 集設計小**：4 個 toy task 不一定能引出真實大型 codebase 中的痛點。

## 結論與行動

**決策樹**（原 plan）映射：
- ~~B 全面顯著優於 C → 復刻 v1~~（Phase 1 N=3 暫時命中、Phase 2 推翻）
- ~~C 顯著優於 B → 維持 v2~~（沒命中）
- ~~個別維度互有勝負 → hybrid v3~~（沒命中）
- ✅ **三個 cell 全部統計持平 → 維持 v2 + README 加「實證持平、有 CLAUDE.md 無顯著差異」段落**

**建議行動**：

1. **維持 v2 內容不變**——實證沒顯示 v2 比 v1 更差、也沒更好。
2. **README「Why this version is shorter」section 改寫**：誠實說明「v2 vs v1 在這個小 task set + Opus 4.7 上沒有可測量差異 (N=10 T1 / N=3 其他)；上游 v1 也是好選擇」。提供 EXPERIMENT.md 連結與資料。
3. **不需要復刻 v1**——但要承認「Phase 1 的興奮是 sample noise」。
4. **保留 `/dec` 指令**——獨立加分項，未受測。

**不建議**：

- 維持原「v2 更精簡所以更好」的論證——實證沒支持。
- 復刻 v1——實證沒支持。

## 對 Karpathy 帖子的回頭看

Karpathy 提到的「LLMs make wrong assumptions and just run along with them」**在 Opus 4.7 上仍真實存在**——這次 30 個 T1 runs 中 22 個是 silent_assumption=True、0 個 asked_clarification。任何 CLAUDE.md 規則（v1 或 v2）都沒有降低這個比例。

但他的另一個觀察「LLMs are exceptionally good at looping until they meet specific goals」**也是真實的**——T4 declarative loop runs 中 agent 確實能 autonomous 跑 pytest 多次、迭代修 bug（只是受 pytest env 問題影響）。

**真正的 leverage 仍在 user-side framing（「give it success criteria」）**——這也是 `/dec` 指令存在的價值。CLAUDE.md 規則的差異邊際效應、在 Opus 4.7 系統提示詞已涵蓋大部分後、不容易凸顯。

## 對外可重現

所有原始資料 + scripts 都在 `harness/`：

- `harness/tasks/T{1,2,3,4}/` — task spec + repo + oracle
- `harness/cells/{A-none,B-v1,C-v2}/` — CLAUDE.md variants
- `harness/runs/<run_id>/` — 每個 invocation 的 diff/transcript/metrics
- `harness/runs/verdicts.json` — Phase 1 36 個 judge verdict + synthesis
- `harness/runs/t1-combined-verdicts.json` — Phase 2 N=30 合併 verdict
- `harness/run-one.sh`、`run-all.sh` — invocation harness
- `harness/summarize_transcript.py`、`preprocess_for_judge.py`、`analyze_t1.py`
- `harness/judge.workflow.js` — Workflow B judge + synth script

任何人想重跑：clone 倉庫、`brew install parallel`、`uv tool install pytest`、`bash harness/run-all.sh`。
