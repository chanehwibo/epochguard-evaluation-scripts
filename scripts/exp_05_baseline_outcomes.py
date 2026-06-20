from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class BaselineOutcome:
    case_id: str
    baseline: str
    outcome: str
    note: str


def main() -> None:
    parser = argparse.ArgumentParser(description="Experiment 6.2: baseline outcome matrix.")
    parser.add_argument("--output", type=Path, default=Path("results/exp_05_baseline_outcomes.csv"))
    args = parser.parse_args()

    rows = [
        BaselineOutcome("local_modification", "no_gate", "A", "No runtime binding after OTA install."),
        BaselineOutcome("local_modification", "digest_only", "P", "Blocks only after explicit digest recheck."),
        BaselineOutcome("local_modification", "interpreter_only", "A", "Not applicable to native binary drift."),
        BaselineOutcome("local_modification", "ima_ipe", "P", "Policy-dependent object coverage."),
        BaselineOutcome("local_modification", "fs_dm_verity", "P", "Works only for immutable protected placement."),
        BaselineOutcome("local_modification", "epochguard", "B", "RVR revocation before execution."),
        BaselineOutcome("stale_rollback", "no_gate", "A", "No active-epoch readiness state."),
        BaselineOutcome("stale_rollback", "digest_only", "A", "Stale file may still match an old digest."),
        BaselineOutcome("stale_rollback", "interpreter_only", "A", "Checks interpreter, not rolled-back payload."),
        BaselineOutcome("stale_rollback", "ima_ipe", "P", "Needs extra epoch-aware integration."),
        BaselineOutcome("stale_rollback", "fs_dm_verity", "P", "Placement and versioning dependent."),
        BaselineOutcome("stale_rollback", "epochguard", "B", "Active epoch mismatch blocks launch."),
        BaselineOutcome("script_tampering", "no_gate", "A", "No script-payload validation."),
        BaselineOutcome("script_tampering", "digest_only", "P", "Depends on external script hash trigger."),
        BaselineOutcome("script_tampering", "interpreter_only", "A", "Interpreter binary remains intact."),
        BaselineOutcome("script_tampering", "ima_ipe", "P", "Coverage depends on script appraisal policy."),
        BaselineOutcome("script_tampering", "fs_dm_verity", "P", "Works only for immutable script placement."),
        BaselineOutcome("script_tampering", "epochguard", "B", "Resolves file-backed payload before exec."),
        BaselineOutcome("plugin_cache_replacement", "no_gate", "A", "No runtime freshness enforcement."),
        BaselineOutcome("plugin_cache_replacement", "digest_only", "P", "Digest-only does not encode active epoch."),
        BaselineOutcome("plugin_cache_replacement", "interpreter_only", "A", "Irrelevant to plugin/cache files."),
        BaselineOutcome("plugin_cache_replacement", "ima_ipe", "P", "Depends on policy scope and managed path."),
        BaselineOutcome("plugin_cache_replacement", "fs_dm_verity", "P", "Mutable cache/plugin paths limit coverage."),
        BaselineOutcome("plugin_cache_replacement", "epochguard", "B", "Pending state blocks stale replacement."),
    ]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


if __name__ == "__main__":
    main()
