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


def read_ms(latency_file: Path) -> list[float]:
    with latency_file.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [float(row["latency_ms"]) for row in reader]


def main() -> None:
    parser = argparse.ArgumentParser(description="Experiment 6.3: preview startup P95 latency.")
    parser.add_argument("--latency-file", type=Path, required=True)
    parser.add_argument("--collect-cmd")
    add_common_arguments(parser, default_trials=30, default_warmups=5)
    add_command_context_arguments(parser)
    args = parser.parse_args()

    context = build_context(args.var, workload="preview_startup")
    materialize_input_file(
        input_path=args.latency_file,
        collect_cmd=args.collect_cmd,
        context=context,
        cwd=args.cwd,
        timeout_sec=args.timeout_sec,
        description="latency file",
    )

    latencies = read_ms(args.latency_file)
    results = [
        TrialResult("exp_15_preview_startup_latency", index + 1, True, "latency", value, "ms", "preview_startup")
        for index, value in enumerate(latencies)
    ]
    finalize_results("exp_15_preview_startup_latency", results, args.output_dir)


if __name__ == "__main__":
    main()
