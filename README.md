# talk-to-minutes

會議錄音 → 結構化報告的 agent 工具。

- **安全**：錄音檔由 OpenAI Whisper 在你的電腦本機轉成文字，聲音檔永遠不離開你的電腦；
  逐字稿文字由你自己的 AI（Claude Code／Codex）整理成報告——資料只經過你本來就在用的
  AI 供應商，不經過任何第三方會議服務。
- **零訂閱**：不需訂閱第三方會議工具。報告由你既有的 AI harness（Claude Code 或
  OpenAI Codex）整理，沒有額外費用。
- **無長度限制**：Whisper 對音檔長度沒有上限，幾小時的會議也能轉，只是處理時間較久。
- **格式庫隨你累積**：報告格式存在 `formats/`，可隨時聊天新增。可根據會議的性質或
  匯報的對象點選不同的報告格式，由你指定每個格式的存檔檔名，方便下次選用。

## 先看看再說（不用安裝）

**線上展示版（含新手教學動畫）：https://habbo-shibbo.github.io/talk-to-minutes/**
——先點右上角「怎麼使用」，操作介面和完整教學都在裡面。

## 下載

- 會 git：`git clone https://github.com/Habbo-Shibbo/talk-to-minutes.git`
- 不會 git：本頁綠色「Code」按鈕 → Download ZIP → 解壓縮
  （得到的資料夾叫 talk-to-minutes-main，一樣用）

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

進到你放 talk-to-minutes 的資料夾（不確定路徑？在終端機打 `cd ` 加空格，把資料夾
從 Finder 拖進來，路徑會自動補上），打開你的 harness：

**OpenAI Codex：** 執行 `codex`
**Claude Code：** 執行 `claude`

然後一句話交辦，例如：「幫我把這個錄音做成會議報告」，接著把錄音檔從 Finder
拖進終端機視窗（路徑會自動填好），按 Enter。harness 會自動讀本資料夾的
`AGENTS.md`（Claude Code 經 `CLAUDE.md`），照流程跑：轉逐字稿 → 列出格式讓你選
→ 產出報告存到 `reports/`。

## 報告格式

- 內建格式見 `formats/INDEX.md`：通用會議紀要、客戶會議報告、主管一頁簡報。
- **新增格式**：直接跟 agent 說「我要設計新格式」，描述情境（例如
  「給業務主管看的季度回顧」）讓它設計，或直接指定你要的標題與整理邏輯。
  確認後它會存進 `formats/` 並更新索引，下次就能點選。
- 格式檔是純 Markdown，也可以自己直接編輯。

## 格式庫預覽頁（app）

執行 `python3 build_viewer.py`（或叫 agent 跑）會產生 `app/index.html`：
每個格式一張預覽卡（縮圖可直接看到報告骨架），卡片下方列出用該格式整理過的
報告，點擊即可回顧內容。跟 agent 說「打開 app」或自己開啟該檔案即可。
`app/` 內嵌報告內容，已加入 `.gitignore`，不會被推上 GitHub。

## 資料夾結構

```
talk-to-minutes/
├── AGENTS.md        # agent 操作說明（Codex 讀這份）
├── CLAUDE.md        # 指向 AGENTS.md（Claude Code 讀這份）
├── transcribe.sh    # Whisper 轉逐字稿腳本
├── build_viewer.py  # 產生格式庫預覽頁 app/index.html
├── formats/         # 報告格式庫（INDEX.md 是索引）
├── transcripts/     # 逐字稿輸出
└── reports/         # 報告輸出
```

## 已知限制

- Whisper 不分辨發言者，逐字稿不分人；agent 只能從上下文推測誰說的。
- 中文轉錄偶爾出現簡體字，agent 產報告時會統一轉繁體。
- 長錄音（1 小時以上）在 CPU 上轉錄較慢，屬正常。如果常轉長錄音嫌慢，
  且你用的是 Apple 晶片的 Mac，可改裝 [mlx-whisper](https://pypi.org/project/mlx-whisper/)
  （同樣的 Whisper 模型，但使用 Apple 晶片的 GPU 運算，快數倍），
  並把 `transcribe.sh` 裡的 `whisper` 指令換成對應的 `mlx_whisper` 用法
  （參數見專案頁）。請你的 agent 幫你改即可。
