## Artifact Package

This folder stores the non-manuscript artifacts referenced by the paper.

### Structure

- `scripts/`: one script file per experiment or workload in Section 6
- `plotting/`: plotting scripts for the paper figures
- `tests/`: optional test programs or workload drivers

### Script mapping to the paper

Section 6.2:

- `exp_01_local_modification.py`
- `exp_02_stale_rollback.py`
- `exp_03_script_tampering.py`
- `exp_04_plugin_cache_replacement.py`
- `exp_05_baseline_outcomes.py`

Section 6.3:

- `exp_06_benign_install_recovery.py`
- `exp_07_interrupted_update_repair.py`
- `exp_08_plugin_update_recovery.py`
- `exp_09_shared_library_refresh.py`
- `exp_10_script_update_recovery.py`
- `exp_11_power_idle_vs_validation.py`
- `exp_12_validation_energy.py`
- `exp_13_boot_ready_time.py`
- `exp_14_web_management_latency.py`
- `exp_15_preview_startup_latency.py`
- `exp_16_plugin_activation_latency.py`
- `exp_17_edge_ai_loader_latency.py`

Section 6.4:

- `exp_18_rvr_lookup_scalability.py`
- `exp_19_statistical_summary.py`

Shared helpers:

- `common.py`: trial recording, summary statistics, CSV/JSON export
- `run_all_experiments.py`: helper to enumerate scripts

Plotting scripts:

- `plotting/fig5.py`: generates Fig. 5, including the baseline outcome matrix.
- `plotting/fig6.py`: generates Fig. 6 for mutation-burst and cold-reboot recovery results.

### Notes

These scripts exclude the EpochGuard core implementation itself. They are intended to hold the experiment harness, workload drivers, parsers, plotting scripts, and result summarization logic used by the paper. Command-driven experiments require deployment-specific commands and traces from an EpochGuard-enabled system.

### Unified command protocol

The denial-latency scripts (`exp_01` to `exp_04`) now support a common command interface:

- `--prepare-cmd`: reset the environment before each trial
- `--mutate-cmd`: perform the adversarial change
- `--trigger-cmd`: optional extra step after mutation
- `--launch-cmd`: attempt the execution that should be denied
- `--deny-match`: regex matched against stdout/stderr to identify denial
- `--deny-exit-codes`: comma-separated exit codes treated as denial
- `--cleanup-cmd`: optional cleanup after each trial
- `--var KEY=VALUE`: reusable template variables used in commands as `{KEY}`

The recovery-latency scripts (`exp_06`, `exp_07`) use:

- `--prepare-cmd`
- `--workflow-cmd`
- `--repair-cmd`
- `--ready-cmd`
- `--ready-match`
- `--cleanup-cmd`

The input-driven scripts (`exp_11`, `exp_13` to `exp_17`) accept:

- an input file path
- an optional `--collect-cmd` or trace-collection command
- optional `--var KEY=VALUE` template variables

### Minimal examples

Denial experiment:

```bash
python exp_01_local_modification.py \
  --mutate-cmd "cp {bad_bin} {target_bin}" \
  --launch-cmd "{target_bin}" \
  --deny-match "Permission denied|EPERM|denied" \
  --var bad_bin=/tmp/evil_app \
  --var target_bin=/opt/demo/app
```

Recovery experiment:

```bash
python exp_07_interrupted_update_repair.py \
  --workflow-cmd "/usr/local/bin/simulate_interrupted_update.sh" \
  --repair-cmd "/usr/local/bin/run_repair.sh" \
  --ready-cmd "/usr/local/bin/check_ready.sh" \
  --ready-match "READY"
```

Latency collection experiment:

```bash
python exp_14_web_management_latency.py \
  --latency-file results/web_latency.csv \
  --collect-cmd "/usr/local/bin/run_web_benchmark.sh > results/web_latency.csv"
```
