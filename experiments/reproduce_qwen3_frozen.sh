#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

export DEEPSEEK_BASE_URL="${DEEPSEEK_BASE_URL:-http://127.0.0.1:8000/v1}"
export DEEPSEEK_MODEL="${DEEPSEEK_MODEL:-Qwen3-14B}"
export DEEPSEEK_API_KEY="${DEEPSEEK_API_KEY:-EMPTY}"
export MODEL_REVISION="${MODEL_REVISION:-unspecified}"
unset DEEPSEEK_REASONING_EFFORT

OUT="$ROOT/results/reproduced_frozen"
mkdir -p "$OUT"

run() { python3 experiments/run_all.py "$@"; }

run --modes S1,S3 --output "$OUT/qwen3_syn_items.jsonl"
run --method G3 --modes S1,S3 --output "$OUT/qwen3_method_g3_items.jsonl"
run --guard --modes S1,S3 --output "$OUT/qwen3_guard_syn_items.jsonl"
run --dataset real --n-per-type 8 --modes S1,S3 --output "$OUT/qwen3_real8_none_items.jsonl"
run --dataset real --method G3 --n-per-type 8 --modes S1,S3 --output "$OUT/qwen3_real8_g3_items.jsonl"
run --dataset real --guard --n-per-type 8 --modes S1,S3 --output "$OUT/qwen3_guard_real8_items.jsonl"

run --clean --modes S1,S3 --output "$OUT/qwen3_clean_syn_none_items.jsonl"
run --clean --method G3 --modes S1,S3 --output "$OUT/qwen3_clean_syn_g3_items.jsonl"
run --guard --clean --modes S1,S3 --output "$OUT/qwen3_guard_syn_clean_items.jsonl"
run --dataset real --clean --n-per-type 4 --modes S1,S3 --output "$OUT/qwen3_real_clean_mixed_s13_items.jsonl"
run --dataset real --method G3 --clean --n-per-type 4 --modes S1,S3 --output "$OUT/qwen3_real_clean_mixed_g3_s13_items.jsonl"
run --dataset real --guard --clean --n-per-type 4 --modes S1,S3 --output "$OUT/qwen3_guard_real_clean_items.jsonl"

run --guard --no-tame-triage --modes S1,S3 --output "$OUT/qwen3_tame_ablate_no_triage_items.jsonl"
run --guard --no-tame-decoupling --modes S1,S3 --output "$OUT/qwen3_tame_ablate_no_decouple_items.jsonl"
run --guard --no-tame-cache-split --modes S1,S3 --output "$OUT/qwen3_tame_ablate_no_cache_items.jsonl"

echo "Historical recipe complete: $OUT"
echo "The real clean slice is intentionally n-per-type=4 and is not an exact control."
