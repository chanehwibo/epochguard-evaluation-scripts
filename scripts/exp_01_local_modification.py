from __future__ import annotations

import argparse

from common import (
    TrialResult,
    add_common_arguments,
    add_denial_probe_arguments,
    build_context,
    finalize_results,
    parse_exit_codes,
    perform_denial_trial,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Experiment 6.2: local modification denial latency.")
    add_common_arguments(parser, default_trials=50, default_warmups=5)
    add_denial_probe_arguments(parser)
    args = parser.parse_args()

    results: list[TrialResult] = []
    total_runs = args.warmups + args.trials
    deny_exit_codes = parse_exit_codes(args.deny_exit_codes)
    for trial in range(total_runs):
        context = build_context(args.var, trial=trial + 1, scenario="local_modification")
        success, latency_ms, detail = perform_denial_trial(
            context=context,
            prepare_cmd=args.prepare_cmd,
            mutate_cmd=args.mutate_cmd,
            trigger_cmd=args.trigger_cmd,
            launch_cmd=args.launch_cmd,
            cleanup_cmd=args.cleanup_cmd,
            cwd=args.cwd,
            timeout_sec=args.timeout_sec,
            max_wait_sec=args.max_wait_sec,
            poll_interval_ms=args.poll_interval_ms,
            deny_match=args.deny_match,
            deny_exit_codes=deny_exit_codes,
            deny_on_nonzero=args.deny_on_nonzero,
        )
        if trial >= args.warmups:
            results.append(
                TrialResult(
                    experiment="exp_01_local_modification",
                    trial=trial - args.warmups + 1,
                    success=success,
                    metric_name="mutation_to_denial_latency",
                    metric_value=latency_ms,
                    unit="ms",
                    detail=detail,
                )
            )

    finalize_results("exp_01_local_modification", results, args.output_dir)


if __name__ == "__main__":
    main()
