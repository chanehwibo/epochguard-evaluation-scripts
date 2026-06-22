from __future__ import annotations

import argparse
import csv
from pathlib import Path

from common import (
    TrialResult,
    add_command_context_arguments,
    add_common_arguments,
    build_context,
    finalize_results,
    materialize_input_file,
)


def read_latencies(latency_file: Path) -> list[float]:
    with latency_file.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [float(row["seconds"]) for row in reader]


def main() -> None:
    parser = argparse.ArgumentParser(description="Experiment 6.3: cold boot and service-ready times.")
    parser.add_argument("--latency-file", type=Path, required=True)
    parser.add_argument("--metric", choices=["cold_boot", "post_ota_ready", "cached_ready"], required=True)
    parser.add_argument("--collect-cmd")
    add_common_arguments(parser, default_trials=30, default_warmups=5)
    add_command_context_arguments(parser)
    args = parser.parse_args()

    context = build_context(args.var, metric=args.metric, scenario="boot_ready")
    materialize_input_file(
        input_path=args.latency_file,
        collect_cmd=args.collect_cmd,
        context=context,
        cwd=args.cwd,
        timeout_sec=args.timeout_sec,
        description="latency file",
    )

    latencies = read_latencies(args.latency_file)
    results = [
        TrialResult(
            "exp_13_boot_ready_time",
            index + 1,
            True,
            args.metric,
            value,
            "s",
            args.metric,
        )
        for index, value in enumerate(latencies)
    ]

    finalize_results("exp_13_boot_ready_time", results, args.output_dir)


if __name__ == "__main__":
    main()
