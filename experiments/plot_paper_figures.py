"""Regenerate the payload- and task-sensitivity figures from frozen rows."""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
FIGURES.mkdir(exist_ok=True)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "DejaVu Sans", "Liberation Sans"],
    "pdf.fonttype": 42,
    "svg.fonttype": "none",
    "font.size": 8,
})


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def dasr(rows: list[dict], mode: str) -> float:
    selected = [row for row in rows if row["mode"] == mode]
    return 100 * sum(row["DASR"] for row in selected) / len(selected)


def main() -> None:
    verdict = load(RESULTS / "real8_none_items.jsonl")
    ioc = load(RESULTS / "ioc_real_none_items.jsonl")
    syn_verdict = load(RESULTS / "items.jsonl")
    syn_ioc = load(RESULTS / "ioc_syn_none_items.jsonl")

    groups = defaultdict(list)
    for row in verdict:
        if row["mode"] == "S1":
            groups[row["payload_kind"]].append(row["DASR"])
    payload = {
        key: 100 * sum(values) / len(values)
        for key, values in groups.items()
        if key in {"AUDIT-followup", "SYSLOG", "AUDIT-status"}
    }
    task = {}
    for dataset, verdict_rows, ioc_rows in (
        ("Synthetic", syn_verdict, syn_ioc),
        ("Real", verdict, ioc),
    ):
        for mode in ("S1", "S3"):
            task[(dataset, "Verdict", mode)] = dasr(verdict_rows, mode)
            task[(dataset, "IOC", mode)] = dasr(ioc_rows, mode)

    distance = {}
    for window, delay in ((1, 3), (2, 2), (3, 1)):
        for method in ("none", "tame"):
            rows = load(RESULTS / f"distance_syn_w{window}_{method}.jsonl")
            for mode in ("S1", "S3"):
                distance[(delay, method, mode)] = dasr(rows, mode)

    source = FIGURES / "state_contamination_sensitivity_source_data.csv"
    with source.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["dataset", "condition", "raw_error", "analysis", "carrier"])
        for name in ("AUDIT-followup", "SYSLOG", "AUDIT-status"):
            writer.writerow(["Real", name, f"{payload[name]:.1f}", "payload", "S1"])
        for dataset in ("Synthetic", "Real"):
            for name in ("Verdict", "IOC"):
                for mode in ("S1", "S3"):
                    writer.writerow([
                        dataset, name, f"{task[(dataset, name, mode)]:.1f}",
                        "task", mode,
                    ])
        for delay in (1, 2, 3):
            for method in ("none", "tame"):
                for mode in ("S1", "S3"):
                    writer.writerow([
                        "Synthetic", f"distance-{delay}-{method}",
                        f"{distance[(delay, method, mode)]:.1f}", "distance", mode,
                    ])

    labels = ["AUDIT-followup", "SYSLOG", "AUDIT-status"]
    values = [payload[label] for label in labels]
    fig, ax = plt.subplots(figsize=(3.35, 2.15))
    bars = ax.barh(labels[::-1], values[::-1], color=["#95A5B3", "#3E6FB6", "#8B1F2D"])
    ax.set_xlim(0, 100)
    ax.set_xlabel("Raw attack-direction error (%)")
    ax.set_title("Payload sensitivity on historical real S1")
    ax.spines[["right", "top"]].set_visible(False)
    for bar, value in zip(bars, values[::-1]):
        ax.text(value + 1.5, bar.get_y() + bar.get_height() / 2, f"{value:.1f}", va="center")
    fig.tight_layout()
    fig.savefig(FIGURES / "state_contamination_payload_sensitivity.pdf")
    fig.savefig(FIGURES / "state_contamination_payload_sensitivity.svg")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(3.35, 2.15))
    labels = ["Syn S1", "Syn S3", "Real S1", "Real S3"]
    x = list(range(len(labels)))
    width = 0.36
    verdict_values = [
        task[(dataset, "Verdict", mode)]
        for dataset, mode in (("Synthetic", "S1"), ("Synthetic", "S3"),
                              ("Real", "S1"), ("Real", "S3"))
    ]
    ioc_values = [
        task[(dataset, "IOC", mode)]
        for dataset, mode in (("Synthetic", "S1"), ("Synthetic", "S3"),
                              ("Real", "S1"), ("Real", "S3"))
    ]
    ax.bar([value - width / 2 for value in x], verdict_values, width,
           color="#3E6FB6", label="Verdict")
    ax.bar([value + width / 2 for value in x], ioc_values, width,
           color="#B94A48", label="IOC")
    ax.set_xticks(x, labels, rotation=18, ha="right")
    ax.set_ylabel("Raw attack-direction error (%)")
    ax.set_ylim(0, 100)
    ax.set_title("Task sensitivity across historical streams")
    ax.legend(frameon=False)
    ax.spines[["right", "top"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIGURES / "state_contamination_task_sensitivity.pdf")
    fig.savefig(FIGURES / "state_contamination_task_sensitivity.svg")
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(3.35, 2.05), sharex=True, sharey=True)
    for ax, mode, title in zip(axes, ("S1", "S3"), ("History", "Retrieval")):
        delays = [1, 2, 3]
        ax.plot(delays, [distance[(d, "none", mode)] for d in delays],
                color="#3E6FB6", marker="o", label="None")
        ax.plot(delays, [distance[(d, "tame", mode)] for d in delays],
                color="#B94A48", marker="s", label="TAME")
        ax.set_title(f"{mode} {title}")
        ax.set_xticks(delays)
        ax.set_ylim(0, 60)
        ax.spines[["right", "top"]].set_visible(False)
    axes[0].set_ylabel("Raw error (%)")
    fig.supxlabel("Trigger distance (windows)", y=0.02, fontsize=8)
    axes[1].legend(frameon=False, loc="upper right")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(FIGURES / "state_contamination_trigger_distance.pdf")
    fig.savefig(FIGURES / "state_contamination_trigger_distance.svg")
    plt.close(fig)

    print(f"wrote figures and {source}")


if __name__ == "__main__":
    main()
