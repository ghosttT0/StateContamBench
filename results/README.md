# Frozen Result Files

## Primary Qwen3-14B

- `qwen3_syn_items.jsonl`, `qwen3_real8_none_items.jsonl`: unprotected attacked
- `qwen3_method_g3_items.jsonl`, `qwen3_real8_g3_items.jsonl`: G3 attacked
- `qwen3_guard_syn_items.jsonl`, `qwen3_guard_real8_items.jsonl`: TAME attacked
- `qwen3_*clean*.jsonl`: clean capability slices
- `qwen3_tame_ablate_*.jsonl`: synthetic TAME ablations

The real attacked files contain 104 rows per carrier; the real clean files
contain 52 rows per carrier and are not paired controls.

## Descriptive Screens

- `gpt54_*`: zero-unknown cross-model raw-error screen used in the paper
- `v4pro_*_cleanrun_*`: complete DeepSeek-V4-Pro cross-model files; partial and
  NUL-corrupted attempts are excluded
- `qwen_*`: Qwen2.5-7B None/G3/TAME, clean-capability, and ablation screens
- `claude5_*`, `glm52_*`: unknown-aware cross-model screens used in the paper
- `items.jsonl`, `real8_none_items.jsonl`: historical all-carrier screen
- `ioc_*`: historical task-sensitivity screens
- `distance_*`: W1/W2/W3 trigger-distance sweep
- `var_*`: paraphrase, indirect, low-key, and retrieval-friendly surface sweep
- `gate_*`, `method_*`, `guard_*`, and `tame_ablate_*`: historical write-path,
  clean-capability, and TAME component screens
- `mechanism_*.json`: carrier mechanism summaries

Unknown-bearing cross-model files are scored on known W4 outputs and report
`U/N` beside every score; the generated evidence report also gives the
historical all-N lower bound. These files are retained only for the descriptive
claims identified in the paper or supplemental evidence report.
`RESULT_INDEX.md` maps every run family to that role.
`quarantined/guard_real8_items.jsonl` is preserved for provenance
but excluded from all aggregates because it contains duplicate `(sid, mode)`
keys. Run `python experiments/validate_artifact.py` to regenerate both evidence
reports and the integrity manifest.
