from __future__ import annotations

import argparse
import time
from pathlib import Path

from common import TrialResult, add_common_arguments, finalize_results, monotonic_ms


def run_trial(script_ready_marker: Path) -> float:
    start = monotonic_ms()
    # Replace with concrete maintenance-script update and readiness probe.
    while not script_ready_marker.exists():
        time.sleep(0.01)
        if monotonic_ms() - start > 60_000:
            break
    end = monotonic_ms()
    return end - start


def main() -> None:
    parser = argparse.ArgumentParser(description="Experiment 6.3: script update recovery latency.")
    parser.add_argument("--script-ready-marker", type=Path, required=True)
    add_common_arguments(parser, default_trials=30, default_warmups=5)
    args = parser.parse_args()

    results: list[TrialResult] = []
    total_runs = args.warmups + args.trials
    for trial in range(total_runs):
        latency_ms = run_trial(args.script_ready_marker)
        if trial >= args.warmups:
            results.append(
                TrialResult(
                    experiment="exp_10_script_update_recovery",
                    trial=trial - args.warmups + 1,
                    success=True,
                    metric_name="script_pending_to_ready_latency",
                    metric_value=latency_ms,
                    unit="ms",
                    detail="script_update",
                )
            )

    finalize_results("exp_10_script_update_recovery", results, args.output_dir)


if __name__ == "__main__":
    main()
