from __future__ import annotations

import argparse

from common import (
    TrialResult,
    add_common_arguments,
    add_readiness_probe_arguments,
    build_context,
    finalize_results,
    perform_readiness_trial,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Experiment 6.3: interrupted update repair latency.")
    add_common_arguments(parser, default_trials=30, default_warmups=5)
    add_readiness_probe_arguments(parser)
    parser.add_argument("--ready-cmd", required=True)
    args = parser.parse_args()

    results: list[TrialResult] = []
    total_runs = args.warmups + args.trials
    for trial in range(total_runs):
        context = build_context(args.var, trial=trial + 1, scenario="interrupted_update")
        success, latency_ms, detail = perform_readiness_trial(
            context=context,
            prepare_cmd=args.prepare_cmd,
            workflow_cmd=args.workflow_cmd,
            repair_cmd=args.repair_cmd,
            ready_cmd=args.ready_cmd,
            cleanup_cmd=args.cleanup_cmd,
            cwd=args.cwd,
            timeout_sec=args.timeout_sec,
            max_wait_sec=args.max_wait_sec,
            poll_interval_ms=args.poll_interval_ms,
            ready_match=args.ready_match,
        )
        if trial >= args.warmups:
            results.append(
                TrialResult(
                    experiment="exp_07_interrupted_update_repair",
                    trial=trial - args.warmups + 1,
                    success=success,
                    metric_name="repair_completion_latency",
                    metric_value=latency_ms,
                    unit="ms",
                    detail=detail,
                )
            )

    finalize_results("exp_07_interrupted_update_repair", results, args.output_dir)


if __name__ == "__main__":
    main()
