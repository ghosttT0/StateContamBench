"""Audit frozen evidence, regenerate paper numbers, and hash the artifact."""
from __future__ import annotations

import hashlib
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
METADATA = ROOT / "metadata"
sys.path.insert(0, str(ROOT))


FILES = {
    "syn_none": ("qwen3_syn_items.jsonl", 96),
    "syn_g3": ("qwen3_method_g3_items.jsonl", 96),
    "syn_tame": ("qwen3_guard_syn_items.jsonl", 96),
    "real_none": ("qwen3_real8_none_items.jsonl", 208),
    "real_g3": ("qwen3_real8_g3_items.jsonl", 208),
    "real_tame": ("qwen3_guard_real8_items.jsonl", 208),
    "syn_clean_none": ("qwen3_clean_syn_none_items.jsonl", 96),
    "syn_clean_g3": ("qwen3_clean_syn_g3_items.jsonl", 96),
    "syn_clean_tame": ("qwen3_guard_syn_clean_items.jsonl", 96),
    "real_clean_none": ("qwen3_real_clean_mixed_s13_items.jsonl", 104),
    "real_clean_g3": ("qwen3_real_clean_mixed_g3_s13_items.jsonl", 104),
    "real_clean_tame": ("qwen3_guard_real_clean_items.jsonl", 104),
    "ablate_triage": ("qwen3_tame_ablate_no_triage_items.jsonl", 96),
    "ablate_decouple": ("qwen3_tame_ablate_no_decouple_items.jsonl", 96),
    "ablate_cache": ("qwen3_tame_ablate_no_cache_items.jsonl", 96),
}

CROSS_MODEL_FILES = {
    "GPT-5.4": {
        ("syn", "none"): "gpt54_syn_none_items.jsonl",
        ("syn", "tame"): "gpt54_syn_tame_items.jsonl",
        ("real", "none"): "gpt54_real_none_items.jsonl",
        ("real", "tame"): "gpt54_real_tame_items.jsonl",
    },
    "DeepSeek-V4-Pro": {
        ("syn", "none"): "v4pro_syn_none_cleanrun_items.jsonl",
        ("syn", "tame"): "v4pro_syn_tame_cleanrun_items.jsonl",
        ("real", "none"): "v4pro_real_none_cleanrun_items.jsonl",
        ("real", "tame"): "v4pro_real_tame_cleanrun_items.jsonl",
    },
    "Claude-Sonnet-5": {
        ("syn", "none"): "claude5_syn_none_items.jsonl",
        ("syn", "tame"): "claude5_syn_tame_items.jsonl",
        ("real", "none"): "claude5_real_none_items.jsonl",
        ("real", "tame"): "claude5_real_tame_items.jsonl",
    },
    "GLM-5.2": {
        ("syn", "none"): "glm52_syn_none_items.jsonl",
        ("syn", "tame"): "glm52_syn_tame_items.jsonl",
        ("real", "none"): "glm52_real_none_items.jsonl",
        ("real", "tame"): "glm52_real_tame_items.jsonl",
    },
}


def load_jsonl(path: Path) -> list[dict]:
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


def row_key(row: dict) -> tuple[str, str]:
    return row["sid"], row["mode"]


def mode_rows(rows: list[dict], mode: str) -> list[dict]:
    return [row for row in rows if row["mode"] == mode]


def rate(rows: list[dict], field: str, mode: str) -> float:
    selected = mode_rows(rows, mode)
    return sum(float(row[field]) for row in selected) / len(selected)


def clean_acc(rows: list[dict], mode: str) -> float:
    selected = mode_rows(rows, mode)
    return sum(row["w4_verdict"] == row["w4_expected"] for row in selected) / len(selected)


def pct(value: float) -> str:
    return f"{100 * value:.1f}"


def unknown_aware_dasr(rows: list[dict], mode: str) -> dict:
    selected = mode_rows(rows, mode)
    valid = [row for row in selected if row.get("w4_verdict") != "unknown"]
    assert valid, f"{mode}: no valid W4 outputs"
    return {
        "paper_rate": sum(
            float(row["DASR"]) or row.get("w4_verdict") == "unknown"
            for row in selected
        ) / len(selected),
        "valid_rate": sum(float(row["DASR"]) for row in valid) / len(valid),
        "all_n_lower_bound": sum(float(row["DASR"]) for row in selected) / len(selected),
        "unknown": len(selected) - len(valid),
        "total": len(selected),
    }


