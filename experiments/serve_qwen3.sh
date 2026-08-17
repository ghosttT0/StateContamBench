#!/usr/bin/env bash
set -euo pipefail

: "${MODEL_PATH:?Set MODEL_PATH to the local Qwen3-14B directory}"
PORT="${PORT:-8000}"

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

vllm serve "$MODEL_PATH" \
  --host 127.0.0.1 \
  --port "$PORT" \
  --served-model-name Qwen3-14B \
  --max-model-len 16384 \
  --gpu-memory-utilization 0.92 \
  --quantization fp8 \
  --chat-template "$ROOT/experiments/qwen3_no_thinking.jinja"
