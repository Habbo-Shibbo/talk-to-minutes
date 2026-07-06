# meeting-report

會議錄音 → 結構化報告的 agent 工具。在本機用 OpenAI Whisper 轉逐字稿
（錄音不上傳、免費），再由你的 AI harness（Claude Code 或 OpenAI Codex）
依你選的格式整理成報告。報告格式存在 `formats/`，可隨時聊天新增。

## 安裝（第一次用，約 5 分鐘）

需求：Mac + [Homebrew](https://brew.sh)。終端機執行：

```bash
brew install ffmpeg openai-whisper
```

第一次轉錄會自動下載 Whisper turbo 模型（約 1.5GB），之後離線可用。

拿到這個資料夾後（朋友分享給你的話，整個資料夾複製到任何位置即可），
給腳本執行權限：

```bash
chmod +x transcribe.sh
```

## 怎麼用

進到這個資料夾，打開你的 harness，用一句話交辦即可：

**OpenAI Codex：**

```bash
cd meeting-report
codex
```

然後說：「幫我把 ~/Downloads/會議錄音.m4a 做成會議報告」。
Codex 會自動讀本資料夾的 `AGENTS.md`，照流程跑：轉逐字稿 → 列出格式讓你選
→ 產出報告存到 `reports/`。

**Claude Code：**

```bash
cd meeting-report
claude
```

同一句話交辦即可（Claude Code 讀 `CLAUDE.md` → `AGENTS.md`）。

## 報告格式

- 內建格式見 `formats/INDEX.md`：通用會議紀要、客戶會議報告、主管一頁簡報。
- **新增格式**：直接跟 agent 說「我要設計新格式」，描述情境（例如
  「給業務主管看的季度回顧」）讓它設計，或直接指定你要的標題與整理邏輯。
  確認後它會存進 `formats/` 並更新索引，下次就能點選。
- 格式檔是純 Markdown，也可以自己直接編輯。

## 資料夾結構

```
meeting-report/
├── AGENTS.md        # agent 操作說明（Codex 讀這份）
├── CLAUDE.md        # 指向 AGENTS.md（Claude Code 讀這份）
├── transcribe.sh    # Whisper 轉逐字稿腳本
├── formats/         # 報告格式庫（INDEX.md 是索引）
├── transcripts/     # 逐字稿輸出
└── reports/         # 報告輸出
```

## 已知限制

- Whisper 不分辨發言者，逐字稿不分人；agent 只能從上下文推測誰說的。
- 中文轉錄偶爾出現簡體字，agent 產報告時會統一轉繁體。
- 長錄音（1 小時以上）在 CPU 上轉錄較慢，屬正常。
