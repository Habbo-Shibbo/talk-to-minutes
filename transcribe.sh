#!/bin/bash
# 會議錄音轉逐字稿
# 用法: ./transcribe.sh <音檔路徑> [語言]
# 語言預設 Chinese；英文會議用: ./transcribe.sh 檔案.m4a English
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "用法: $0 <音檔路徑> [語言]" >&2
  exit 1
fi

AUDIO="$1"
LANG_OPT="${2:-Chinese}"

if [ ! -f "$AUDIO" ]; then
  echo "找不到檔案: $AUDIO" >&2
  exit 1
fi

DIR="$(cd "$(dirname "$0")" && pwd)"
OUT="$DIR/transcripts"
mkdir -p "$OUT"

PROMPT=""
if [ "$LANG_OPT" = "Chinese" ]; then
  PROMPT="以下是繁體中文的會議內容。"
fi

whisper "$AUDIO" \
  --model turbo \
  --language "$LANG_OPT" \
  --output_format txt \
  --output_dir "$OUT" \
  ${PROMPT:+--initial_prompt "$PROMPT"}

BASE="$(basename "$AUDIO")"
echo ""
echo "逐字稿完成: $OUT/${BASE%.*}.txt"
