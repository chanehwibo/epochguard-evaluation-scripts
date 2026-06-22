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

    # Keep this matrix aligned with Fig. 5(b): A = accepted/may execute,
    # P = partial or deployment-dependent coverage, B = blocked.
    rows = [
        BaselineOutcome("local_modification", "no_gate", "A", "No runtime binding after OTA install."),
        BaselineOutcome("local_modification", "digest_only", "B", "Covered by an explicit content-digest recheck."),
        BaselineOutcome("local_modification", "interpreter_only", "A", "Not applicable to native binary drift."),
        BaselineOutcome("local_modification", "ima_ipe", "B", "Covered when the object is in appraisal or execute-policy scope."),
        BaselineOutcome("local_modification", "ima_ipe_ota_refresh", "B", "Covered by refreshed OTA-derived appraisal or execute policy."),
        BaselineOutcome("local_modification", "fs_dm_verity", "B", "Covered for immutable protected placement."),
        BaselineOutcome("local_modification", "epochguard", "B", "RVR revocation before execution."),
        BaselineOutcome("stale_rollback", "no_gate", "A", "No active-epoch readiness state."),
        BaselineOutcome("stale_rollback", "digest_only", "A", "Stale file may still match an old digest."),
        BaselineOutcome("stale_rollback", "interpreter_only", "A", "Checks interpreter, not rolled-back payload."),
        BaselineOutcome("stale_rollback", "ima_ipe", "A", "Static content or execute policy does not encode active epoch readiness."),
        BaselineOutcome("stale_rollback", "ima_ipe_ota_refresh", "B", "Refreshed OTA-derived policy can reject artifacts outside the current epoch."),
        BaselineOutcome("stale_rollback", "fs_dm_verity", "A", "Immutable verification alone does not encode active OTA epoch state."),
        BaselineOutcome("stale_rollback", "epochguard", "B", "Active epoch mismatch blocks launch."),
        BaselineOutcome("update_cache_pollution", "no_gate", "A", "No evidence-bound recovery for polluted cache content."),
        BaselineOutcome("update_cache_pollution", "digest_only", "P", "Depends on whether cache content is explicitly rehashed before use."),
        BaselineOutcome("update_cache_pollution", "interpreter_only", "A", "Irrelevant to update-cache artifacts."),
        BaselineOutcome("update_cache_pollution", "ima_ipe", "P", "Coverage depends on whether cache paths are in policy scope."),
        BaselineOutcome("update_cache_pollution", "ima_ipe_ota_refresh", "P", "Refresh helps only for covered cache objects and recovery paths."),
        BaselineOutcome("update_cache_pollution", "fs_dm_verity", "P", "Limited for mutable staging and repair-cache locations."),
        BaselineOutcome("update_cache_pollution", "epochguard", "B", "Evidence-bound recovery keeps polluted cache content non-Ready."),
        BaselineOutcome("script_tampering", "no_gate", "A", "No script-payload validation."),
        BaselineOutcome("script_tampering", "digest_only", "P", "Depends on external script hash trigger."),
        BaselineOutcome("script_tampering", "interpreter_only", "P", "Only covers interpreter integrity, not all file-backed script payloads."),
        BaselineOutcome("script_tampering", "ima_ipe", "P", "Coverage depends on script appraisal policy."),
        BaselineOutcome("script_tampering", "ima_ipe_ota_refresh", "P", "Refresh helps only when script payloads are covered by policy."),
        BaselineOutcome("script_tampering", "fs_dm_verity", "P", "Works only for immutable script placement."),
        BaselineOutcome("script_tampering", "epochguard", "B", "Resolves file-backed payload before exec."),
        BaselineOutcome("plugin_replacement", "no_gate", "A", "No runtime freshness enforcement."),
        BaselineOutcome("plugin_replacement", "digest_only", "P", "Digest-only checking does not encode active epoch readiness."),
        BaselineOutcome("plugin_replacement", "interpreter_only", "A", "Irrelevant to plugin files."),
        BaselineOutcome("plugin_replacement", "ima_ipe", "P", "Depends on policy scope and managed plugin path."),
        BaselineOutcome("plugin_replacement", "ima_ipe_ota_refresh", "P", "Refresh helps only for covered plugin objects and load paths."),
        BaselineOutcome("plugin_replacement", "fs_dm_verity", "P", "Mutable plugin paths limit coverage."),
        BaselineOutcome("plugin_replacement", "epochguard", "B", "Pending state blocks stale replacement."),
        BaselineOutcome("metadata_replay", "no_gate", "A", "Local metadata is not authoritative without runtime binding."),
        BaselineOutcome("metadata_replay", "digest_only", "P", "Digest evidence can be replayed without active-epoch readiness."),
        BaselineOutcome("metadata_replay", "interpreter_only", "A", "Irrelevant to replayed metadata."),
        BaselineOutcome("metadata_replay", "ima_ipe", "P", "Policy metadata replay depends on deployment-specific protection."),
        BaselineOutcome("metadata_replay", "ima_ipe_ota_refresh", "P", "Refresh helps only when replayed state cannot override the current policy."),
        BaselineOutcome("metadata_replay", "fs_dm_verity", "P", "May protect immutable metadata but not mutable local readiness state."),
        BaselineOutcome("metadata_replay", "epochguard", "B", "Persistent metadata is a hint and cannot restore Ready state by itself."),
    ]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


if __name__ == "__main__":
    main()
