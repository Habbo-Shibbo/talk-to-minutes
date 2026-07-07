#!/usr/bin/env python3
"""產生 app/index.html：格式預覽卡＋各格式整理過的報告清單。
每次新增格式或產出報告後執行：python3 build_viewer.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read_md(path):
    text = path.read_text(encoding="utf-8")
    return re.sub(r"<!--.*?-->", "", text, flags=re.S).strip()


def first_heading(text, fallback):
    m = re.search(r"^# (.+)$", text, re.M)
    return m.group(1).strip() if m else fallback


def section(text, name):
    m = re.search(rf"^## {name}\n+(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1).strip() if m else ""


formats = []
for p in sorted((ROOT / "formats").glob("*.md")):
    if p.name == "INDEX.md":
        continue
    text = read_md(p)
    formats.append({
        "file": p.name,
        "title": first_heading(text, p.stem),
        "scenario": section(text, "適用情境"),
        "body": text,
    })

reports = []
for p in sorted((ROOT / "reports").glob("*.md")):
    text = read_md(p)
    m = re.search(r"使用格式：[^\n]*?([^\s（()）:：]+\.md)", text)
    reports.append({
        "file": p.name,
        "title": first_heading(text, p.stem),
        "format": m.group(1) if m else None,
        "body": text,
    })

data = json.dumps({"formats": formats, "reports": reports, "root": str(ROOT)},
                  ensure_ascii=False)
data = data.replace("</", "<\\/")  # 避免內容中的 </script> 破壞頁面

TEMPLATE = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>talk-to-minutes 格式庫</title>
<style>
  :root { --ink:#1a1a1a; --muted:#767676; --line:#e3e0da; --bg:#f4f2ee; --card:#fff; --accent:#4a5f8a; }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--bg); color:var(--ink);
         font-family:"PingFang TC","Heiti TC",system-ui,sans-serif; }
  header { padding:28px 32px 8px; display:flex; align-items:flex-start; gap:16px; }
  header .htxt { flex:1; }
  header h1 { margin:0; font-size:26px; }
  header p { margin:6px 0 0; color:var(--muted); font-size:15.5px; }
  .guide-btn { flex:none; border:1.5px solid var(--accent); background:#fff; color:var(--accent);
               border-radius:22px; padding:10px 20px; font-size:15.5px; cursor:pointer; margin-top:4px; }
  .guide-btn:hover { background:var(--accent); color:#fff; }
  #tour { max-width:640px; }
  .tour-body { padding:8px 28px 10px; font-size:16px; line-height:1.85; min-height:320px; }
  .tour-body .kpoint { background:#e9ecf3; border-radius:8px; padding:10px 14px; margin:14px 0;
                       color:var(--accent); font-weight:600; font-size:15.5px; line-height:1.7; }
  .tour-body .role { margin:8px 0; padding-left:14px; }
  .tour-body .role b { color:var(--accent); }
  .tour-foot { display:flex; align-items:center; gap:10px; padding:14px 22px; border-top:1px solid var(--line); }
  .tdots { display:flex; gap:7px; margin-right:auto; }
  .tdot { width:9px; height:9px; border-radius:50%; background:#d8d5cd; }
  .tdot.on { background:var(--accent); }
  .tour-foot button { border:none; border-radius:8px; padding:10px 18px; font-size:15px; cursor:pointer; }
  #t-prev { background:#eee; }
  #t-next { background:var(--accent); color:#fff; }
  .grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(290px,1fr));
          gap:26px; padding:24px 32px 48px; align-items:start; }
  .fmt { display:flex; flex-direction:column; gap:10px; }
  .sheet { background:var(--card); border:1px solid var(--line); border-radius:6px;
           aspect-ratio:3/4; overflow:hidden; padding:14px 14px 0; cursor:pointer;
           box-shadow:0 1px 3px rgba(0,0,0,.08); position:relative; transition:box-shadow .15s; }
  .sheet:hover { box-shadow:0 4px 14px rgba(0,0,0,.14); }
  .sheet::after { content:""; position:absolute; left:0; right:0; bottom:0; height:34px;
                  background:linear-gradient(transparent,var(--card)); }
  .mini { font-size:10.5px; line-height:1.55; color:#333; pointer-events:none; }
  .mini h1 { font-size:14px; margin:0 0 6px; border-bottom:1px solid var(--line); padding-bottom:4px; }
  .mini h2 { font-size:12px; margin:8px 0 3px; color:var(--accent); }
  .mini ul,.mini ol { margin:2px 0; padding-left:16px; }
  .mini table { border-collapse:collapse; width:100%; margin:3px 0; }
  .mini th,.mini td { border:1px solid var(--line); padding:1px 4px; font-size:9.5px; text-align:left; }
  .mini p { margin:2px 0; }
  .fmt-name { font-size:19px; font-weight:600; }
  .fmt-file { font-size:15px; color:#1e8449; font-weight:400; margin-left:8px; }
  .fmt-scenario { font-size:14.5px; color:var(--muted); line-height:1.55; margin-top:-4px; }
  .rlist { border-top:1px solid var(--line); padding-top:8px; display:flex; flex-direction:column; gap:2px; }
  .rlist-label { font-size:13.5px; color:var(--muted); margin-bottom:2px; }
  .rlink { font-size:15.5px; color:var(--accent); cursor:pointer; padding:5px 6px; border-radius:4px;
           overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  .rlink:hover { background:#e9ecf3; }
  .rnone { font-size:14px; color:#b5b0a8; padding:2px 6px; }
  #peek { display:none; position:fixed; top:50%; transform:translateY(-50%);
          width:min(620px, 46vw); background:#fff;
          border-radius:12px; box-shadow:0 16px 50px rgba(0,0,0,.3); z-index:50;
          pointer-events:none; overflow:hidden; }
  #peek.on { display:block; }
  #peek .doc { max-height:80vh; overflow-y:auto; }
  #peek .peek-hint { font-size:15.5px; font-weight:600; color:#fff; background:var(--accent);
                     text-align:center; padding:10px 0; }
  .base-row { display:flex; align-items:baseline; gap:10px; margin:0 0 6px; font-size:15.5px;
              flex-wrap:wrap; }
  #base-select { width:100%; font-size:15px; padding:10px 12px; border:1px solid var(--line);
                 border-radius:8px; background:#fff; margin:0 0 14px; }
  .add-card { border:2px dashed #c8c2b8; border-radius:10px; min-height:180px; display:flex;
              flex-direction:column; align-items:center; justify-content:center; gap:8px;
              cursor:pointer; color:var(--muted); font-size:17px; }
  .add-card:hover { border-color:var(--accent); color:var(--accent); }
  .add-plus { font-size:44px; line-height:1; }
  #newfmt textarea { width:100%; min-height:150px; font-size:16px; line-height:1.6;
                     font-family:inherit; border:1px solid var(--line); border-radius:8px;
                     padding:12px; resize:vertical; }
  #newfmt .hint { font-size:14.5px; color:var(--muted); line-height:1.6; margin:0 0 10px; }
  #newfmt .actions { display:flex; align-items:center; gap:12px; margin-top:14px; }
  #newfmt .actions button { border:none; background:var(--accent); color:#fff; border-radius:8px;
                            padding:10px 18px; font-size:15.5px; cursor:pointer; }
  #newfmt .copied { font-size:14.5px; color:#2e7d32; }
  .steps { display:flex; gap:8px; margin:0 0 16px; }
  .step { flex:1; display:flex; align-items:center; gap:8px; padding:8px 10px; border-radius:8px;
          background:#f0eee9; color:var(--muted); font-size:14.5px; }
  .step .n { width:22px; height:22px; border-radius:50%; background:#c9c5bc; color:#fff;
             display:flex; align-items:center; justify-content:center; font-size:13px; flex:none; }
  .step.on { background:#e9ecf3; color:var(--accent); font-weight:600; }
  .step.on .n { background:var(--accent); }
  .term-intro { font-size:14.5px; color:var(--muted); margin:18px 0 8px; }
  .term { background:#1e1e1e; color:#c9c9c9; border-radius:10px; padding:13px 15px; font-size:13.5px;
          line-height:1.9; font-family:ui-monospace,SFMono-Regular,Menlo,monospace; }
  .term .u { color:#e8e8e8; } .term .p { color:#8a8a8a; } .term .a { color:#7fd4a8; }
  .cmd-label { font-size:14px; color:var(--muted); margin:14px 0 2px; }
  .cmd-row { display:flex; align-items:stretch; gap:8px; margin:6px 0; }
  .cmd-row .cmd { flex:1; background:#1e1e1e; color:#e8e8e8; border-radius:8px; padding:11px 14px;
                  font-family:ui-monospace,Menlo,monospace; font-size:14px; overflow-x:auto;
                  white-space:nowrap; display:flex; align-items:center; }
  .cmd-row .cmd-copy { flex:none; border:none; background:var(--accent); color:#fff;
                       border-radius:8px; padding:0 18px; font-size:14px; cursor:pointer; }
  .dragdemo { position:relative; background:#f0eee9; border:1px solid var(--line);
              border-radius:10px; padding:14px; margin:10px 0 4px; overflow:hidden; }
  .dd-finder { width:190px; background:#fff; border:1px solid var(--line); border-radius:8px;
               box-shadow:0 2px 8px rgba(0,0,0,.08); margin-bottom:26px; }
  .dd-finder .dd-bar { background:#e8e5df; border-radius:8px 8px 0 0; padding:4px 10px;
                       color:#8a8578; font-size:11.5px; }
  .dd-file { padding:8px 12px; font-size:13.5px; }
  .dd-term { background:#1e1e1e; border-radius:8px; padding:12px 14px; color:#e8e8e8;
             font-family:ui-monospace,Menlo,monospace; font-size:13.5px; line-height:1.8; }
  .dd-term .p { color:#8a8a8a; }
  .dd-path { color:#7fd4a8; opacity:0; animation:ddpath 7s linear infinite; }
  .dd-hint-enter { background:#3a3a3a; border-radius:4px; padding:0 8px; margin-left:10px;
                   opacity:0; animation:ddenter 7s linear infinite; }
  .dd-ghost { position:absolute; left:30px; top:44px; opacity:0; pointer-events:none;
              background:#fff; border:1px solid var(--line); border-radius:6px; padding:3px 10px;
              font-size:13px; box-shadow:0 6px 16px rgba(0,0,0,.25);
              animation:ddghost 7s linear infinite; }
  @keyframes ddghost {
    0%,10% { opacity:0; transform:translate(0,0); }
    16% { opacity:1; transform:translate(0,0); }
    44% { opacity:1; transform:translate(120px,62px) scale(.96); }
    50%,100% { opacity:0; transform:translate(120px,62px) scale(.9); }
  }
  @keyframes ddpath { 0%,48% { opacity:0; } 54%,100% { opacity:1; } }
  @keyframes ddenter { 0%,62% { opacity:0; } 68%,94% { opacity:1; } 100% { opacity:0; } }
  .dd-cap { display:flex; gap:16px; font-size:13.5px; color:var(--muted); margin-top:10px;
            flex-wrap:wrap; }
  .dd-cap b { color:var(--accent); }
  .term .f1 { opacity:0; animation:tfin .4s ease .8s forwards; }
  .term .f2 { opacity:0; animation:tfin .4s ease 1.8s forwards; }
  .term .f3 { opacity:0; animation:tfin .4s ease 2.8s forwards; }
  .term .cur { display:inline-block; width:8px; height:15px; background:#7fd4a8;
               vertical-align:-2px; margin-left:3px; animation:tblink 1s step-end infinite; }
  .term .tag { display:inline-block; font-size:11.5px; border-radius:4px; padding:1px 7px;
               margin-right:8px; font-family:inherit; }
  .term .tag-you { background:#4a5f8a; color:#fff; }
  .term .tag-ai { background:#274d3b; color:#a8e6c5; }
  @keyframes tfin { to { opacity:1; } }
  @keyframes tblink { 50% { opacity:0; } }
  dialog.wide { max-width:1280px; width:calc(100vw - 40px); }
  .ed-grid { display:grid; grid-template-columns:1fr 1fr; }
  .ed-col { padding:14px 18px; min-width:0; }
  .ed-col + .ed-col { border-left:1px solid var(--line); background:#faf9f6; }
  .ed-label { font-size:13.5px; color:var(--muted); margin-bottom:10px; }
  #diff-view { font-size:15px; line-height:1.9; max-height:58vh; overflow-y:auto; }
  #diff-view .dh1 { font-size:17px; font-weight:600; }
  #diff-view .dh2 { color:var(--accent); font-weight:600; }
  #diff-view del { color:#c0392b; text-decoration:line-through; }
  #diff-view ins { color:#1e8449; text-decoration:none; }
  .ed-tools { display:flex; align-items:center; gap:8px; margin-bottom:8px; flex-wrap:wrap; }
  .ed-tools button { border:1px solid var(--line); background:#fff; border-radius:8px;
                     padding:7px 12px; font-size:14px; cursor:pointer; color:var(--ink); }
  .ed-tools button:hover { border-color:var(--accent); color:var(--accent); }
  .ed-tools select { font-size:14px; padding:7px 8px; border:1px solid var(--line);
                     border-radius:8px; background:#fff; }
  .ed-tools-hint { font-size:12.5px; color:var(--muted); }
  #ed-text { width:100%; height:52vh; font-family:ui-monospace,SFMono-Regular,Menlo,monospace;
             font-size:13.5px; line-height:1.8; border:1px solid var(--line); border-radius:8px;
             padding:12px; resize:none; }
  .ed-bar { display:flex; align-items:center; gap:12px; padding:14px 22px;
            border-top:1px solid var(--line); font-size:15px; flex-wrap:wrap; }
  .ed-bar input { font-size:14.5px; font-family:ui-monospace,Menlo,monospace; padding:8px 10px;
                  border:1px solid var(--line); border-radius:8px; width:190px; }
  .ed-bar #ed-title { font-family:inherit; width:210px; }
  .ed-bar .count { color:var(--muted); font-size:14px; margin-left:auto; }
  .ed-bar button.primary { border:none; background:var(--accent); color:#fff; border-radius:8px;
                           padding:10px 18px; font-size:15.5px; cursor:pointer; }
  .ed-bar .back { border:none; background:none; color:var(--muted); font-size:14.5px; cursor:pointer; }
  dialog { border:none; border-radius:10px; max-width:720px; width:calc(100vw - 48px);
           max-height:85vh; padding:0; box-shadow:0 12px 40px rgba(0,0,0,.25); }
  dialog::backdrop { background:rgba(0,0,0,.35); }
  .dlg-bar { display:flex; justify-content:space-between; align-items:center; gap:12px;
             padding:14px 22px; border-bottom:1px solid var(--line); position:sticky; top:0; background:#fff; }
  .dlg-bar .t { font-weight:600; font-size:17.5px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  .dlg-bar button { border:none; background:#eee; border-radius:6px; padding:8px 16px; cursor:pointer; font-size:15px; }
  .dlg-sub { display:none; align-items:center; gap:10px; padding:10px 22px;
             border-bottom:1px solid var(--line); background:#f7f6f3; font-size:13.5px; flex-wrap:wrap; }
  .dlg-sub .dlg-path { font-family:ui-monospace,Menlo,monospace; color:var(--muted);
                       overflow:hidden; text-overflow:ellipsis; max-width:100%; }
  .dlg-sub button { border:1px solid var(--line); background:#fff; border-radius:6px;
                    padding:6px 12px; font-size:13.5px; cursor:pointer; }
  .dlg-sub .wordbtn { background:var(--accent); color:#fff; border:none; }
  .doc { padding:10px 28px 32px; font-size:16px; line-height:1.8; overflow-y:auto; }
  .doc h1 { font-size:22px; border-bottom:1px solid var(--line); padding-bottom:8px; }
  .doc h2 { font-size:18px; color:var(--accent); margin-top:24px; }
  .doc table { border-collapse:collapse; width:100%; margin:8px 0; }
  .doc th,.doc td { border:1px solid var(--line); padding:6px 10px; text-align:left; font-size:15px; }
  .doc th { background:#f7f6f3; }
  .doc code { background:#f0eee9; border-radius:3px; padding:1px 5px; font-size:14px; }
</style>
</head>
<body>
<header>
  <div class="htxt">
    <h1>talk-to-minutes 格式庫</h1>
    <p>滑鼠停在卡片上可放大檢視格式；點卡片看完整定義；卡片下方是用該格式整理過的報告，
       點檔名看內容。</p>
  </div>
  <button class="guide-btn" onclick="openTour()">怎麼使用？</button>
</header>
<div class="grid" id="grid"></div>
<div id="peek"><div class="doc" id="peek-body"></div>
  <div class="peek-hint">⟳ 滑鼠留在原本的卡片上滾滾輪，這個預覽就會上下捲動</div></div>
<dialog id="newfmt">
  <div class="dlg-bar"><div class="t" id="nf-title">設計新格式</div>
    <button onclick="document.getElementById('newfmt').close()">關閉</button></div>
  <div class="doc" id="nf-wizard">
    <div class="steps">
      <div class="step on" id="s1"><span class="n">1</span>寫需求</div>
      <div class="step" id="s2"><span class="n">2</span>按複製</div>
      <div class="step" id="s3"><span class="n">3</span>貼給 AI</div>
    </div>
    <div class="base-row">
      <label for="base-select">以現有格式為基礎：</label>
      <span style="font-size:13.5px;color:var(--muted);">選現有格式會開啟左右對照編輯器</span>
    </div>
    <select id="base-select"><option value="">不帶入，在下方格子描述想要怎樣的報告，讓 AI 幫我設計</option></select>
    <textarea id="newfmt-text" placeholder="想要什麼樣的報告？講情境（給誰看、開什麼會）或直接列標題，例：除錯會議紀錄，要有「問題現象、已排除的可能、下一步實驗」…"></textarea>
    <div class="actions">
      <button onclick="copyPrompt()">複製交辦指令</button>
      <span class="copied" id="copied-msg"></span>
    </div>
    <div class="term-intro">按「複製交辦指令」後，切回終端機，⌘V 貼上、按 Enter——要貼的就這一次，之後都是 AI 的回覆：</div>
    <div class="term" id="term">
      <div><span class="tag tag-you">你貼上</span><span class="u">剛複製的整段指令 → 按 Enter</span></div>
      <div class="f1"><span class="tag tag-ai">AI 回覆</span><span class="a">依你的需求設計了新格式草稿：「除錯會議紀錄」——問題現象／已排除的可能／下一步實驗</span></div>
      <div class="f2"><span class="tag tag-ai">AI 回覆</span><span class="a">確認 OK 嗎？存檔後預覽頁會多一張新卡片<span class="cur"></span></span></div>
    </div>
  </div>
  <div id="nf-editor" style="display:none">
    <div class="ed-grid">
      <div class="ed-col">
        <div class="ed-label">原格式 · 即時對照（<del style="color:#c0392b">紅刪除線</del>＝刪掉、<span style="color:#1e8449">綠字</span>＝新增）</div>
        <div id="diff-view"></div>
      </div>
      <div class="ed-col">
        <div class="ed-label">你的版本 · 直接編輯（Markdown）</div>
        <div class="ed-tools">
          <button onclick="indentSel(-1)" title="升階（Shift+Tab）">← 升階</button>
          <button onclick="indentSel(1)" title="降階（Tab）">降階 →</button>
          <select id="num-style" title="編號樣式">
            <option value="arabic">編號：1. → 1.1（法律式）</option>
            <option value="roman">編號：I. → A. → 1.（大綱式）</option>
          </select>
          <span class="ed-tools-hint">編號自動重排｜游標放在編號行按 Tab／Shift+Tab 升降階</span>
        </div>
        <textarea id="ed-text" spellcheck="false"></textarea>
      </div>
    </div>
    <div class="ed-bar">
      <button class="back" onclick="backToWizard()">← 返回</button>
      <label for="ed-title">主標題</label>
      <input id="ed-title" list="title-options" placeholder="選現有的或打新的">
      <datalist id="title-options"></datalist>
      <label for="ed-filename">副標題（檔名）</label>
      <input id="ed-filename" placeholder="例：exec-numbers.md">
      <span class="count" id="ed-count"></span>
      <button class="primary" onclick="copySaveCmd()">複製存檔指令</button>
      <span class="copied" id="ed-copied"></span>
    </div>
  </div>
</dialog>
<dialog id="dlg">
  <div class="dlg-bar"><div class="t" id="dlg-title"></div>
    <button onclick="document.getElementById('dlg').close()">關閉</button></div>
  <div class="dlg-sub" id="dlg-sub"></div>
  <div class="doc" id="dlg-body"></div>
</dialog>
<dialog id="tour">
  <div class="dlg-bar"><div class="t" id="tour-title"></div>
    <button onclick="document.getElementById('tour').close()">略過</button></div>
  <div class="tour-body" id="tour-body"></div>
  <div class="tour-foot">
    <div class="tdots" id="tdots"></div>
    <button id="t-prev" onclick="showTour(tstep-1)">上一步</button>
    <button id="t-next" onclick="tourNext()">下一步</button>
  </div>
</dialog>
<script>
const DATA = __DATA__;

function esc(s){ return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); }
function inline(s){
  return esc(s)
    .replace(/\\*\\*([^*]+)\\*\\*/g,"<b>$1</b>")
    .replace(/`([^`]+)`/g,"<code>$1</code>");
}
function mdToHtml(md){
  const out=[]; let list=null, table=false, para=[];
  const flushPara=()=>{ if(para.length){ out.push("<p>"+inline(para.join(" "))+"</p>"); para=[]; } };
  const flushList=()=>{ if(list){ out.push("</"+list+">"); list=null; } };
  const flushTable=()=>{ if(table){ out.push("</table>"); table=false; } };
  for(const raw of md.split("\\n")){
    const l=raw.trimEnd();
    if(/^\\s*\\|/.test(l)){
      flushPara(); flushList();
      const cells=l.trim().replace(/^\\||\\|$/g,"").split("|").map(c=>c.trim());
      if(cells.every(c=>/^:?-+:?$/.test(c))) continue;
      const tag=table?"td":"th";
      if(!table){ out.push("<table>"); table=true; }
      out.push("<tr>"+cells.map(c=>"<"+tag+">"+inline(c)+"</"+tag+">").join("")+"</tr>");
      continue;
    }
    flushTable();
    let m;
    if((m=l.match(/^(#{1,3}) (.+)/))){
      flushPara(); flushList();
      const h="h"+m[1].length; out.push("<"+h+">"+inline(m[2])+"</"+h+">");
    } else if((m=l.match(/^\\s*[-*] (.+)/))){
      flushPara();
      if(list!=="ul"){ flushList(); out.push("<ul>"); list="ul"; }
      out.push("<li>"+inline(m[1])+"</li>");
    } else if((m=l.match(/^\\s*\\d+\\. (.+)/))){
      flushPara();
      if(list!=="ol"){ flushList(); out.push("<ol>"); list="ol"; }
      out.push("<li>"+inline(m[1])+"</li>");
    } else if(l.trim()===""){
      flushPara(); flushList();
    } else {
      para.push(l.trim());
    }
  }
  flushPara(); flushList(); flushTable();
  return out.join("\\n");
}

function openDoc(title, md, file){
  document.getElementById("dlg-title").textContent=title;
  document.getElementById("dlg-body").innerHTML=mdToHtml(md);
  const sub=document.getElementById("dlg-sub");
  if(file){
    window.__docMd=md; window.__docFile=file;
    sub.style.display="flex";
    sub.innerHTML='<span class="dlg-path">'+esc(DATA.root+"/reports/"+file)+'</span>'+
      '<button onclick="copyPath(this)">複製路徑</button>'+
      '<button class="wordbtn" onclick="downloadDoc()" title="有裝 Microsoft Word 選這個">Word (.doc)｜你有 Office Word</button>'+
      '<button class="wordbtn" onclick="downloadRtf()" title="沒裝 Word 選這個">Word (.rtf)｜Pages、TextEdit、Google Docs</button>';
  } else { sub.style.display="none"; }
  const dlg=document.getElementById("dlg");
  dlg.showModal(); document.getElementById("dlg-body").scrollTop=0;
}
function copyPath(btn){
  const p=DATA.root+"/reports/"+window.__docFile;
  const done=()=>{ btn.textContent="已複製 ✓"; setTimeout(()=>{ btn.textContent="複製路徑"; },1500); };
  if(navigator.clipboard&&navigator.clipboard.writeText){
    navigator.clipboard.writeText(p).then(done,()=>fallbackCopy(p,done));
  } else { fallbackCopy(p,done); }
}
const RBS=String.fromCharCode(92);
const R=s=>s.split("¤").join(RBS);
function rtfEsc(s){
  let out="";
  for(const ch of s){
    const c=ch.codePointAt(0);
    if(ch===RBS)out+=R("¤¤");
    else if(ch==="{")out+=R("¤{");
    else if(ch==="}")out+=R("¤}");
    else if(c<128)out+=ch;
    else if(c<=0xFFFF){ let n=c; if(n>32767)n-=65536; out+=R("¤u")+n+"?"; }
    else {
      const h=0xD800+((c-0x10000)>>10), l=0xDC00+((c-0x10000)&1023);
      out+=R("¤u")+(h-65536)+"?"+R("¤u")+(l-65536)+"?";
    }
  }
  return out;
}
function inlineRtf(s){
  let out="";
  for(const p of s.split(/(\\*\\*[^*]+\\*\\*)/)){
    const m=p.match(/^\\*\\*([^*]+)\\*\\*$/);
    if(m)out+="{"+R("¤b ")+rtfEsc(m[1])+"}";
    else out+=rtfEsc(p.replace(/`([^`]+)`/g,"$1"));
  }
  return out;
}
function mdToRtf(md){
  const out=[R("{¤rtf1¤ansi¤deff0{¤fonttbl{¤f0 PingFang TC;}}¤f0¤fs24¤uc1 ")];
  const lines=md.split("\\n");
  let i=0;
  while(i<lines.length){
    const l=lines[i];
    let m;
    if(/^\\s*\\|/.test(l)){
      const rows=[];
      while(i<lines.length&&/^\\s*\\|/.test(lines[i])){
        const cells=lines[i].trim().replace(/^\\||\\|$/g,"").split("|").map(c=>c.trim());
        if(!cells.every(c=>/^:?-+:?$/.test(c)))rows.push(cells);
        i++;
      }
      const ncol=Math.max.apply(null,rows.map(r=>r.length));
      for(let r=0;r<rows.length;r++){
        let row=R("¤trowd¤trgaph108");
        for(let c=1;c<=ncol;c++)
          row+=R("¤clbrdrt¤brdrs¤clbrdrl¤brdrs¤clbrdrb¤brdrs¤clbrdrr¤brdrs¤cellx")+Math.round(9360*c/ncol);
        for(let c=0;c<ncol;c++){
          const txt=inlineRtf(rows[r][c]||"");
          row+=R("¤intbl ")+(r===0?"{"+R("¤b ")+txt+"}":txt)+R("¤cell");
        }
        out.push(row+R("¤row"));
      }
      out.push(R("¤pard¤par"));
      continue;
    }
    if((m=l.match(/^# (.+)/))){ out.push("{"+R("¤b¤fs36 ")+inlineRtf(m[1])+R("¤par")+"}"+R("¤par")); }
    else if((m=l.match(/^## (.+)/))){ out.push("{"+R("¤b¤fs30 ")+inlineRtf(m[1])+R("¤par")+"}"); }
    else if((m=l.match(/^### (.+)/))){ out.push("{"+R("¤b¤fs26 ")+inlineRtf(m[1])+R("¤par")+"}"); }
    else if((m=l.match(/^\\s*[-*] (.+)/))){ out.push(R("¤pard¤li360 ¤bullet  ")+inlineRtf(m[1])+R("¤par¤pard")); }
    else if(l.trim()===""){ out.push(R("¤par")); }
    else { out.push(inlineRtf(l)+R("¤par")); }
    i++;
  }
  out.push("}");
  return out.join("\\n");
}
function saveBlob(content,type,ext){
  const blob=new Blob(content,{type:type});
  const a=document.createElement("a");
  a.href=URL.createObjectURL(blob);
  a.download=window.__docFile.replace(/\\.md$/,ext);
  document.body.appendChild(a); a.click(); a.remove();
}
function downloadRtf(){
  saveBlob([mdToRtf(window.__docMd)],"application/rtf",".rtf");
}
function downloadDoc(){
  const html='<html xmlns:o="urn:schemas-microsoft-com:office:office" '+
    'xmlns:w="urn:schemas-microsoft-com:office:word"><head><meta charset="utf-8"><style>'+
    'body{font-family:"PingFang TC","Microsoft JhengHei",sans-serif;font-size:12pt;line-height:1.7;}'+
    'h1{font-size:18pt;} h2{font-size:14pt;} table{border-collapse:collapse;}'+
    'th,td{border:1pt solid #999;padding:4pt 8pt;} th{background:#f0f0f0;}'+
    '</style></head><body>'+mdToHtml(window.__docMd)+"</body></html>";
  saveBlob(["\\ufeff"+html],"application/msword",".doc");
}

const grid=document.getElementById("grid");
for(const f of DATA.formats){
  const card=document.createElement("div"); card.className="fmt";
  const sheet=document.createElement("div"); sheet.className="sheet";
  sheet.innerHTML='<div class="mini">'+mdToHtml(f.body)+"</div>";
  sheet.onclick=()=>openDoc(f.title+"（"+f.file+"）", f.body);
  sheet.onmouseenter=()=>{
    const peek=document.getElementById("peek");
    const body=document.getElementById("peek-body");
    body.innerHTML=mdToHtml(f.body); body.scrollTop=0;
    // 預覽自動閃到卡片的對側，不擋住其他卡
    const r=sheet.getBoundingClientRect();
    if(r.left + r.width/2 > window.innerWidth/2){
      peek.style.left="24px"; peek.style.right="auto";
    } else {
      peek.style.left="auto"; peek.style.right="24px";
    }
    peek.classList.add("on");
  };
  sheet.onmouseleave=()=>document.getElementById("peek").classList.remove("on");
  sheet.addEventListener("wheel",e=>{
    e.preventDefault();
    document.getElementById("peek-body").scrollTop+=e.deltaY;
  },{passive:false});
  card.appendChild(sheet);
  const name=document.createElement("div"); name.className="fmt-name";
  name.innerHTML=esc(f.title)+'<span class="fmt-file">'+esc(f.file)+"</span>";
  card.appendChild(name);
  if(f.scenario){
    const sc=document.createElement("div"); sc.className="fmt-scenario";
    sc.textContent=f.scenario.replace(/\\n+/g," "); card.appendChild(sc);
  }
  const rl=document.createElement("div"); rl.className="rlist";
  const mine=DATA.reports.filter(r=>r.format===f.file);
  rl.innerHTML='<div class="rlist-label">用此格式整理的報告（'+mine.length+'）</div>';
  if(mine.length===0){ rl.innerHTML+='<div class="rnone">尚無</div>'; }
  for(const r of mine){
    const a=document.createElement("div"); a.className="rlink"; a.textContent=r.file;
    a.title=r.title; a.onclick=()=>openDoc(r.title, r.body, r.file);
    rl.appendChild(a);
  }
  card.appendChild(rl);
  grid.appendChild(card);
}
const orphans=DATA.reports.filter(r=>!DATA.formats.some(f=>f.file===r.format));
if(orphans.length){
  const card=document.createElement("div"); card.className="fmt";
  card.innerHTML='<div class="fmt-name">未歸類報告</div>'+
    '<div class="fmt-scenario">metadata 缺「使用格式」或格式檔已被移除</div>';
  const rl=document.createElement("div"); rl.className="rlist";
  for(const r of orphans){
    const a=document.createElement("div"); a.className="rlink"; a.textContent=r.file;
    a.onclick=()=>openDoc(r.title, r.body, r.file); rl.appendChild(a);
  }
  card.appendChild(rl); grid.appendChild(card);
}
const addCard=document.createElement("div"); addCard.className="add-card";
addCard.innerHTML='<div class="add-plus">＋</div><div>設計新格式</div>';
addCard.onclick=()=>{
  document.getElementById("copied-msg").textContent="";
  backToWizard();
  const t=document.getElementById("term"); t.innerHTML=t.innerHTML;
  document.getElementById("newfmt").showModal();
};
grid.appendChild(addCard);

const baseSel=document.getElementById("base-select");
for(const f of DATA.formats){
  const o=document.createElement("option");
  o.value=f.file; o.textContent=f.title+"（"+f.file+"）";
  baseSel.appendChild(o);
}
let currentBase=null;
baseSel.onchange=()=>{ if(baseSel.value) enterEditor(baseSel.value); };

function enterEditor(file){
  currentBase=DATA.formats.find(f=>f.file===file);
  document.getElementById("nf-wizard").style.display="none";
  document.getElementById("nf-editor").style.display="block";
  document.getElementById("nf-title").textContent="以「"+currentBase.title+"」為底，編輯新格式";
  document.getElementById("newfmt").classList.add("wide");
  document.getElementById("ed-filename").value=currentBase.file.replace(/\\.md$/,"")+"-v2.md";
  document.getElementById("ed-copied").textContent="";
  document.getElementById("ed-text").value=currentBase.body;
  document.getElementById("ed-title").value=currentBase.title;
  renderDiff();
}
document.getElementById("title-options").innerHTML=
  [...new Set(DATA.formats.map(f=>f.title))].map(t=>'<option value="'+esc(t)+'">').join("");
document.getElementById("ed-title").addEventListener("input",()=>{
  const t=document.getElementById("ed-title").value.trim();
  if(!t)return;
  const ta=document.getElementById("ed-text");
  const lines=ta.value.split("\\n");
  const idx=lines.findIndex(l=>/^# /.test(l));
  if(idx>=0)lines[idx]="# "+t; else lines.unshift("# "+t);
  ta.value=lines.join("\\n");
  clearTimeout(window.__dt); window.__dt=setTimeout(renderDiff,200);
});
function backToWizard(){
  document.getElementById("nf-editor").style.display="none";
  document.getElementById("nf-wizard").style.display="block";
  document.getElementById("nf-title").textContent="設計新格式";
  document.getElementById("newfmt").classList.remove("wide");
  document.getElementById("s3").classList.remove("on");
  baseSel.value=""; currentBase=null;
}
document.getElementById("ed-text").addEventListener("input",()=>{
  clearTimeout(window.__dt);
  window.__dt=setTimeout(()=>{ applyRenumber(); renderDiff(); },200);
});
document.getElementById("ed-text").addEventListener("keydown",e=>{
  if(e.key==="Tab"){ e.preventDefault(); indentSel(e.shiftKey?-1:1); return; }
  if(e.key==="Enter"){
    const ta=e.target, v=ta.value, s=ta.selectionStart;
    const ls=v.lastIndexOf("\\n",s-1)+1;
    let le=v.indexOf("\\n",s); if(le<0)le=v.length;
    const m=v.slice(ls,le).match(NUMLINE);
    if(!m) return;
    e.preventDefault();
    if(!(m[3]||"").trim()){
      ta.value=v.slice(0,ls)+v.slice(le);
      ta.setSelectionRange(ls,ls);
    } else {
      const ins="\\n"+m[1]+"0. ";
      ta.value=v.slice(0,s)+ins+v.slice(s);
      ta.setSelectionRange(s+ins.length,s+ins.length);
    }
    applyRenumber(); renderDiff();
  }
});
document.getElementById("num-style").onchange=()=>{ applyRenumber(); renderDiff(); };

function letterOf(n,upper){
  const s=String.fromCharCode(65+((n-1)%26));
  return upper?s:s.toLowerCase();
}
function toRoman(n){
  const t=[[1000,"M"],[900,"CM"],[500,"D"],[400,"CD"],[100,"C"],[90,"XC"],
           [50,"L"],[40,"XL"],[10,"X"],[9,"IX"],[5,"V"],[4,"IV"],[1,"I"]];
  let s="";for(const[v,r]of t){while(n>=v){s+=r;n-=v;}}return s;
}
const NUMLINE=/^(\\s*)((?:\\d+|[IVXLCivxlc]+)(?:\\.\\d+)+|(?:\\d+|[IVXLCivxlc]+|[A-Za-z])\\.)(?:\\s+(.*))?$/;
function normLine(l){ const m=l.match(NUMLINE); return m? m[1]+"#. "+(m[3]||"") : l; }
function renumberText(text){
  const style=document.getElementById("num-style").value;
  let counters=[];
  return text.split("\\n").map(line=>{
    const m=line.match(NUMLINE);
    if(!m){ if(line.trim()!=="")counters=[]; return line; }
    const level=Math.min(Math.floor(m[1].replace(/\\t/g,"  ").length/2),3);
    counters=counters.slice(0,level+1);
    while(counters.length<level+1)counters.push(0);
    counters[counters.length-1]++;
    let num;
    if(style==="roman"){
      const c=counters[counters.length-1];
      num=[toRoman(c),letterOf(c,true),String(c),letterOf(c,false)][Math.min(level,3)]+".";
    } else {
      num=counters.length===1?counters[0]+".":counters.join(".");
    }
    return "  ".repeat(level)+num+" "+(m[3]||"");
  }).join("\\n");
}
function applyRenumber(){
  const ta=document.getElementById("ed-text");
  const old=ta.value, neu=renumberText(old);
  if(old===neu)return;
  const pos=ta.selectionStart;
  const before=old.slice(0,pos);
  const lineIdx=before.split("\\n").length-1;
  const colOld=pos-(before.lastIndexOf("\\n")+1);
  const oldLines=old.split("\\n"), newLines=neu.split("\\n");
  let newPos=0;
  for(let i=0;i<lineIdx;i++)newPos+=newLines[i].length+1;
  const shift=newLines[lineIdx].length-oldLines[lineIdx].length;
  newPos+=Math.max(0,Math.min(newLines[lineIdx].length,colOld+shift));
  ta.value=neu; ta.setSelectionRange(newPos,newPos);
}
function indentSel(delta){
  const ta=document.getElementById("ed-text");
  if(!currentBase)return;
  const v=ta.value, s=ta.selectionStart, e=ta.selectionEnd;
  const ls=v.lastIndexOf("\\n",s-1)+1;
  let le=v.indexOf("\\n",e); if(le<0)le=v.length;
  const block=v.slice(ls,le).split("\\n").map(line=>{
    if(!NUMLINE.test(line))return line;
    if(delta>0)return "  "+line;
    return line.replace(/^ {1,2}/,"");
  }).join("\\n");
  ta.value=v.slice(0,ls)+block+v.slice(le);
  const cur=ls+block.length;
  ta.setSelectionRange(cur,cur);
  applyRenumber(); renderDiff(); ta.focus();
}

function lcsOps(a,b,ka,kb){
  ka=ka||a; kb=kb||b;
  const n=a.length,m=b.length;
  const dp=Array.from({length:n+1},()=>new Int32Array(m+1));
  for(let i=n-1;i>=0;i--)for(let j=m-1;j>=0;j--)
    dp[i][j]=ka[i]===kb[j]?dp[i+1][j+1]+1:Math.max(dp[i+1][j],dp[i][j+1]);
  const ops=[];let i=0,j=0;
  while(i<n&&j<m){
    if(ka[i]===kb[j]){ops.push(["=",b[j]]);i++;j++;}
    else if(dp[i+1][j]>=dp[i][j+1]){ops.push(["-",a[i]]);i++;}
    else{ops.push(["+",b[j]]);j++;}
  }
  while(i<n){ops.push(["-",a[i]]);i++;}
  while(j<m){ops.push(["+",b[j]]);j++;}
  return ops;
}
function lcsLen(a,b){
  const n=a.length,m=b.length;
  if(!n||!m)return 0;
  let prev=new Int32Array(m+1);
  for(let i=n-1;i>=0;i--){
    const cur=new Int32Array(m+1);
    for(let j=m-1;j>=0;j--)
      cur[j]=a[i]===b[j]?prev[j+1]+1:Math.max(prev[j],cur[j+1]);
    prev=cur;
  }
  return prev[0];
}
function simRatio(x,y){
  if(!x.length&&!y.length)return 1;
  return 2*lcsLen([...x],[...y])/(x.length+y.length);
}
function pairRow(oldL,newL){
  const mo=oldL.match(NUMLINE), mn=newL.match(NUMLINE);
  if(mo&&mn){
    const co=mo[3]||"", cn=mn[3]||"";
    const numPart=newL.slice(0,newL.length-cn.length);
    const segs=charSegs(co,cn);
    if(!segs.some(s=>s.t!=="="))return [{t:"=",s:newL}];
    return [{t:"=",s:numPart}].concat(segs);
  }
  return charSegs(oldL,newL);
}
function pairRun(dels,adds){
  const n=dels.length,m=adds.length,TH=0.5;
  const S=dels.map(d=>adds.map(a=>simRatio(normLine(d),normLine(a))));
  const f=Array.from({length:n+1},()=>new Float64Array(m+1));
  for(let i=n-1;i>=0;i--)for(let j=m-1;j>=0;j--){
    let best=Math.max(f[i+1][j],f[i][j+1]);
    if(S[i][j]>=TH)best=Math.max(best,S[i][j]+f[i+1][j+1]);
    f[i][j]=best;
  }
  const rows=[];let i=0,j=0;
  while(i<n&&j<m){
    if(S[i][j]>=TH && Math.abs(f[i][j]-(S[i][j]+f[i+1][j+1]))<1e-9){
      rows.push(pairRow(dels[i],adds[j]));i++;j++;
    } else if(f[i+1][j]>=f[i][j+1]){rows.push([{t:"-",s:dels[i]}]);i++;}
    else{rows.push([{t:"+",s:adds[j]}]);j++;}
  }
  while(i<n){rows.push([{t:"-",s:dels[i]}]);i++;}
  while(j<m){rows.push([{t:"+",s:adds[j]}]);j++;}
  return rows;
}
function charSegs(oldS,newS){
  const ops=lcsOps([...oldS],[...newS]);
  const segs=[];
  for(const[t,c]of ops){
    if(segs.length&&segs[segs.length-1].t===t)segs[segs.length-1].s+=c;
    else segs.push({t:t,s:c});
  }
  return segs;
}
function renderDiff(){
  if(!currentBase)return;
  const a=currentBase.body.split("\\n"), b=document.getElementById("ed-text").value.split("\\n");
  const ops=lcsOps(a,b,a.map(normLine),b.map(normLine));
  const rows=[];let k=0;
  while(k<ops.length){
    if(ops[k][0]==="="){rows.push([{t:"=",s:ops[k][1]}]);k++;continue;}
    const dels=[],adds=[];
    while(k<ops.length&&ops[k][0]==="-"){dels.push(ops[k][1]);k++;}
    while(k<ops.length&&ops[k][0]==="+"){adds.push(ops[k][1]);k++;}
    for(const row of pairRun(dels,adds))rows.push(row);
  }
  let html="",hunks=0,inHunk=false;
  for(const segs of rows){
    const changed=segs.some(s=>s.t!=="=");
    if(changed&&!inHunk){hunks++;inHunk=true;}
    if(!changed)inHunk=false;
    const full=segs.filter(s=>s.t!=="-").map(s=>s.s).join("")||segs.map(s=>s.s).join("");
    let cls="";
    if(/^# /.test(full))cls="dh1"; else if(/^#{2,3} /.test(full))cls="dh2";
    const inner=segs.map(s=>{
      const e=esc(s.s);
      if(s.t==="-")return "<del>"+e+"</del>";
      if(s.t==="+")return "<ins>"+e+"</ins>";
      return e;
    }).join("");
    html+='<div class="'+cls+'">'+(inner||"&nbsp;")+"</div>";
  }
  document.getElementById("diff-view").innerHTML=html;
  document.getElementById("ed-count").textContent=hunks?("改了 "+hunks+" 處"):"尚未改動";
  const et=document.getElementById("ed-title");
  const hd=b.find(l=>/^# /.test(l));
  if(hd&&document.activeElement!==et)et.value=hd.slice(2).trim();
}
function copySaveCmd(){
  let fname=document.getElementById("ed-filename").value.trim()||"new-format.md";
  if(!/\\.md$/.test(fname))fname+=".md";
  const body=document.getElementById("ed-text").value;
  const prompt="請把下面的內容存成 formats/"+fname+"（新的報告格式檔，以 formats/"+
    currentBase.file+" 為基礎修改而來）。內容已定稿：逐字保存，不要改寫、不要補充。"+
    "存檔後照 AGENTS.md：在 formats/INDEX.md 表格尾端追加一列（適用情境照內容摘要一句），"+
    "並重跑 python3 build_viewer.py 更新預覽頁。\\n\\n檔案內容如下：\\n\\n"+body;
  const done=()=>{ document.getElementById("ed-copied").textContent=
    "已複製。切到終端機裡跟 AI 的對話視窗，⌘V 貼上、按 Enter"; };
  if(navigator.clipboard&&navigator.clipboard.writeText){
    navigator.clipboard.writeText(prompt).then(done,()=>fallbackCopy(prompt,done));
  } else { fallbackCopy(prompt,done); }
}

function copyPrompt(){
  const need=document.getElementById("newfmt-text").value.trim();
  const prompt="我要為 talk-to-minutes 設計一個新的報告格式，請照 AGENTS.md「設計新格式」"+
    "的流程處理：先給我草稿確認，確認後存進 formats/、更新 INDEX.md，並重跑 "+
    "build_viewer.py 更新預覽頁。\\n\\n我的需求：\\n"+(need||"（請先訪談我，問清楚情境再設計）");
  const done=()=>{ document.getElementById("copied-msg").textContent=
    "已複製。切到終端機裡跟 AI 的對話視窗，⌘V 貼上、按 Enter";
    document.getElementById("s3").classList.add("on"); };
  if(navigator.clipboard&&navigator.clipboard.writeText){
    navigator.clipboard.writeText(prompt).then(done,()=>fallbackCopy(prompt,done));
  } else { fallbackCopy(prompt,done); }
}
function fallbackCopy(text,done){
  const ta=document.createElement("textarea"); ta.value=text; document.body.appendChild(ta);
  ta.select(); document.execCommand("copy"); ta.remove(); done();
}

const TOUR=[
 {t:"歡迎！先搞懂三個角色",h:
  '<p>這個工具把「會議錄音」變成「你要的格式的報告」。分工是這樣：</p>'+
  '<div class="role"><b>這個網頁</b>：你的儀表板——瀏覽格式、回顧報告、編輯格式。</div>'+
  '<div class="role"><b>你的 AI</b>（Claude Code 或 Codex，跑在終端機裡）：引擎——轉錄音檔、寫報告、存檔。</div>'+
  '<div class="role"><b>formats/ 資料夾</b>：你的格式庫，每個格式一張卡片。</div>'+
  '<div class="kpoint">報告不是在這個網頁生成的。我們需要透過終端機在本地先安裝轉錄引擎 openai-whisper（好處是沒有時長困擾、也沒有訂閱費），再透過「終端機裡面跑的 Claude Code 或 Codex」進行文字到報告的整理——你需要有 ChatGPT 帳號（免費帳號即可用 Codex，額度較小）或 Claude Pro 以上帳號。不用擔心，步驟很簡單，接下來會一步步教你。</div>'},
 {t:"第一次使用：裝好轉錄引擎（只做一次）",h:
  '<p><b>Whisper 是什麼？</b>OpenAI 開源的語音辨識工具，把說話聲轉成文字。它<b>在你自己的電腦上跑</b>，免費、沒有字數限制、錄音檔不會上傳到任何地方。（之後 AI 整理報告時，送出去的只有轉好的文字，就像你平常貼文字給 AI 一樣——聲音永遠留在本機。）</p>'+
  '<p><b>需要什麼電腦？</b>一台還能跑現行 macOS 的 Mac 就行。越新越快；很舊或記憶體小的機器也能用，只是長錄音轉得慢一點。Apple 晶片（M 系列）最順。</p>'+
  '<div class="cmd-label">① 先裝 Homebrew（macOS 的軟體安裝器）：到 <a href="https://brew.sh">brew.sh</a> 照首頁指令貼一次。已經有就跳過。</div>'+
  '<div class="cmd-label">② 裝 Whisper 本體，複製這行貼到終端機執行：</div>'+
  '<div class="cmd-row"><span class="cmd">brew install ffmpeg openai-whisper</span><button class="cmd-copy" onclick="copyCmd(this)">複製</button></div>'+
  '<div class="cmd-label">③ 還沒有 AI 助手？裝一個（擇一即可，先執行 <span style="font-family:ui-monospace,Menlo,monospace">brew install node</span>）：</div>'+
  '<div class="cmd-label" style="margin-top:6px;">Claude Code（需 Claude Pro 以上方案）：</div>'+
  '<div class="cmd-row"><span class="cmd">npm install -g @anthropic-ai/claude-code</span><button class="cmd-copy" onclick="copyCmd(this)">複製</button></div>'+
  '<div class="cmd-label">Codex（ChatGPT 免費帳號即可，付費方案額度較大）：</div>'+
  '<div class="cmd-row"><span class="cmd">npm install -g @openai/codex</span><button class="cmd-copy" onclick="copyCmd(this)">複製</button></div>'+
  '<p style="font-size:14px;color:var(--muted);margin:6px 0 0;">裝好後第一次啟動會請你登入帳號（瀏覽器跳出授權），用你既有的訂閱、不用另外付 API 費。</p>'+
  '<div class="kpoint">怎麼確認裝好了？安裝跑完最後幾行會出現 🍺 圖示（例如「🍺 /opt/homebrew/Cellar/openai-whisper/…」）就代表裝好了。想再確認：打 <span style="font-family:ui-monospace,Menlo,monospace">which whisper</span> 按 Enter，有跳出一行路徑（如 /opt/homebrew/bin/whisper）就 OK。</div>'},
 {t:"跑出你的第一份報告",h:
  '<p><b>1. 進到 talk-to-minutes 資料夾。</b>打開「終端機」(Terminal) app，照下面的動畫做：<b>資料夾和檔案可以直接拖進終端機，路徑會自動打好</b>，完全不用手打：</p>'+
  '<div class="dragdemo">'+
  '<div class="dd-finder"><div class="dd-bar">Finder</div><div class="dd-file">📁 talk-to-minutes</div></div>'+
  '<div class="dd-ghost">📁 talk-to-minutes</div>'+
  '<div class="dd-term"><span class="p">%</span> cd <span class="dd-path">/Users/你/任何位置/talk-to-minutes</span><span class="dd-hint-enter">按 Enter ⏎</span></div>'+
  '</div>'+
  '<div class="dd-cap"><span><b>①</b> 在黑色視窗打 cd＋一個空格</span><span><b>②</b> 把資料夾從 Finder 拖進黑色視窗</span><span><b>③</b> 路徑自動出現 → 按 Enter</span></div>'+
  '<p><b>2. 依據你想用 Claude Code 或 Codex 來整理你的報告，在終端機複製以下指令並貼上：</b></p>'+
  '<div class="cmd-label">用 Claude Code：</div>'+
  '<div class="cmd-row"><span class="cmd">claude</span><button class="cmd-copy" onclick="copyCmd(this)">複製</button></div>'+
  '<div class="cmd-label">用 Codex：</div>'+
  '<div class="cmd-row"><span class="cmd">codex</span><button class="cmd-copy" onclick="copyCmd(this)">複製</button></div>'+
  '<p style="margin-top:12px;"><b>3. 給它錄音檔——同一招，拖就好：</b></p>'+
  '<div class="dragdemo">'+
  '<div class="dd-finder"><div class="dd-bar">Finder</div><div class="dd-file">🎵 會議錄音.m4a</div></div>'+
  '<div class="dd-ghost">🎵 會議錄音.m4a</div>'+
  '<div class="dd-term"><span class="p">›</span> 幫我把這個錄音做成報告：<span class="dd-path">/Users/你/Downloads/會議錄音.m4a</span><span class="dd-hint-enter">按 Enter ⏎</span></div>'+
  '</div>'+
  '<div class="dd-cap"><span><b>①</b> 對 AI 打「幫我把這個錄音做成報告：」</span><span><b>②</b> 把錄音檔拖進視窗</span><span><b>③</b> 路徑自動出現 → 按 Enter</span></div>'+
  '<p><b>4. 選格式、完成。</b>AI 轉錄後會問你要哪個格式，選好它就寫好、存檔（錄音檔全程留在本機，只有逐字稿文字交給你的 AI 整理）。回到本頁按重新整理，報告就掛在對應格式的卡片下面。</p>'+
  ''},
 {t:"看格式、看報告",h:
  '<p>每張白色卡片是一個報告格式：</p>'+
  '<div class="role"><b>滑鼠停上去</b>：旁邊浮出放大版（滑鼠留在卡片上滾滾輪可以捲動它）。</div>'+
  '<div class="role"><b>點卡片</b>：打開完整的格式定義。</div>'+
  '<div class="role"><b>卡片下方的清單</b>：用這個格式整理過的所有報告，點檔名直接看內容。</div>'+
  '<div class="kpoint">選格式的邏輯：看「這份報告要給誰」——給自己留檔用通用紀要、給團隊同步用客戶會議、給主管看用一頁簡報。</div>'+
  '<p>或是自定義會議記錄格式（見下頁）。</p>'},
 {t:"改格式、創造你自己的格式",h:
  '<p>最右邊的虛線「＋設計新格式」卡片，兩條路：</p>'+
  '<div class="role"><b>以現有格式為底</b>（最常用）：左右對照編輯器——右邊直接改，左邊即時顯示紅刪除線（刪）和綠字（增），編號自動重排。改完按「複製存檔指令」。</div>'+
  '<div class="role"><b>從零開始</b>：描述情境（給誰看、開什麼會），按「複製交辦指令」，讓 AI 幫你設計。</div>'+
  '<p>複製之後，切回<b>第 3 步啟動 AI 的那個終端機視窗</b>，⌘V 貼上、按 Enter——格式就存好了。</p>'+
  '<div class="kpoint">存好的格式會變成新卡片，下次開會直接點選。</div>'+
  '<p style="margin-top:10px;">隨時想重看這份導覽，按右上角「怎麼使用？」。</p>'}
];
let tstep=0;
function showTour(i){
  tstep=Math.max(0,Math.min(TOUR.length-1,i));
  document.getElementById("tour-title").textContent=(tstep+1)+" / "+TOUR.length+"　"+TOUR[tstep].t;
  document.getElementById("tour-body").innerHTML=TOUR[tstep].h;
  document.getElementById("tdots").innerHTML=TOUR.map((_,x)=>
    '<div class="tdot'+(x===tstep?" on":"")+'"></div>').join("");
  document.getElementById("t-prev").style.visibility=tstep===0?"hidden":"visible";
  document.getElementById("t-next").textContent=tstep===TOUR.length-1?"開始使用":"下一步";
}
function tourNext(){
  if(tstep>=TOUR.length-1){ document.getElementById("tour").close(); return; }
  showTour(tstep+1);
}
function openTour(){ document.getElementById("tour").showModal(); showTour(0); }
function copyCmd(btn){
  const el=btn.parentElement.querySelector(".cmd");
  const text=el?el.textContent:"";
  const done=()=>{ btn.textContent="已複製 ✓"; setTimeout(()=>{ btn.textContent="複製"; },1500); };
  if(navigator.clipboard&&navigator.clipboard.writeText){
    navigator.clipboard.writeText(text).then(done,()=>fallbackCopy(text,done));
  } else { fallbackCopy(text,done); }
}
document.getElementById("tour").addEventListener("close",
  ()=>localStorage.setItem("t2m_tour","2"));
if(localStorage.getItem("t2m_tour")!=="2") openTour();
</script>
</body>
</html>
"""

(ROOT / "app").mkdir(exist_ok=True)
out = ROOT / "app" / "index.html"
out.write_text(TEMPLATE.replace("__DATA__", data), encoding="utf-8")
print(f"已更新 {out}（格式 {len(formats)} 個、報告 {len(reports)} 份）")
