from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


plt.rcParams.update(
    {
        "font.family": "serif",
        "font.size": 10,
        "axes.labelsize": 11,
        "axes.titlesize": 12,
        "legend.fontsize": 9,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "figure.dpi": 300,
        "lines.linewidth": 1.5,
        "lines.markersize": 6,
    }
)

colors = ["#1f77b4", "#d62728"]
fig, axs = plt.subplots(2, 2, figsize=(10, 7.5))

# Fig. 6(a): validation jobs submitted.
rates = np.array([10, 50, 100, 200])
no_coal_jobs = np.array([996, 988, 965, 918])
no_coal_jobs_err = np.array([3, 6, 15, 32])
eg_coal_jobs = np.array([492, 108, 56, 31])
eg_coal_jobs_err = np.array([20, 9, 5, 4])

axs[0, 0].errorbar(
    rates,
    no_coal_jobs,
    yerr=no_coal_jobs_err,
    fmt="-s",
    capsize=4,
    color=colors[0],
    label="No coalescing",
    markerfacecolor="white",
)
axs[0, 0].errorbar(rates, eg_coal_jobs, yerr=eg_coal_jobs_err, fmt="-o", capsize=4, color=colors[1], label="EpochGuard coalescing")
axs[0, 0].set_title("(a) Validation jobs under mutation bursts")
axs[0, 0].set_xlabel("Mutation rate (events/s)")
axs[0, 0].set_ylabel("Validation jobs / 1,000 mutation attempts")
axs[0, 0].set_xticks(rates)
axs[0, 0].legend()
axs[0, 0].grid(True, linestyle="--", alpha=0.5)

# Fig. 6(b): maximum validation queue length.
no_coal_queue = np.array([6, 136, 1280, 3950])
no_coal_queue_err = np.array([2, 18, 160, 430])
eg_coal_queue = np.array([2, 3, 4, 5])
eg_coal_queue_err = np.array([0.5, 0.6, 0.8, 1.1])

axs[0, 1].errorbar(
    rates,
    no_coal_queue,
    yerr=no_coal_queue_err,
    fmt="-s",
    capsize=4,
    color=colors[0],
    label="No coalescing",
    markerfacecolor="white",
)
axs[0, 1].errorbar(rates, eg_coal_queue, yerr=eg_coal_queue_err, fmt="-o", capsize=4, color=colors[1], label="EpochGuard coalescing")
axs[0, 1].set_title("(b) Maximum validation queue length")
axs[0, 1].set_xlabel("Mutation rate (events/s)")
axs[0, 1].set_ylabel("Max queue length")
axs[0, 1].set_xticks(rates)
axs[0, 1].set_yscale("log")
axs[0, 1].set_ylim(0.8, 8000)
axs[0, 1].set_yticks([1, 10, 100, 1000, 10000])
axs[0, 1].get_yaxis().set_major_formatter(plt.ScalarFormatter())
axs[0, 1].legend()
axs[0, 1].grid(True, linestyle="--", alpha=0.5)

# Fig. 6(c): critical-scope ready time.
components = ["200", "1,000", "10,000"]
x = np.arange(len(components))
width = 0.35
eager_ready = np.array([1.28, 5.62, 50.40])
eager_ready_err = np.array([0.14, 0.41, 2.70])
staged_ready = np.array([0.46, 0.52, 0.91])
staged_ready_err = np.array([0.05, 0.07, 0.13])

axs[1, 0].bar(x - width / 2, eager_ready, width, yerr=eager_ready_err, capsize=4, label="Eager full validation", color=colors[0], alpha=0.8, edgecolor="black")
axs[1, 0].bar(x + width / 2, staged_ready, width, yerr=staged_ready_err, capsize=4, label="Staged/lazy recovery", color=colors[1], alpha=0.8, edgecolor="black", hatch="//")
axs[1, 0].set_title("(c) Critical scope ready time after cold reboot")
axs[1, 0].set_xlabel("Managed components")
axs[1, 0].set_ylabel("Critical scope ready time (s)")
axs[1, 0].set_xticks(x)
axs[1, 0].set_xticklabels(components)
axs[1, 0].legend()
axs[1, 0].grid(True, axis="y", linestyle="--", alpha=0.5)

# Fig. 6(d): full background convergence time.
eager_conv = np.array([1.33, 5.79, 50.90])
eager_conv_err = np.array([0.16, 0.44, 2.80])
staged_conv = np.array([1.92, 8.42, 63.80])
staged_conv_err = np.array([0.24, 0.70, 3.90])

axs[1, 1].bar(x - width / 2, eager_conv, width, yerr=eager_conv_err, capsize=4, label="Eager full validation", color=colors[0], alpha=0.8, edgecolor="black")
axs[1, 1].bar(x + width / 2, staged_conv, width, yerr=staged_conv_err, capsize=4, label="Staged/lazy recovery", color=colors[1], alpha=0.8, edgecolor="black", hatch="//")
axs[1, 1].set_title("(d) Full background convergence time")
axs[1, 1].set_xlabel("Managed components")
axs[1, 1].set_ylabel("Full convergence time (s)")
axs[1, 1].set_xticks(x)
axs[1, 1].set_xticklabels(components)
axs[1, 1].legend(loc="upper left")
axs[1, 1].grid(True, axis="y", linestyle="--", alpha=0.5)

plt.tight_layout(pad=1.5, w_pad=2.0, h_pad=3.0)

out_dir = Path(__file__).resolve().parent
plt.savefig(out_dir / "fig6.png", format="png", dpi=600, bbox_inches="tight")
plt.savefig(out_dir / "fig6_stress_recovery.pdf", format="pdf", dpi=600, bbox_inches="tight")
print(f"Saved figures to: {out_dir}")

plt.show()
