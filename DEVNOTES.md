# DEVNOTES — 改程式前必讀（給 AI agent 與人類維護者）

本檔記錄不寫下來就會被踩爆的設計決策與陷阱。改 `build_viewer.py` 前先讀完。

## build_viewer.py 的結構

一個 Python 腳本掃 `formats/`、`reports/`，把資料以 JSON 嵌進 `TEMPLATE`
（一整個 Python 字串裡的 HTML/CSS/JS），輸出 `app/index.html`。
**app/ 是產物，不要手改**——改模板後重跑 `python3 build_viewer.py`。

## 陷阱一：模板裡的反斜線跳脫（最容易改壞的地方）

`TEMPLATE` 是 Python 一般字串（非 raw string）。規則：

- 想在最終 JS 裡出現 `\n`（如 `split("\n")`）→ 模板裡寫 `\\n`
- JS regex 的 `\d` `\s` `\.` → 模板裡寫 `\\d` `\\s` `\\.`
- 驗證方法（每次改完 JS 必跑）：
  ```bash
  python3 build_viewer.py
  python3 -c "import re;js=re.search(r'<script>(.*)</script>',open('app/index.html').read(),re.S).group(1);open('/tmp/c.js','w').write('var localStorage={getItem:()=>\"2\",setItem:()=>{}},navigator={},window={},URL={createObjectURL:()=>\"\"},Blob=function(){},document={activeElement:null,body:{appendChild:()=>{}},getElementById:()=>({classList:{add:()=>{},remove:()=>{}},style:{},addEventListener:()=>{},value:'',onchange:null,showModal:()=>{},innerHTML:''}),createElement:()=>({classList:{add:()=>{}},style:{}})};'+js)"
  node --check /tmp/c.js
  ```

## 陷阱二：RTF 產生器的 ¤ 替換

RTF 控制字全以反斜線開頭，經過「Python 字串→JS 字串」雙層跳脫會需要四個反斜線，
極易寫錯。所以 `mdToRtf` 用 `R()`：RTF 原始碼一律用 `¤` 代替反斜線書寫，
執行時 `R()` 把 `¤` 換回反斜線。**不要**在 RTF 相關程式碼裡直接寫反斜線。
改完 RTF 產生器用 Apple 引擎驗證（Pages 同引擎）：
`textutil -convert html 產出.rtf` 成功＝Pages 開得起來。

## 陷阱三：diff 編輯器的三個刻意設計（不是 bug，不要「修」）

1. **行比對忽略行首編號**（`normLine` 把編號正規化成 `#.`）：因為編號自動重排會
   讓插入一行後所有後續行的編號都變，若不忽略，diff 會把整個清單標成全刪全增。
2. **刪改混雜用相似度配對**（`pairRun`，門檻 0.5）：不能照位置硬配，
   否則錯位的行會被逐字比對成紅綠絞肉。門檻改低會亂配、改高會失去行內字級標記。
3. **編輯器載入時不重排編號**：只有使用者編輯／按升降階／切樣式後才重排，
   避免「打開舊格式就被改動」。

## 陷阱四：編號系統的語意

- `NUMLINE` 只認「行首」編號（阿拉伯複合 `1.1`、簡單 `1.`、羅馬 `I.`、單字母 `A.`）。
  內文中的數字（「2-3 句」）不受影響——改 regex 前先想清楚這條界線。
- 兩種樣式是 Word 的兩個標準：法律式 `1. → 1.1 → 1.1.1`（複合），
  大綱式 `I. → A. → 1. → a.`（每層只顯示自己的編號）。不存在 `I.1` 或 `I.i`。
- 空白行不重置編號計數、非空白非編號行（含標題）會重置。

## 陷阱五：報告歸類

預覽頁靠報告 metadata 的 `使用格式：…<檔名>.md` 把報告掛到格式卡下。
解析刻意寬容（帶不帶括號都認）；AGENTS.md 已規定 agent 必須寫
`使用格式：<主標題>（<檔名>.md）`。兩邊是雙保險，動其一前先看另一邊。

## 其他約定

- 導覽的 localStorage key 是 `t2m_tour`，值 `"2"`＝看過。導覽內容大改時把
  判斷值 bump（`"2"`→`"3"`），既有使用者會重新看到新導覽。
- 隱私文案鐵則：只有「錄音檔／聲音檔」可以說不上傳；逐字稿文字會送到
  使用者自己的 AI 供應商。禁寫「會議內容完全不上傳」。
- `transcripts/`、`reports/`、`app/` 在 .gitignore（app/index.html 內嵌報告全文），
  永遠不推上 GitHub。
- UI 字級偏大是刻意的（使用者明確要求），不要「優化」回小字。
