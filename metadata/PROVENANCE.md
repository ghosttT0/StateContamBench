# Provenance Record

The package was assembled from a clean source-and-results snapshot plus the
anonymous manuscript's current plotting sources. Git history and repository
remote metadata were intentionally excluded for double-blind review.

The frozen Qwen3 run records the following run-level configuration:

- served model name: `Qwen3-14B`
- inference server: vLLM 0.10.2
- quantization: FP8
- maximum model length: 16,384
- request temperature: 0.0
- request seed: 7
- request maximum output tokens: 2,048
- thinking output: disabled by `experiments/qwen3_no_thinking.jinja`

The original server log contained machine-local absolute paths and terminal
control sequences. It is excluded; `qwen3_vllm_server.sanitized.log` retains
the configuration-bearing lines with local paths replaced.

The legacy JSONL rows do not contain a model revision or input hashes. That
absence is surfaced by the validator and is not repaired retroactively.
