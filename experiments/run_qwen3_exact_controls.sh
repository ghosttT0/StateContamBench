#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

export DEEPSEEK_BASE_URL="${DEEPSEEK_BASE_URL:-http://127.0.0.1:8000/v1}"
export DEEPSEEK_MODEL="${DEEPSEEK_MODEL:-Qwen3-14B}"
export DEEPSEEK_API_KEY="${DEEPSEEK_API_KEY:-EMPTY}"
export MODEL_REVISION="${MODEL_REVISION:-unspecified}"
unset DEEPSEEK_REASONING_EFFORT

OUT="$ROOT/results/reproduced_exact"
mkdir -p "$OUT"

run_pair() {
  local stem="$1"
  shift
  python3 experiments/run_all.py "$@" --modes S1,S3 --output "$OUT/${stem}_attacked.jsonl"
  python3 experiments/run_all.py "$@" --clean --modes S1,S3 --output "$OUT/${stem}_clean.jsonl"
}

# The fixed generator makes separate invocations byte-stable and records hashes.
run_pair qwen3_syn_none
run_pair qwen3_syn_g3 --method G3
run_pair qwen3_syn_tame --guard
run_pair qwen3_real104_none --dataset real --n-per-type 8
run_pair qwen3_real104_g3 --dataset real --n-per-type 8 --method G3
run_pair qwen3_real104_tame --dataset real --n-per-type 8 --guard

echo "Exact-control run complete: $OUT"
echo "Verify sequence_sha256/trigger_sha256 before computing PDCR."
