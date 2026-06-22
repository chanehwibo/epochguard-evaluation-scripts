from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from common import ci95, mean, median, percentile, stdev


def load_metric_values(input_file: Path, metric_column: str) -> list[float]:
    with input_file.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [float(row[metric_column]) for row in reader]


def main() -> None:
    parser = argparse.ArgumentParser(description="Experiment 6.4: statistical summary generator.")
    parser.add_argument("--input-file", type=Path, required=True)
    parser.add_argument("--metric-column", default="metric_value")
    parser.add_argument("--output", type=Path, default=Path("results/exp_19_statistical_summary.json"))
    args = parser.parse_args()

    values = load_metric_values(args.input_file, args.metric_column)
    summary = {
        "count": len(values),
        "mean": mean(values),
        "stdev": stdev(values),
        "median": median(values),
        "p95": percentile(values, 0.95),
        "ci95": ci95(values),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