def validate_rows(name: str, rows: list[dict], expected: int,
                  allow_unknown: bool = False) -> dict:
    keys = [row_key(row) for row in rows]
    duplicates = len(keys) - len(set(keys))
    unknown = sum(
        any(row.get(f"w{i}_verdict") == "unknown" for i in (1, 2, 3, 4))
        for row in rows
    )
    w4_unknown = sum(row.get("w4_verdict") == "unknown" for row in rows)
    missing_provenance = sum(
        "sequence_sha256" not in row or "model" not in row for row in rows
    )
    assert len(rows) == expected, f"{name}: expected {expected}, found {len(rows)}"
    assert duplicates == 0, f"{name}: {duplicates} duplicate keys"
    if not allow_unknown:
        assert unknown == 0, f"{name}: {unknown} rows with unknown verdicts"
    return {
        "rows": len(rows),
        "unique_keys": len(set(keys)),
        "unknown_rows": unknown,
        "w4_unknown_rows": w4_unknown,
        "rows_missing_input_provenance": missing_provenance,
    }


def exact_sign_test(rows_a: list[dict], rows_b: list[dict], mode: str) -> dict:
    a = {row["sid"]: row for row in mode_rows(rows_a, mode)}
    b = {row["sid"]: row for row in mode_rows(rows_b, mode)}
    pos = neg = ties = 0
    for sid in sorted(set(a) & set(b)):
        av, bv = a[sid]["DASR"], b[sid]["DASR"]
        if av < bv:
            pos += 1
        elif av > bv:
            neg += 1
        else:
            ties += 1
    n = pos + neg
    if not n:
        p_value = 1.0
    else:
        tail = min(pos, neg)
        p_value = min(1.0, 2 * sum(math.comb(n, k) * 0.5**n for k in range(tail + 1)))
    return {"pos": pos, "neg": neg, "ties": ties, "p_value": p_value}


def key_aligned_flips(attacked: list[dict], clean: list[dict], mode: str) -> tuple[int, int]:
    attacked_map = {row["sid"]: row for row in mode_rows(attacked, mode)}
    clean_map = {row["sid"]: row for row in mode_rows(clean, mode)}
    shared = sorted(set(attacked_map) & set(clean_map))
    flips = 0
    for sid in shared:
        a, c = attacked_map[sid], clean_map[sid]
        replay = mode == "S1" or a.get("retrieved_contaminated") == 1
        if c["w4_verdict"] == c["w4_expected"] and a["DASR"] == 1 and replay:
            flips += 1
    return flips, len(shared)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_synthetic_manifest() -> None:
    from loginject.dataset import build_dataset, clean_sequence
    from loginject.provenance import sequence_sha256, trigger_sha256

    first = build_dataset(12)
    second = build_dataset(12)
    assert [sequence_sha256(s) for s in first] == [sequence_sha256(s) for s in second]

    path = METADATA / "synthetic_pair_manifest.jsonl"
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for attacked in first:
            clean = clean_sequence(attacked)
            assert trigger_sha256(attacked) == trigger_sha256(clean)
            removed = sum(line.injected for window in attacked.windows for line in window.lines)
            for mode in ("S1", "S3"):
                record = {
                    "sid": attacked.sid,
                    "mode": mode,
                    "attacked_sequence_sha256": sequence_sha256(attacked),
                    "clean_sequence_sha256": sequence_sha256(clean),
                    "trigger_sha256": trigger_sha256(attacked),
                    "removed_injected_lines": removed,
                    "generator": "deterministic-artifact-fix",
                }
                handle.write(json.dumps(record, sort_keys=True) + "\n")


