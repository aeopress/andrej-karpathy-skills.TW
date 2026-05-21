# 受 Karpathy 啟發的 Claude Code 指引

一份精簡的 `CLAUDE.md`，補強 Claude Code 內建系統提示詞未涵蓋的部分；內容衍生自 [Andrej Karpathy 對 LLM 編碼陷阱的觀察](https://x.com/karpathy/status/2015883857489522876)。

[English](./README.md) | 繁體中文（台灣）

## 現況（2026 年 5 月）

Claude Code 在 Opus 4.7 / Sonnet 4.6 時代的預設系統提示詞已經內建了大部分通用的「不要過度設計／外科手術式修改／不要加沒人要的功能」指引 — 這些原本是本 skill 第一版的主要內容。**新版刻意只保留系統提示詞還未涵蓋的部分，並把 Karpathy 真正的「leverage」洞見重新定位為使用者端的 prompting 指引。**

舊版完整四原則保留在 [`archived/v1/`](./archived/v1/) 供參考。

## 給 LLM 看的內容

三條 reminder，與 [`CLAUDE.md`](./CLAUDE.md) 完全一致：

1. **困惑時停下** — 請求語意不清時，明確指出哪裡不清楚並提問；不要默默挑一個解讀就動手。
2. **每一行改動都要對應到請求** — 回報完成前，重看自己的 diff；任何沒有直接服務使用者目標的行就刪掉。
3. **以宣告式目標跑 loop** — 當存在可驗證的終態時，自主驅動直到達成。

整個指令檔就這樣。Karpathy 列出的其他陷阱（過度複雜化、順手重構、推測性功能、死碼累積、刪掉模型「看不順眼」的註解⋯⋯）都已經被 Claude Code 預設系統提示詞涵蓋；在這裡重述只會稀釋訊號。

## 給使用者的真正槓桿

Karpathy 最強的洞見其實是**使用者端的紀律**，不是 LLM 自我約束的事：

> 「LLM 非常擅長循環執行直到達成特定目標⋯⋯不要告訴它該做什麼，給它成功標準然後看著它跑完。」

要在自己的工作流中解鎖這個槓桿：

### 把命令式請求轉成宣告式

| 命令式（槓桿弱） | 宣告式（槓桿強） |
|---|---|
| 「加上輸入驗證」 | 「為這些無效輸入寫失敗測試，然後讓它們通過」 |
| 「修這個 bug」 | 「寫一個能重現 bug 的測試，然後讓它通過 — 其他測試必須還能過」 |
| 「讓它更快」 | 「把這個負載下的 p95 延遲壓到 X ms 以下；用 `scripts/bench.sh` 量」 |
| 「重構 X」 | 「重構 X 但不能改變可觀察行為；既有測試必須還能過」 |

### 同時交付驗證工具

連同目標一起給它驗證手段：測試指令、benchmark 腳本、lint 指令、給視覺檢查的 browser MCP。然後放手讓它迭代。

### 何時用哪一種

- **宣告式**：有可觀察結果的功能、bug 修復、效能工作、有測試覆蓋的重構。
- **命令式**：探索性編輯、UI 微調、文字創作、任何「完成」標準主觀的工作。

### 顯式 reframing：`/dec`（外掛內建）

`/dec <需求>` 會請 Claude 把這條需求轉成「成功條件 + 驗證指令 + 非目標」**但不動手實作**。你確認後它才開始做。適合你想對單一 prompt 套用宣告式紀律、又不想改變其他寫法時使用。

```
/dec 修掉登入頁第一次載入時的閃爍
```

回覆會包含成功條件（例：「Playwright 截圖比對 10 次，位移 < 2px」）、驗證指令、明確非目標。若任務太主觀或太小，會回「不適用，建議直接做」，不會硬轉換。

## 安裝

**選項 A：Claude Code 外掛**

在 Claude Code 中：

```
/plugin marketplace add yelban/andrej-karpathy-skills.TW
/plugin install andrej-karpathy-skills@karpathy-skills
```

**選項 B：依專案使用 `CLAUDE.md`**

```bash
curl -o CLAUDE.md https://raw.githubusercontent.com/yelban/andrej-karpathy-skills.TW/main/CLAUDE.md
```

## 搭配 Cursor 使用

本倉庫附 [`.cursor/rules/karpathy-guidelines.mdc`](.cursor/rules/karpathy-guidelines.mdc)，設定為 `alwaysApply: true`。詳情見 [`CURSOR.md`](./CURSOR.md)。

## 為什麼新版這麼短

把[原本四原則](./archived/v1/CLAUDE.md)跟現在 Claude Code Opus 4.7 系統提示詞逐條比對：

| 原版原則 | 系統提示詞是否已涵蓋？ |
|---|---|
| Simplicity First（不加推測性功能、不為一次性程式碼做抽象） | 已涵蓋 — "Don't add features, refactor, or introduce abstractions beyond what the task requires" |
| Simplicity First（不為不可能情境寫錯誤處理） | 已涵蓋 — "Don't add error handling, fallbacks, or validation for scenarios that can't happen" |
| Surgical Changes（不重構相鄰程式碼） | 已涵蓋 — "A bug fix doesn't need surrounding cleanup; a one-shot operation doesn't need a helper" |
| Surgical Changes（符合既有風格、不重新格式化） | 已涵蓋 — "Match the scope of your actions to what was actually requested" |
| Think Before Coding（明說假設、呈現權衡） | 部分涵蓋 — 系統提示詞涵蓋了探索性回覆；本 skill 補上「困惑時停下」 |
| Goal-Driven Execution（loop until verified） | 部分涵蓋 — 系統提示詞涵蓋了自我驗證；本 skill 補上使用者端的「宣告式 framing」 |

新版保留的三條 reminder，就是系統提示詞尚未涵蓋或強調不足的部分。

完整的 v1 → v2 逐行差異 — 每條被刪除的子規則對應到系統提示詞的取代來源、加上各條改寫的理由 — 詳見 [`archived/v1/NOTE.md`](./archived/v1/NOTE.md#detailed-v1--v2-diff-for-claudemd)（英文）。

## 與上游的關係

本倉庫是 [`forrestchang/andrej-karpathy-skills`](https://github.com/forrestchang/andrej-karpathy-skills) 的繁體中文（台灣）在地化 fork，為 Claude Code Opus 4.7 時代更新內容。Plugin / marketplace 名稱刻意與上游一致；README 為雙語（英文 + 繁體中文）。

## 授權

MIT
