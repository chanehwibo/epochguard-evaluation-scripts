from __future__ import annotations

import argparse
import csv
import json
import math
import re
import statistics
import subprocess
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, Mapping, Sequence


@dataclass
class TrialResult:
    experiment: str
    trial: int
    success: bool
    metric_name: str
    metric_value: float
    unit: str
    detail: str = ""


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def run_command(command: Sequence[str], timeout: float | None = None, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=str(cwd) if cwd else None,
        timeout=timeout,
        text=True,
        capture_output=True,
        check=False,
    )


def run_shell_command(command: str, timeout: float | None = None, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        timeout=timeout,
        text=True,
        capture_output=True,
        shell=True,
        check=False,
    )


def monotonic_ms() -> float:
    return time.perf_counter_ns() / 1_000_000.0


def mean(values: Sequence[float]) -> float:
    return statistics.fmean(values) if values else float("nan")


def stdev(values: Sequence[float]) -> float:
    return statistics.stdev(values) if len(values) > 1 else 0.0


def median(values: Sequence[float]) -> float:
    return statistics.median(values) if values else float("nan")


def percentile(values: Sequence[float], p: float) -> float:
    if not values:
        return float("nan")
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = (len(ordered) - 1) * p
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return ordered[lower]
    fraction = rank - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def ci95(values: Sequence[float]) -> tuple[float, float]:
    if not values:
        return float("nan"), float("nan")
    if len(values) == 1:
        return values[0], values[0]
    m = mean(values)
    margin = 1.96 * (stdev(values) / math.sqrt(len(values)))
    return m - margin, m + margin


def write_csv(results: Iterable[TrialResult], out_path: Path) -> None:
    ensure_dir(out_path.parent)
    with out_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(TrialResult("", 0, False, "", 0.0, "")).keys()))
        writer.writeheader()
        for row in results:
            writer.writerow(asdict(row))


def write_summary(results: Sequence[TrialResult], out_path: Path) -> None:
    ensure_dir(out_path.parent)
    values = [r.metric_value for r in results if r.success]
    summary = {
        "trials": len(results),
        "successes": sum(1 for r in results if r.success),
        "metric_name": results[0].metric_name if results else "",
        "unit": results[0].unit if results else "",
        "mean": mean(values),
        "stdev": stdev(values),
        "median": median(values),
        "p95": percentile(values, 0.95),
        "ci95": ci95(values),
    }
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")


def add_common_arguments(parser: argparse.ArgumentParser, default_trials: int, default_warmups: int) -> None:
    parser.add_argument("--trials", type=int, default=default_trials)
    parser.add_argument("--warmups", type=int, default=default_warmups)
    parser.add_argument("--output-dir", type=Path, default=Path("results"))


def finalize_results(experiment: str, results: Sequence[TrialResult], output_dir: Path) -> None:
    ensure_dir(output_dir)
    write_csv(results, output_dir / f"{experiment}.csv")
    write_summary(results, output_dir / f"{experiment}.summary.json")


def fail_if_missing(path: Path, description: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"{description} not found: {path}")


def parse_vars(items: Sequence[str] | None) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for item in items or []:
        if "=" not in item:
            raise ValueError(f"Invalid --var entry: {item}. Expected KEY=VALUE.")
        key, value = item.split("=", 1)
        parsed[key.strip()] = value
    return parsed


def build_context(items: Sequence[str] | None = None, **kwargs: object) -> dict[str, str]:
    context = parse_vars(items)
    for key, value in kwargs.items():
        if value is None:
            continue
        context[key] = str(value)
    return context


def render_template(template: str, context: Mapping[str, object]) -> str:
    rendered_context = {key: str(value) for key, value in context.items()}
    return template.format(**rendered_context)


def combined_output(result: subprocess.CompletedProcess[str]) -> str:
    stdout = result.stdout or ""
    stderr = result.stderr or ""
    if stdout and stderr:
        return f"{stdout}\n{stderr}"
    return stdout or stderr


def require_success(result: subprocess.CompletedProcess[str], step_name: str) -> None:
    if result.returncode == 0:
        return
    output = combined_output(result).strip()
    raise RuntimeError(f"{step_name} failed with exit code {result.returncode}: {output}")


def parse_exit_codes(value: str | None) -> set[int]:
    if not value:
        return set()
    return {int(part.strip()) for part in value.split(",") if part.strip()}


def text_matches(pattern: str | None, text: str) -> bool:
    if not pattern:
        return False
    return re.search(pattern, text, flags=re.MULTILINE) is not None


def add_command_context_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--cwd", type=Path, default=None)
    parser.add_argument("--timeout-sec", type=float, default=30.0)
    parser.add_argument("--var", action="append", default=[], metavar="KEY=VALUE")


