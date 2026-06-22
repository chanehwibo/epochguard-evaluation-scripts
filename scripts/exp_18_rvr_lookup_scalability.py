from __future__ import annotations

import argparse
import csv
from pathlib import Path

from common import TrialResult, finalize_results


def read_rows(input_file: Path) -> list[dict[str, str]]:
    with input_file.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader)


def main() -> None:
    parser = argparse.ArgumentParser(description="Experiment 6.4: RVR lookup scalability.")
    parser.add_argument("--input-file", type=Path, required=True)
    parser.add_argument("--mode", choices=["warm_cache", "cold_lookup"], required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    args = parser.parse_args()

    rows = read_rows(args.input_file)
    results = [
        TrialResult(
            "exp_18_rvr_lookup_scalability",
            index + 1,
            True,
            args.mode,
            float(row["latency_us"]),
            "us",
            f"components={row['components']}",
        )
        for index, row in enumerate(rows)
    ]
    finalize_results("exp_18_rvr_lookup_scalability", results, args.output_dir)


if __name__ == "__main__":
    main()
