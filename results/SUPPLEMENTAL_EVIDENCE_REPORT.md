# Supplemental Evidence Report

All values below are regenerated from the bundled JSONL rows. These run 
families predate row-level input fingerprints and therefore support only 
descriptive raw-error, robustness, utility, and capability analyses.

## Trigger Distance

| Injection | Distance to W4 | S1 None | S1 TAME | S3 None | S3 TAME |
|---|---:|---:|---:|---:|---:|
| W1 | 3 | 45.8% | 18.8% | 41.7% | 10.4% |
| W2 | 2 | 45.8% | 25.0% | 37.5% | 8.3% |
| W3 | 1 | 47.9% | 22.9% | 37.5% | 10.4% |

## Surface Variants

| Variant | S1 None | S1 G1 | S1 G3 | S3 None | S3 G1 | S3 G3 |
|---|---:|---:|---:|---:|---:|---:|
| paraphrase | 33.3% | 12.5% | 20.8% | 16.7% | 8.3% | 16.7% |
| indirect | 20.8% | 8.3% | 20.8% | 16.7% | 8.3% | 12.5% |
| low-key | 8.3% | 25.0% | 12.5% | 8.3% | 12.5% | 8.3% |
| retrfriendly | 25.0% | 16.7% | 16.7% | 4.2% | 12.5% | 4.2% |

## Task Sensitivity

| Dataset | Task | S1 None | S3 None |
|---|---|---:|---:|
| Synthetic | Verdict | 45.8% | 39.6% |
| Synthetic | IOC | 35.4% | 33.3% |
| Real-104 | Verdict | 77.9% | 81.7% |
| Real-52 | IOC | 78.8% | 88.5% |

## Historical Synthetic Write-Path Baselines

| Carrier | None | G1 | G2 | G3 | G4 | TAME |
|---|---:|---:|---:|---:|---:|---:|
| S1 | 45.8% | 8.3% | 10.4% | 18.8% | 45.8% | 10.4% |
| S3 | 39.6% | 8.3% | 8.3% | 10.4% | 43.8% | 8.3% |

### Clean W4 Accuracy

| Carrier | None | G1 | G3 | G4 | TAME |
|---|---:|---:|---:|---:|---:|
| S1 | 91.7% | 89.6% | 81.2% | 87.5% | 89.6% |
| S3 | 89.6% | 91.7% | 87.5% | 91.7% | 93.8% |

## Historical Real-Log G3 Screen

The attacked TAME file for this historical slice is unavailable because its 
duplicate keys are quarantined below. The remaining rows still document the 
raw G3 screen and the separate clean capability slices.

| Carrier | None raw | G3 raw | None clean ACC | G3 clean ACC | TAME clean ACC |
|---|---:|---:|---:|---:|---:|
| S1 | 77.9% | 50.0% | 65.4% | 51.9% | 63.5% |
| S3 | 81.7% | 52.9% | 50.0% | 51.9% | 48.1% |

## Historical TAME Component Ablation

| Carrier | Full TAME | No triage | No decoupling | No cache |
|---|---:|---:|---:|---:|
| S1 | 10.4% | 22.9% | 43.8% | 14.6% |
| S3 | 8.3% | 10.4% | 45.8% | 16.7% |

## Qwen2.5-7B Detector-Ceiling Screen

| Dataset | Carrier | None | G3 | TAME | Clean ACC |
|---|---|---:|---:|---:|---:|
| Synthetic | S1 | 75.0% | 75.0% | 77.1% | 25.0% |
| Synthetic | S3 | 75.0% | 75.0% | 75.0% | 25.0% |
| Real-104 | S1 | 83.7% | 73.1% | 72.1% | 19.2% |
| Real-104 | S3 | 73.1% | 75.0% | 75.0% | 25.0% |

### Qwen2.5-7B TAME Component Ablation

| Carrier | Full TAME | No triage | No decoupling | No cache |
|---|---:|---:|---:|---:|
| S1 | 77.1% | 75.0% | 75.0% | 75.0% |
| S3 | 75.0% | 75.0% | 75.0% | 75.0% |

## Quarantined Legacy Output

`results/quarantined/guard_real8_items.jsonl` is preserved as an original 
artifact but excluded from every paper aggregate: it contains 480 rows for only 
208 unique `(sid, mode)` keys, with each key repeated two or three times.
