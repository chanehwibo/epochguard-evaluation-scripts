from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


SCRIPT_ORDER = [
    "exp_01_local_modification.py",
    "exp_02_stale_rollback.py",
    "exp_03_script_tampering.py",
    "exp_04_plugin_cache_replacement.py",
    "exp_05_baseline_outcomes.py",
    "exp_06_benign_install_recovery.py",
    "exp_07_interrupted_update_repair.py",
    "exp_08_plugin_update_recovery.py",
    "exp_09_shared_library_refresh.py",
    "exp_10_script_update_recovery.py",
    "exp_11_power_idle_vs_validation.py",
    "exp_12_validation_energy.py",
    "exp_13_boot_ready_time.py",
    "exp_14_web_management_latency.py",
    "exp_15_preview_startup_latency.py",
    "exp_16_plugin_activation_latency.py",
    "exp_17_edge_ai_loader_latency.py",
    "exp_18_rvr_lookup_scalability.py",
    "exp_19_statistical_summary.py",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the EpochGuard paper experiment scripts in order.")
    parser.add_argument("--scripts-dir", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    for script_name in SCRIPT_ORDER:
        command = [args.python, str(args.scripts_dir / script_name), "--help"]
        if args.dry_run:
            print(" ".join(command))
            continue
        subprocess.run(command, check=False)


if __name__ == "__main__":
    main()
