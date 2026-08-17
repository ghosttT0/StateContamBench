# StateContamBench Anonymous Review Artifact

Anonymous review mirror:
<https://anonymous.4open.science/r/StateContamBench-8D36/>

This artifact accompanies the submission on delayed state contamination in
LLM-based security-log analysis. It contains the benchmark implementation,
frozen result rows used by the paper and its supplemental screens, a Qwen3-14B
execution recipe, source data for the paper figures, and integrity checks that
recompute the reported values.

The cross-model screen retains all six analyzer families. For runs with unknown
W4 outputs, it reports valid-output DASR together with `U/N` and an all-N lower
bound; unknown responses are never silently counted as non-attacks.

## Important Evidence Status

The frozen Qwen3 files predate the deterministic dataset fix included in this
artifact. Their attacked and clean slices have identical `(sid, mode)` key sets,
but the old synthetic generator used process-random nuisance fields. Those rows
therefore support raw error rates, clean accuracy, carrier-index contamination,
and key-aligned diagnostics, but **not an exact paired causal rate**.

The corrected generator now:

- uses a stable per-sequence random-number generator;
- uses a stable SHA-256-derived payload seed instead of Python's salted `hash()`;
- records sequence and trigger hashes in every newly generated result row; and
- provides a recipe that reruns attacked and clean conditions from identical
  source streams and records the exact replay state in new rows. Legacy rows do
  not retain the W4 top-k hit content.

The paper reports these legacy runs as descriptive raw-error and capability
screens, not as paired causal estimates. The exact-control recipe supports a
future PDCR extension without invalidating the bundled descriptive evidence.

## Directory Map

```text
loginject/       Benchmark, state carriers, TAME, evaluation, provenance
experiments/     Smoke test, audit, plotting, and frozen/repaired run recipes
results/         Frozen JSONL rows used by the paper and generated audit report
metadata/        Run provenance, sanitized server log, hashes, and manifests
figures/         Figure source data and regenerable outputs
paper/           Anonymous manuscript source snapshot
```

Excluded intentionally: API credentials, `.env` files, model weights, caches,
download logs, Python bytecode, Git history, local preview images, and duplicate
TIFF exports.

## Quick Validation (No Model or Network)

Python 3.11 or newer is recommended.

```bash
python -m pip install -r requirements.txt
python experiments/smoke.py
python experiments/validate_artifact.py
```

The audit writes or refreshes:

- `results/PAPER_EVIDENCE_REPORT.md`;
- `results/SUPPLEMENTAL_EVIDENCE_REPORT.md`;
- `results/RESULT_INDEX.md`;
- `metadata/synthetic_pair_manifest.jsonl`; and
- `metadata/ARTIFACT_MANIFEST.json`.

Expected primary frozen values include raw Qwen3 DASR of 70.8%/68.8% on
synthetic S1/S3 and 81.7%/61.5% on real S1/S3. The audit deliberately reports
PDCR as unavailable for these legacy rows because they lack input hashes.

## Reproduce the Frozen Qwen3 Configuration

The recorded environment used Qwen3-14B, vLLM 0.10.2, FP8 quantization, a
16,384-token context, temperature 0, seed 7, and the supplied no-thinking chat
template. Start a compatible server with a local model path:

```bash
export MODEL_PATH=/path/to/Qwen3-14B
export MODEL_REVISION=exact-model-commit-or-checksum
bash experiments/serve_qwen3.sh
```

In another shell, run the historical recipe without overwriting frozen files:

```bash
export MODEL_REVISION=exact-model-commit-or-checksum
bash experiments/reproduce_qwen3_frozen.sh
```

This reproduces the original sampling depths, including the non-identical
real clean slice (`n-per-type=4` versus attacked `n-per-type=8`).

## Generate Exact Controls

For causal measurement, rerun both attacked and clean conditions with the
corrected deterministic generator:

```bash
export MODEL_REVISION=exact-model-commit-or-checksum
bash experiments/run_qwen3_exact_controls.sh
```

Outputs are written under `results/reproduced_exact/`. Set `MODEL_REVISION` in
the runner shell to the exact model commit or checksum. Each row records the
model revision, decoding settings, `sequence_sha256`,
`control_sequence_sha256`, and `trigger_sha256`. A valid attacked/clean pair
must have the same control and trigger hashes; the attacked sequence hash is
expected to differ because it includes lines marked `injected=true`.

## Real-Log Data

Real-log construction uses the public upstream
`ait-aecid/log-interpretation-prompt-injection` dataset. Either let the loader
clone it into `.external/` or point to an existing checkout:

```bash
export AIT_LOGINJECT_REPO=/path/to/log-interpretation-prompt-injection
python -c "from loginject.real_dataset import ensure_repo; print(ensure_repo())"
```

The upstream dataset is not redistributed here. Its own license and access
terms apply.

## Paper and Figures

Regenerate the quantitative paper figures with:

```bash
python experiments/plot_paper_figures.py
python experiments/plot_benchmark_example.py
```

Build the anonymous manuscript from `paper/` with:

```bash
cd paper
latexmk -pdf -interaction=nonstopmode -halt-on-error state_contamination_usenix2027_draft.tex
```

## Review-Phase Availability

This directory is a review package, not a public release. No open-source license
is granted by this copy. A stable public release and explicit license must be
provided if the paper is accepted.
