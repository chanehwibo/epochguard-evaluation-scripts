from __future__ import annotations

import argparse
import csv
from pathlib import Path

from common import TrialResult, add_common_arguments, finalize_results


def integrate_energy_mj(trace_file: Path) -> float:
    rows: list[tuple[float, float]] = []
    with trace_file.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append((float(row["seconds"]), float(row["watts"])))
    energy_j = 0.0
    for index in range(1, len(rows)):
        dt = rows[index][0] - rows[index - 1][0]
        avg_power = (rows[index][1] + rows[index - 1][1]) / 2.0
        energy_j += dt * avg_power
    return energy_j * 1000.0


def main() -> None:
    parser = argparse.ArgumentParser(description="Experiment 6.3: validation energy per component.")
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--components", type=int, required=True)
    parser.add_argument("--mode", choices=["coalesced", "uncoalesced"], required=True)
    add_common_arguments(parser, default_trials=30, default_warmups=5)
    args = parser.parse_args()

    total_mj = integrate_energy_mj(args.trace)
    per_component_mj = total_mj / args.components
    results = [
        TrialResult(
            "exp_12_validation_energy",
            1,
            True,
            "energy_per_component",
            per_component_mj,
            "mJ",
            args.mode,
        )
    ]

    finalize_results("exp_12_validation_energy", results, args.output_dir)


if __name__ == "__main__":
    main()
