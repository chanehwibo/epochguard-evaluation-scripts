from __future__ import annotations

import argparse
import time
from pathlib import Path

from common import TrialResult, add_common_arguments, finalize_results, monotonic_ms


def run_trial(library_ready_marker: Path) -> float:
    start = monotonic_ms()
    # Replace with concrete shared-library refresh and readiness probe.
    while not library_ready_marker.exists():
        time.sleep(0.01)
        if monotonic_ms() - start > 60_000:
            break
    end = monotonic_ms()
    return end - start


def main() -> None:
    parser = argparse.ArgumentParser(description="Experiment 6.3: shared-library refresh recovery latency.")
    parser.add_argument("--library-ready-marker", type=Path, required=True)
    add_common_arguments(parser, default_trials=30, default_warmups=5)
    args = parser.parse_args()

    results: list[TrialResult] = []
    total_runs = args.warmups + args.trials
    for trial in range(total_runs):
        latency_ms = run_trial(args.library_ready_marker)
        if trial >= args.warmups:
            results.append(
                TrialResult(
                    experiment="exp_09_shared_library_refresh",
                    trial=trial - args.warmups + 1,
                    success=True,
                    metric_name="library_pending_to_ready_latency",
                    metric_value=latency_ms,
                    unit="ms",
                    detail="shared_library_refresh",
                )
            )

    finalize_results("exp_09_shared_library_refresh", results, args.output_dir)


if __name__ == "__main__":
    main()
