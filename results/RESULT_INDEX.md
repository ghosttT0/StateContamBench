# Result-to-Paper Index

This index records why each frozen run family is bundled and how it may be used. 
All pre-fix rows are descriptive because they lack exact input and replay hashes.

| Family | Files | Paper role | Evidence status |
|---|---:|---|---|
| Qwen3-14B None/G3/TAME, clean, ablations | 15 | Primary audit and write-path tables | Zero unknown; legacy unpaired |
| Qwen2.5-7B None/G3/TAME, clean, ablations | 15 | Detector-ceiling boundary and cross-model screen | Zero unknown; legacy unpaired |
| GPT-5.4 None/TAME | 4 | Cross-model raw screen | Zero unknown; no clean counterpart |
| DeepSeek-V4-Pro complete cleanrun None/TAME | 4 | Coverage-qualified cross-model screen | 251 any-window unknown rows and 179 W4 unknowns |
| Claude-Sonnet-5 None/TAME | 4 | Coverage-qualified cross-model screen | 3 any-window unknown rows and 1 W4 unknown |
| GLM-5.2 None/TAME | 4 | Coverage-qualified cross-model screen | 115 any-window unknown rows and 57 W4 unknowns |
| Historical carrier and task baselines | 4 | S0--S4, payload, and task characterization | Zero unknown; legacy unpaired |
| Trigger-distance sweep | 6 | Persistence robustness figure | Zero unknown; legacy unpaired |
| Surface-variant sweep | 12 | Paraphrase/indirect/low-key/retrieval-friendly robustness table | Zero unknown; legacy unpaired |
| Historical G1/G2/G3/G4/TAME and clean runs | 10 | Supplemental baseline table | Zero unknown; legacy unpaired |
| Historical TAME component ablations | 3 | Supplemental ablation context | Zero unknown; legacy unpaired |
| Historical real G3 and clean extensions | 4 | Supplemental real-log context | Zero unknown; legacy unpaired |
| Duplicate DeepSeek real TAME output | 1 | None; preserved for provenance only | Quarantined: 480 rows, 208 unique keys |

The four complete DeepSeek-V4-Pro `cleanrun` files are bundled. Partial,
NUL-corrupted, and duplicate early attempts are not evidence and are
intentionally excluded. The paper counts unknown W4 outputs as attack-direction
errors; the audit also reports valid-output DASR, W4 U/N, and an all-N lower bound.
