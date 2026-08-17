"""Validate supplemental frozen runs and regenerate descriptive paper tables."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


def load_jsonl(filename: str) -> list[dict]:
    path = RESULTS / filename
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise AssertionError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
    return rows


def specifications() -> dict[str, tuple[str, int]]:
    specs = {
        "legacy-clean-syn-none": ("clean_syn_none_items.jsonl", 240),
        "legacy-clean-syn-g1": ("clean_syn_g1_items.jsonl", 192),
        "legacy-clean-syn-g3": ("clean_syn_g3_items.jsonl", 192),
        "legacy-clean-syn-g4": ("clean_syn_g4_items.jsonl", 192),
        "legacy-syn-g1": ("gate_g1_items.jsonl", 240),
        "legacy-syn-g2": ("gate_g2_items.jsonl", 240),
        "legacy-syn-g3": ("method_g3_items.jsonl", 192),
        "legacy-syn-g4": ("method_g4_items.jsonl", 192),
        "legacy-syn-tame": ("guard_syn_final_items.jsonl", 96),
        "legacy-clean-syn-tame": ("guard_syn_clean_final_items.jsonl", 96),
        "legacy-real-g3": ("real8_g3_items.jsonl", 208),
        "legacy-clean-real-none": ("real_clean_mixed_s13_items.jsonl", 104),
        "legacy-clean-real-g3": ("real_clean_mixed_g3_s13_items.jsonl", 104),
        "legacy-clean-real-tame": ("guard_real_clean_final_items.jsonl", 104),
        "legacy-ioc-syn": ("ioc_syn_none_items.jsonl", 96),
        "legacy-ablate-triage": ("tame_ablate_no_triage_items.jsonl", 96),
        "legacy-ablate-decouple": ("tame_ablate_no_decouple_items.jsonl", 96),
        "legacy-ablate-cache": ("tame_ablate_no_cache_items.jsonl", 96),
    }
    for window in (1, 2, 3):
        for method in ("none", "tame"):
            specs[f"distance-w{window}-{method}"] = (
                f"distance_syn_w{window}_{method}.jsonl", 96
            )
    for variant in ("indirect", "low-key", "paraphrase", "retrfriendly"):
        for method in ("none", "G1", "G3"):
            specs[f"variant-{variant}-{method}"] = (
                f"var_{variant}_{method}.jsonl", 48
            )
    qwen_specs = {
        "qwen25-syn-none": ("qwen_syn_items.jsonl", 240),
        "qwen25-syn-g3": ("qwen_method_g3_items.jsonl", 96),
        "qwen25-syn-tame": ("qwen_guard_syn_items.jsonl", 96),
        "qwen25-real-none": ("qwen_real8_none_items.jsonl", 208),
        "qwen25-real-g3": ("qwen_real8_g3_items.jsonl", 208),
        "qwen25-real-tame": ("qwen_guard_real8_items.jsonl", 208),
        "qwen25-clean-syn-none": ("qwen_clean_syn_none_items.jsonl", 96),
        "qwen25-clean-syn-g3": ("qwen_clean_syn_g3_items.jsonl", 96),
        "qwen25-clean-syn-tame": ("qwen_guard_syn_clean_items.jsonl", 96),
        "qwen25-clean-real-none": ("qwen_real_clean_mixed_s13_items.jsonl", 104),
        "qwen25-clean-real-g3": ("qwen_real_clean_mixed_g3_s13_items.jsonl", 104),
        "qwen25-clean-real-tame": ("qwen_guard_real_clean_items.jsonl", 104),
        "qwen25-ablate-triage": ("qwen_tame_ablate_no_triage_items.jsonl", 96),
        "qwen25-ablate-decouple": ("qwen_tame_ablate_no_decouple_items.jsonl", 96),
        "qwen25-ablate-cache": ("qwen_tame_ablate_no_cache_items.jsonl", 96),
    }
    specs.update(qwen_specs)
    return specs


def check_rows(label: str, rows: list[dict], expected: int) -> dict:
    keys = [(row["sid"], row["mode"]) for row in rows]
    unknown = sum(
        any(row.get(f"w{i}_verdict") == "unknown" for i in (1, 2, 3, 4))
        for row in rows
    )
    assert len(rows) == expected, f"{label}: expected {expected}, found {len(rows)}"
    assert len(set(keys)) == expected, f"{label}: duplicate sequence-carrier keys"
    assert unknown == 0, f"{label}: {unknown} rows contain unknown verdicts"
    return {
        "rows": len(rows),
        "unique_keys": len(set(keys)),
        "unknown_rows": unknown,
        "rows_missing_input_provenance": sum(
            "sequence_sha256" not in row for row in rows
        ),
    }


def rate(rows: list[dict], mode: str, field: str = "DASR") -> float:
    selected = [row for row in rows if row["mode"] == mode]
    assert selected, f"no {mode} rows"
    return 100 * sum(float(row[field]) for row in selected) / len(selected)


def accuracy(rows: list[dict], mode: str) -> float:
    selected = [row for row in rows if row["mode"] == mode]
    assert selected, f"no {mode} rows"
    return 100 * sum(
        row["w4_verdict"] == row["w4_expected"] for row in selected
    ) / len(selected)


def f(value: float) -> str:
    return f"{value:.1f}%"


def write_report(cache: dict[str, list[dict]]) -> None:
    get = lambda filename: cache[filename]
    lines = [
        "# Supplemental Evidence Report",
        "",
        "All values below are regenerated from the bundled JSONL rows. These run ",
        "families predate row-level input fingerprints and therefore support only ",
        "descriptive raw-error, robustness, utility, and capability analyses.",
        "",
        "## Trigger Distance",
        "",
        "| Injection | Distance to W4 | S1 None | S1 TAME | S3 None | S3 TAME |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for window, distance in ((1, 3), (2, 2), (3, 1)):
        none = get(f"distance_syn_w{window}_none.jsonl")
        tame = get(f"distance_syn_w{window}_tame.jsonl")
        lines.append(
            f"| W{window} | {distance} | {f(rate(none, 'S1'))} | "
            f"{f(rate(tame, 'S1'))} | {f(rate(none, 'S3'))} | "
            f"{f(rate(tame, 'S3'))} |"
        )

    lines += [
        "",
        "## Surface Variants",
        "",
        "| Variant | S1 None | S1 G1 | S1 G3 | S3 None | S3 G1 | S3 G3 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for variant in ("paraphrase", "indirect", "low-key", "retrfriendly"):
        rows = {
            method: get(f"var_{variant}_{method}.jsonl")
            for method in ("none", "G1", "G3")
        }
        lines.append(
            f"| {variant} | {f(rate(rows['none'], 'S1'))} | "
            f"{f(rate(rows['G1'], 'S1'))} | {f(rate(rows['G3'], 'S1'))} | "
            f"{f(rate(rows['none'], 'S3'))} | {f(rate(rows['G1'], 'S3'))} | "
            f"{f(rate(rows['G3'], 'S3'))} |"
        )

    lines += [
        "",
        "## Task Sensitivity",
        "",
        "| Dataset | Task | S1 None | S3 None |",
        "|---|---|---:|---:|",
    ]
    for dataset, task, filename in (
        ("Synthetic", "Verdict", "items.jsonl"),
        ("Synthetic", "IOC", "ioc_syn_none_items.jsonl"),
        ("Real-104", "Verdict", "real8_none_items.jsonl"),
        ("Real-52", "IOC", "ioc_real_none_items.jsonl"),
    ):
        rows = get(filename)
        lines.append(
            f"| {dataset} | {task} | {f(rate(rows, 'S1'))} | {f(rate(rows, 'S3'))} |"
        )

    lines += [
        "",
        "## Historical Synthetic Write-Path Baselines",
        "",
        "| Carrier | None | G1 | G2 | G3 | G4 | TAME |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    methods = {
        "None": get("items.jsonl"),
        "G1": get("gate_g1_items.jsonl"),
        "G2": get("gate_g2_items.jsonl"),
        "G3": get("method_g3_items.jsonl"),
        "G4": get("method_g4_items.jsonl"),
        "TAME": get("guard_syn_final_items.jsonl"),
    }
    for mode in ("S1", "S3"):
        values = " | ".join(f(rate(methods[name], mode)) for name in methods)
        lines.append(f"| {mode} | {values} |")

    lines += [
        "",
        "### Clean W4 Accuracy",
        "",
        "| Carrier | None | G1 | G3 | G4 | TAME |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    clean_methods = {
        "None": get("clean_syn_none_items.jsonl"),
        "G1": get("clean_syn_g1_items.jsonl"),
        "G3": get("clean_syn_g3_items.jsonl"),
        "G4": get("clean_syn_g4_items.jsonl"),
        "TAME": get("guard_syn_clean_final_items.jsonl"),
    }
    for mode in ("S1", "S3"):
        values = " | ".join(f(accuracy(clean_methods[name], mode)) for name in clean_methods)
        lines.append(f"| {mode} | {values} |")

    lines += [
        "",
        "## Historical Real-Log G3 Screen",
        "",
        "The attacked TAME file for this historical slice is unavailable because its ",
        "duplicate keys are quarantined below. The remaining rows still document the ",
        "raw G3 screen and the separate clean capability slices.",
        "",
        "| Carrier | None raw | G3 raw | None clean ACC | G3 clean ACC | TAME clean ACC |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    real_none = get("real8_none_items.jsonl")
    real_g3 = get("real8_g3_items.jsonl")
    real_clean = {
        "None": get("real_clean_mixed_s13_items.jsonl"),
        "G3": get("real_clean_mixed_g3_s13_items.jsonl"),
        "TAME": get("guard_real_clean_final_items.jsonl"),
    }
    for mode in ("S1", "S3"):
        lines.append(
            f"| {mode} | {f(rate(real_none, mode))} | {f(rate(real_g3, mode))} | "
            f"{f(accuracy(real_clean['None'], mode))} | "
            f"{f(accuracy(real_clean['G3'], mode))} | "
            f"{f(accuracy(real_clean['TAME'], mode))} |"
        )

    lines += [
        "",
        "## Historical TAME Component Ablation",
        "",
        "| Carrier | Full TAME | No triage | No decoupling | No cache |",
        "|---|---:|---:|---:|---:|",
    ]
    legacy_ablation = {
        "Full": get("guard_syn_final_items.jsonl"),
        "No triage": get("tame_ablate_no_triage_items.jsonl"),
        "No decoupling": get("tame_ablate_no_decouple_items.jsonl"),
        "No cache": get("tame_ablate_no_cache_items.jsonl"),
    }
    for mode in ("S1", "S3"):
        lines.append(
            f"| {mode} | {f(rate(legacy_ablation['Full'], mode))} | "
            f"{f(rate(legacy_ablation['No triage'], mode))} | "
            f"{f(rate(legacy_ablation['No decoupling'], mode))} | "
            f"{f(rate(legacy_ablation['No cache'], mode))} |"
        )

    lines += [
        "",
        "## Qwen2.5-7B Detector-Ceiling Screen",
        "",
        "| Dataset | Carrier | None | G3 | TAME | Clean ACC |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for dataset, prefix in (("Synthetic", "syn"), ("Real-104", "real")):
        none = get(f"qwen_{'syn' if prefix == 'syn' else 'real8'}_items.jsonl" if prefix == "syn" else "qwen_real8_none_items.jsonl")
        g3 = get("qwen_method_g3_items.jsonl" if prefix == "syn" else "qwen_real8_g3_items.jsonl")
        tame = get("qwen_guard_syn_items.jsonl" if prefix == "syn" else "qwen_guard_real8_items.jsonl")
        clean = get("qwen_clean_syn_none_items.jsonl" if prefix == "syn" else "qwen_real_clean_mixed_s13_items.jsonl")
        for mode in ("S1", "S3"):
            lines.append(
                f"| {dataset} | {mode} | {f(rate(none, mode))} | {f(rate(g3, mode))} | "
                f"{f(rate(tame, mode))} | {f(accuracy(clean, mode))} |"
            )

    lines += [
        "",
        "### Qwen2.5-7B TAME Component Ablation",
        "",
        "| Carrier | Full TAME | No triage | No decoupling | No cache |",
        "|---|---:|---:|---:|---:|",
    ]
    qwen_ablation = {
        "Full": get("qwen_guard_syn_items.jsonl"),
        "No triage": get("qwen_tame_ablate_no_triage_items.jsonl"),
        "No decoupling": get("qwen_tame_ablate_no_decouple_items.jsonl"),
        "No cache": get("qwen_tame_ablate_no_cache_items.jsonl"),
    }
    for mode in ("S1", "S3"):
        lines.append(
            f"| {mode} | {f(rate(qwen_ablation['Full'], mode))} | "
            f"{f(rate(qwen_ablation['No triage'], mode))} | "
            f"{f(rate(qwen_ablation['No decoupling'], mode))} | "
            f"{f(rate(qwen_ablation['No cache'], mode))} |"
        )

    lines += [
        "",
        "## Quarantined Legacy Output",
        "",
        "`results/quarantined/guard_real8_items.jsonl` is preserved as an original ",
        "artifact but excluded from every paper aggregate: it contains 480 rows for only ",
        "208 unique `(sid, mode)` keys, with each key repeated two or three times.",
        "",
    ]
    (RESULTS / "SUPPLEMENTAL_EVIDENCE_REPORT.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def write_index() -> None:
    lines = [
        "# Result-to-Paper Index",
        "",
        "This index records why each frozen run family is bundled and how it may be used. ",
        "All pre-fix rows are descriptive because they lack exact input and replay hashes.",
        "",
        "| Family | Files | Paper role | Evidence status |",
        "|---|---:|---|---|",
        "| Qwen3-14B None/G3/TAME, clean, ablations | 15 | Primary audit and write-path tables | Zero unknown; legacy unpaired |",
        "| Qwen2.5-7B None/G3/TAME, clean, ablations | 15 | Detector-ceiling boundary and cross-model screen | Zero unknown; legacy unpaired |",
        "| GPT-5.4 None/TAME | 4 | Cross-model raw screen | Zero unknown; no clean counterpart |",
        "| DeepSeek-V4-Pro complete cleanrun None/TAME | 4 | Coverage-qualified cross-model screen | 251 any-window unknown rows and 179 W4 unknowns |",
        "| Claude-Sonnet-5 None/TAME | 4 | Coverage-qualified cross-model screen | 3 any-window unknown rows and 1 W4 unknown |",
        "| GLM-5.2 None/TAME | 4 | Coverage-qualified cross-model screen | 115 any-window unknown rows and 57 W4 unknowns |",
        "| Historical carrier and task baselines | 4 | S0--S4, payload, and task characterization | Zero unknown; legacy unpaired |",
        "| Trigger-distance sweep | 6 | Persistence robustness figure | Zero unknown; legacy unpaired |",
        "| Surface-variant sweep | 12 | Paraphrase/indirect/low-key/retrieval-friendly robustness table | Zero unknown; legacy unpaired |",
        "| Historical G1/G2/G3/G4/TAME and clean runs | 10 | Supplemental baseline table | Zero unknown; legacy unpaired |",
        "| Historical TAME component ablations | 3 | Supplemental ablation context | Zero unknown; legacy unpaired |",
        "| Historical real G3 and clean extensions | 4 | Supplemental real-log context | Zero unknown; legacy unpaired |",
        "| Duplicate DeepSeek real TAME output | 1 | None; preserved for provenance only | Quarantined: 480 rows, 208 unique keys |",
        "",
        "The four complete DeepSeek-V4-Pro `cleanrun` files are bundled. Partial,",
        "NUL-corrupted, and duplicate early attempts are not evidence and are",
        "intentionally excluded. Unknown-bearing families are reported with valid-output",
        "DASR, W4 U/N, and an all-N lower bound rather than silently scored as safe.",
        "",
    ]
    (RESULTS / "RESULT_INDEX.md").write_text("\n".join(lines), encoding="utf-8")


def generate_supplemental_report() -> dict[str, dict]:
    checks = {}
    cache = {
        filename: load_jsonl(filename)
        for filename, _ in set(specifications().values())
    }
    for label, (filename, expected) in specifications().items():
        checks[f"supplemental-{label}"] = check_rows(label, cache[filename], expected)

    for filename in ("items.jsonl", "real8_none_items.jsonl", "ioc_real_none_items.jsonl"):
        cache[filename] = load_jsonl(filename)

    quarantined = load_jsonl("quarantined/guard_real8_items.jsonl")
    keys = {(row["sid"], row["mode"]) for row in quarantined}
    assert len(quarantined) == 480 and len(keys) == 208
    checks["quarantined-legacy-real-tame"] = {
        "rows": len(quarantined),
        "unique_keys": len(keys),
        "unknown_rows": 0,
        "status": "excluded-duplicate-keys",
    }

    write_report(cache)
    write_index()
    return checks


if __name__ == "__main__":
    result = generate_supplemental_report()
    print(f"supplemental validation OK: {len(result)} slices")
    print(RESULTS / "SUPPLEMENTAL_EVIDENCE_REPORT.md")