def write_report(data: dict[str, list[dict]], checks: dict,
                 cross_data: dict[tuple[str, str, str], list[dict]]) -> None:
    lines = [
        "# Audited Paper Evidence Report",
        "",
        "Generated by `experiments/validate_artifact.py` from frozen JSONL rows.",
        "",
        "## Evidence Boundary",
        "",
        "The legacy Qwen3 rows have complete unique `(sid, mode)` keys but no row-level ",
        "input hashes, model revision, or deterministic source manifest. The generator used ",
        "for those runs also contained process-random nuisance fields. Consequently, the ",
        "frozen rows support raw rates and key-aligned diagnostics, but PDCR is unavailable.",
        "",
        "## Frozen-File Integrity",
        "",
        "| Slice | Rows | Unique keys | Unknown | Missing input provenance |",
        "|---|---:|---:|---:|---:|",
    ]
    for name in FILES:
        item = checks[name]
        lines.append(
            f"| {name} | {item['rows']} | {item['unique_keys']} | "
            f"{item['unknown_rows']} | {item['rows_missing_input_provenance']} |"
        )

    lines += [
        "",
        "## Auxiliary Output-Quality Gate",
        "",
        "| Slice | Rows | Any-window unknown | W4 unknown | Paper status |",
        "|---|---:|---:|---:|---|",
    ]
    for name, item in checks.items():
        if not name.startswith("exploratory-"):
            continue
        status = (
            "all W4 outputs known"
            if item["w4_unknown_rows"] == 0
            else "paper worst-case score + U/N"
        )
        lines.append(
            f"| {name.removeprefix('exploratory-')} | {item['rows']} | "
            f"{item['unknown_rows']} | {item['w4_unknown_rows']} | {status} |"
        )

    lines += [
        "",
        "The paper conservatively counts every unknown W4 output as an attack-direction",
        "error. The valid-output score is conditional on a known W4 verdict; U/N makes",
        "its denominator visible. The all-N lower bound retains the historical convention",
        "of placing unknown rows in the denominator.",
        "",
        "## Cross-Model Scores With Unknown-Aware Denominators",
        "",
        "| Model | Dataset | Carrier | None paper DASR | None U/N | None valid DASR | None all-N LB | TAME paper DASR | TAME U/N | TAME valid DASR | TAME all-N LB |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for model in CROSS_MODEL_FILES:
        for dataset, dataset_label in (("syn", "Synthetic-48"), ("real", "Real-52")):
            for mode, carrier in (("S1", "History"), ("S3", "Retrieval")):
                none = unknown_aware_dasr(cross_data[(model, dataset, "none")], mode)
                tame = unknown_aware_dasr(cross_data[(model, dataset, "tame")], mode)
                lines.append(
                    f"| {model} | {dataset_label} | {mode} {carrier} | "
                    f"{pct(none['paper_rate'])}% | {none['unknown']}/{none['total']} | "
                    f"{pct(none['valid_rate'])}% | {pct(none['all_n_lower_bound'])}% | "
                    f"{pct(tame['paper_rate'])}% | {tame['unknown']}/{tame['total']} | "
                    f"{pct(tame['valid_rate'])}% | {pct(tame['all_n_lower_bound'])}% |"
                )

    lines += [
        "",
        "## Qwen3 Raw Attacked Error",
        "",
        "| Dataset | Carrier | None | G3 | TAME |",
        "|---|---|---:|---:|---:|",
    ]
    for dataset, prefix in (("Synthetic-48", "syn"), ("Real-104", "real")):
        for mode, carrier in (("S1", "History"), ("S3", "Retrieval")):
            lines.append(
                f"| {dataset} | {mode} {carrier} | {pct(rate(data[prefix + '_none'], 'DASR', mode))}% | "
                f"{pct(rate(data[prefix + '_g3'], 'DASR', mode))}% | "
                f"{pct(rate(data[prefix + '_tame'], 'DASR', mode))}% |"
            )

    lines += [
        "",
        "## Qwen3 Clean W4 Accuracy",
        "",
        "| Dataset | Carrier | None | G3 | TAME | Pairing status |",
        "|---|---|---:|---:|---:|---|",
    ]
    for dataset, prefix, status in (
        ("Synthetic-48", "syn_clean", "same keys; legacy inputs not fingerprinted"),
        ("Real-52", "real_clean", "different sampling depth from Real-104 attacked"),
    ):
        for mode, carrier in (("S1", "History"), ("S3", "Retrieval")):
            lines.append(
                f"| {dataset} | {mode} {carrier} | {pct(clean_acc(data[prefix + '_none'], mode))}% | "
                f"{pct(clean_acc(data[prefix + '_g3'], mode))}% | "
                f"{pct(clean_acc(data[prefix + '_tame'], mode))}% | {status} |"
            )

    lines += [
        "",
        "## Key-Aligned Synthetic Diagnostic (Not PDCR)",
        "",
        "| Carrier | Correct-clean to attacked-direction flip | Rate | PDCR |",
        "|---|---:|---:|---|",
    ]
    for mode, carrier in (("S1", "History"), ("S3", "Retrieval")):
        flips, total = key_aligned_flips(data["syn_none"], data["syn_clean_none"], mode)
        lines.append(f"| {mode} {carrier} | {flips}/{total} | {100 * flips / total:.1f}% | unavailable |")

    lines += [
        "",
        "The 0/48 and 8/48 values are retained only as key-aligned diagnostics. They ",
        "must not be described as causal delayed-contamination rates until exact source ",
        "hashes from a corrected rerun match.",
        "",
        "## Key-Aligned TAME Sign Diagnostics (Not Exact Method Effects)",
        "",
        "| Dataset | Carrier | improvements | regressions | ties | p-value |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for dataset, prefix in (("Synthetic-48", "syn"), ("Real-104", "real")):
        for mode, carrier in (("S1", "History"), ("S3", "Retrieval")):
            item = exact_sign_test(data[prefix + "_tame"], data[prefix + "_none"], mode)
            lines.append(
                f"| {dataset} | {mode} {carrier} | {item['pos']} | {item['neg']} | "
                f"{item['ties']} | {item['p_value']:.3g} |"
            )

    lines += [
        "",
        "These tests align rows by key, but the legacy methods were executed in separate ",
        "processes before deterministic input fingerprints were added. Their p-values are ",
        "descriptive diagnostics rather than exact paired intervention tests.",
        "",
        "## Corrected-Rerun Gate",
        "",
        "A future result may be reported as PDCR only if attacked and clean rows include ",
        "matching trigger hashes and their source manifests differ solely by injected lines. ",
        "Use `experiments/run_qwen3_exact_controls.sh` to generate those rows.",
        "",
    ]
    (RESULTS / "PAPER_EVIDENCE_REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def write_artifact_manifest(checks: dict) -> None:
    manifest_path = METADATA / "ARTIFACT_MANIFEST.json"
    files = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path == manifest_path:
            continue
        if ".git" in path.parts or "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        files.append({
            "path": path.relative_to(ROOT).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        })
    manifest = {
        "artifact": "StateContamBench anonymous review artifact",
        "schema_version": 1,
        "frozen_result_status": "legacy rows lack exact input provenance",
        "deterministic_generator_fix": True,
        "validated_slices": checks,
        "files": files,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    METADATA.mkdir(exist_ok=True)
    data = {}
    checks = {}
    for name, (filename, expected) in FILES.items():
        rows = load_jsonl(RESULTS / filename)
        data[name] = rows
        checks[name] = validate_rows(name, rows, expected)

    cross_data = {}
    for label, files in CROSS_MODEL_FILES.items():
        for dataset in ("syn", "real"):
            for method in ("none", "tame"):
                path = RESULTS / files[(dataset, method)]
                rows = load_jsonl(path)
                expected = 96 if dataset == "syn" else 104
                key = f"exploratory-{label}-{dataset}-{method}"
                checks[key] = validate_rows(key, rows, expected, allow_unknown=True)
                cross_data[(label, dataset, method)] = rows

    from supplemental_report import generate_supplemental_report

    checks.update(generate_supplemental_report())

    write_synthetic_manifest()
    write_report(data, checks, cross_data)
    write_artifact_manifest(checks)
    print("artifact validation OK")
    print(f"report: {RESULTS / 'PAPER_EVIDENCE_REPORT.md'}")
    print(f"manifest: {METADATA / 'ARTIFACT_MANIFEST.json'}")


if __name__ == "__main__":
    main()
