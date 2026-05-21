---
description: Reframe an imperative request as declarative (success criteria + verification). Do not implement yet.
---

把以下需求轉成 declarative 版本，**不要動工**，先輸出三項：

1. **成功條件**：可驗證的端狀態（測試通過 / 輸出比對 / 效能門檻 / lint clean，擇一或多）
2. **驗證指令**：具體可執行的命令或檢查方式（例：`bun test foo.spec.ts`、`scripts/bench.sh`）
3. **非目標**：本次明確不做什麼，避免 scope creep

輸出後等使用者確認再實作。

若任務本質主觀（UI 微調、文案、命名）或太小（typo、單行 rename），
回覆「不適用，建議直接做」，不要硬轉換。

---

Request: $ARGUMENTS