def add_denial_probe_arguments(parser: argparse.ArgumentParser) -> None:
    add_command_context_arguments(parser)
    parser.add_argument("--launch-cmd", required=True)
    parser.add_argument("--prepare-cmd")
    parser.add_argument("--mutate-cmd")
    parser.add_argument("--trigger-cmd")
    parser.add_argument("--cleanup-cmd")
    parser.add_argument("--max-wait-sec", type=float, default=10.0)
    parser.add_argument("--poll-interval-ms", type=float, default=10.0)
    parser.add_argument("--deny-match")
    parser.add_argument("--deny-exit-codes", default="")
    parser.add_argument("--deny-on-nonzero", action=argparse.BooleanOptionalAction, default=True)


def add_readiness_probe_arguments(parser: argparse.ArgumentParser) -> None:
    add_command_context_arguments(parser)
    parser.add_argument("--prepare-cmd")
    parser.add_argument("--workflow-cmd")
    parser.add_argument("--repair-cmd")
    parser.add_argument("--ready-cmd")
    parser.add_argument("--cleanup-cmd")
    parser.add_argument("--max-wait-sec", type=float, default=60.0)
    parser.add_argument("--poll-interval-ms", type=float, default=10.0)
    parser.add_argument("--ready-match")


def run_template_command(
    template: str,
    context: Mapping[str, object],
    timeout_sec: float | None,
    cwd: Path | None,
) -> subprocess.CompletedProcess[str]:
    command = render_template(template, context)
    return run_shell_command(command, timeout=timeout_sec, cwd=cwd)


def is_denial_result(
    result: subprocess.CompletedProcess[str],
    *,
    deny_match: str | None,
    deny_exit_codes: set[int],
    deny_on_nonzero: bool,
) -> bool:
    output = combined_output(result)
    if text_matches(deny_match, output):
        return True
    if result.returncode in deny_exit_codes:
        return True
    if deny_on_nonzero and result.returncode != 0:
        return True
    return False


def perform_denial_trial(
    *,
    context: Mapping[str, object],
    prepare_cmd: str | None,
    mutate_cmd: str,
    trigger_cmd: str | None,
    launch_cmd: str,
    cleanup_cmd: str | None,
    cwd: Path | None,
    timeout_sec: float,
    max_wait_sec: float,
    poll_interval_ms: float,
    deny_match: str | None,
    deny_exit_codes: set[int],
    deny_on_nonzero: bool,
) -> tuple[bool, float, str]:
    if prepare_cmd:
        require_success(run_template_command(prepare_cmd, context, timeout_sec, cwd), "prepare")
    require_success(run_template_command(mutate_cmd, context, timeout_sec, cwd), "mutate")
    if trigger_cmd:
        require_success(run_template_command(trigger_cmd, context, timeout_sec, cwd), "trigger")

    start = monotonic_ms()
    deadline = start + (max_wait_sec * 1000.0)
    last_output = ""
    try:
        while monotonic_ms() <= deadline:
            result = run_template_command(launch_cmd, context, timeout_sec, cwd)
            last_output = combined_output(result).strip()
            if is_denial_result(
                result,
                deny_match=deny_match,
                deny_exit_codes=deny_exit_codes,
                deny_on_nonzero=deny_on_nonzero,
            ):
                return True, monotonic_ms() - start, last_output
            time.sleep(poll_interval_ms / 1000.0)
        return False, max_wait_sec * 1000.0, last_output
    finally:
        if cleanup_cmd:
            run_template_command(cleanup_cmd, context, timeout_sec, cwd)


def perform_readiness_trial(
    *,
    context: Mapping[str, object],
    prepare_cmd: str | None,
    workflow_cmd: str | None,
    repair_cmd: str | None,
    ready_cmd: str,
    cleanup_cmd: str | None,
    cwd: Path | None,
    timeout_sec: float,
    max_wait_sec: float,
    poll_interval_ms: float,
    ready_match: str | None,
) -> tuple[bool, float, str]:
    if prepare_cmd:
        require_success(run_template_command(prepare_cmd, context, timeout_sec, cwd), "prepare")
    if workflow_cmd:
        require_success(run_template_command(workflow_cmd, context, timeout_sec, cwd), "workflow")
    if repair_cmd:
        require_success(run_template_command(repair_cmd, context, timeout_sec, cwd), "repair")

    start = monotonic_ms()
    deadline = start + (max_wait_sec * 1000.0)
    last_output = ""
    try:
        while monotonic_ms() <= deadline:
            result = run_template_command(ready_cmd, context, timeout_sec, cwd)
            last_output = combined_output(result).strip()
            if result.returncode == 0 and (not ready_match or text_matches(ready_match, last_output)):
                return True, monotonic_ms() - start, last_output
            time.sleep(poll_interval_ms / 1000.0)
        return False, max_wait_sec * 1000.0, last_output
    finally:
        if cleanup_cmd:
            run_template_command(cleanup_cmd, context, timeout_sec, cwd)


def materialize_input_file(
    *,
    input_path: Path,
    collect_cmd: str | None,
    context: Mapping[str, object],
    cwd: Path | None,
    timeout_sec: float,
    description: str,
) -> None:
    if collect_cmd:
        require_success(run_template_command(collect_cmd, context, timeout_sec, cwd), f"collect {description}")
    fail_if_missing(input_path, description)
