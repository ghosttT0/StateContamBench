# Artifact Scope and Claim Boundary

## Supported by Frozen Rows

- Raw attack-direction error (DASR) and clean W4 accuracy.
- Carrier-index contamination indicators and model reasons in attacked rows.
- Qwen3 None/G3/TAME and component-ablation descriptive comparisons.
- Qwen2.5 None/G3/TAME, clean-capability, and component-ablation screens.
- Six-family cross-model attacked screens, including unknown-aware denominators
  for Claude-Sonnet-5, GLM-5.2, and DeepSeek-V4-Pro.
- Historical all-carrier, payload-sensitivity, task-sensitivity,
  trigger-distance, surface-variant, write-path, and cross-model screens.
- Every value regenerated in `PAPER_EVIDENCE_REPORT.md` and
  `SUPPLEMENTAL_EVIDENCE_REPORT.md`, subject to the evidence boundaries below.

## Not Supported by Frozen Rows

- A causal PDCR for the legacy Qwen3 outputs.
- Verified W4 replay for legacy S3 rows: the old output records index
  contamination, not the exact top-k hit list shown to the model.
- Real-104 attacked/clean subtraction: attacked uses `n-per-type=8`, whereas
  clean uses `n-per-type=4` and is a different draw.
- Exact method-effect significance for old separate-process runs: their source
  streams were not fingerprinted and the old synthetic RNG was not frozen.
- Provider-wide or deployment-wide generalization from the cross-model screen.
- Direct ranking of unknown-bearing models against zero-unknown models; their
  valid-output DASR is conditional on W4 coverage.
- Any aggregate from `results/quarantined/guard_real8_items.jsonl`, whose 480
  rows collapse to 208 duplicate sequence-carrier keys.

## Required Before a Causal Claim

1. Run `experiments/run_qwen3_exact_controls.sh` using the same model revision.
2. Confirm row-level source, trigger, prompt-scope, and replay-state hashes.
3. Compute PDCR only for pairs whose non-injected source streams match and
   whose W4 trace records payload-derived replay.
4. Preserve the resulting JSONL files, model revision, environment, and hashes.
