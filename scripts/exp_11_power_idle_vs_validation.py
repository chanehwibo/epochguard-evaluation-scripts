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


def read_power_trace(trace_file: Path) -> list[float]:
    values: list[float] = []
    with trace_file.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            values.append(float(row["watts"]))
    return values


def main() -> None:
    parser = argparse.ArgumentParser(description="Experiment 6.3: idle and validation power comparison.")
    parser.add_argument("--idle-trace", type=Path, required=True)
    parser.add_argument("--validation-trace", type=Path, required=True)
    parser.add_argument("--collect-idle-cmd")
    parser.add_argument("--collect-validation-cmd")
    add_common_arguments(parser, default_trials=30, default_warmups=5)
    add_command_context_arguments(parser)
    args = parser.parse_args()

    context = build_context(args.var, scenario="power")
    materialize_input_file(
        input_path=args.idle_trace,
        collect_cmd=args.collect_idle_cmd,
        context=context,
        cwd=args.cwd,
        timeout_sec=args.timeout_sec,
        description="idle trace",
    )
    materialize_input_file(
        input_path=args.validation_trace,
        collect_cmd=args.collect_validation_cmd,
        context=context,
        cwd=args.cwd,
        timeout_sec=args.timeout_sec,
        description="validation trace",
    )

    idle_values = read_power_trace(args.idle_trace)
    validation_values = read_power_trace(args.validation_trace)

    results = [
        TrialResult("exp_11_power_idle_vs_validation", 1, True, "idle_power_mean", sum(idle_values) / len(idle_values), "W", "idle"),
        TrialResult("exp_11_power_idle_vs_validation", 2, True, "validation_power_mean", sum(validation_values) / len(validation_values), "W", "validation"),
    ]

    finalize_results("exp_11_power_idle_vs_validation", results, args.output_dir)


if __name__ == "__main__":
    main()
