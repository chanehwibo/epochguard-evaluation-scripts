from pathlib import Path

import matplotlib.colors as mcolors
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np


FONT_TITLE = 11
FONT_LABEL = 10
FONT_TICK = 9
FONT_ANNOTATE = 9
FONT_LEGEND = 9

COLOR_BASE = "#7f7f7f"
COLOR_EPOCH = "#1f77b4"
COLOR_WARN = "#d62728"
COLOR_PARTIAL = "#ff7f0e"
COLOR_GREEN = "#2ca02c"

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans"]
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42

fig, axs = plt.subplots(2, 2, figsize=(12, 8))

# Fig. 5(a): attack blocking latency.
ax_a = axs[0, 0]
scenarios_a = ["Local\nmodification", "Stale\nrollback", "Script\ntampering", "Plugin/cache\nrepl."]
means_a = [1.15, 1.42, 2.75, 1.88]
sds_a = [0.18, 0.22, 0.45, 0.31]

x_a = np.arange(len(scenarios_a))
bars_a = ax_a.bar(x_a, means_a, yerr=sds_a, color=COLOR_EPOCH, capsize=4, alpha=0.85, width=0.5)

ax_a.set_ylabel("Mutation-to-denial latency (ms)", fontsize=FONT_LABEL)
ax_a.set_title("(a) Mutation-to-denial latency", fontsize=FONT_TITLE, pad=10)
ax_a.set_xticks(x_a)
ax_a.set_xticklabels(scenarios_a, fontsize=FONT_TICK)
ax_a.tick_params(axis="y", labelsize=FONT_TICK)
ax_a.grid(True, axis="y", linestyle="--", alpha=0.5)
ax_a.set_ylim(0, 4.0)

for i, bar in enumerate(bars_a):
    yval = bar.get_height()
    ax_a.annotate(
        f"{yval:.2f}",
        xy=(bar.get_x() + bar.get_width() / 2, yval + sds_a[i]),
        xytext=(0, 3),
        textcoords="offset points",
        ha="center",
        va="bottom",
        fontsize=FONT_ANNOTATE,
        fontweight="bold",
    )

# Fig. 5(b): baseline security outcomes.
ax_b = axs[0, 1]

# Columns: No gate, Digest, Interp., IMA/IPE, IMA/IPE+OTA, Verity, EpochGuard.
# Encoding: 0 = A (accepted), 1 = P (partial), 2 = B (blocked).
heatmap_data = np.array(
    [
        [0, 2, 0, 2, 2, 2, 2],  # Local modification
        [0, 0, 0, 0, 2, 0, 2],  # Stale rollback
        [0, 1, 0, 1, 1, 1, 2],  # Update-cache pollution
        [0, 1, 1, 1, 1, 1, 2],  # Script tampering
        [0, 1, 0, 1, 1, 1, 2],  # Plugin replacement
        [0, 1, 0, 1, 1, 1, 2],  # Metadata replay
    ]
)

cmap = mcolors.ListedColormap([COLOR_WARN, COLOR_PARTIAL, COLOR_EPOCH])
norm = mcolors.BoundaryNorm([-0.5, 0.5, 1.5, 2.5], cmap.N)
ax_b.imshow(heatmap_data, cmap=cmap, norm=norm, aspect="auto", alpha=0.85)

text_labels = ["A", "P", "B"]
for i in range(heatmap_data.shape[0]):
    for j in range(heatmap_data.shape[1]):
        val = heatmap_data[i, j]
        text_color = "k" if val == 1 else "w"
        ax_b.text(
            j,
            i,
            text_labels[val],
            ha="center",
            va="center",
            color=text_color,
            fontweight="bold",
            fontsize=FONT_ANNOTATE,
        )

x_labels_b = ["No gate", "Digest", "Interp.", "IMA/IPE", "IMA/IPE\n+OTA", "Verity", "EpochGuard"]
y_labels_b = [
    "Local\nmodification",
    "Stale\nrollback",
    "Update-cache\npollution",
    "Script\ntampering",
    "Plugin\nreplacement",
    "Metadata\nreplay",
]

ax_b.set_xticks(np.arange(len(x_labels_b)))
ax_b.set_yticks(np.arange(len(y_labels_b)))
ax_b.set_xticklabels(x_labels_b, fontsize=FONT_TICK)
ax_b.set_yticklabels(y_labels_b, fontsize=FONT_TICK)
ax_b.set_title("(b) Baseline security outcomes", fontsize=FONT_TITLE, pad=10)
ax_b.text(
    0.5,
    -0.22,
    "A = accepted/may execute; P = partial; B = blocked",
    ha="center",
    va="top",
    transform=ax_b.transAxes,
    fontsize=FONT_TICK,
    color="#333333",
)

# Fig. 5(c): benign recovery and operational cost.
pos_c = axs[1, 0].get_subplotspec()
axs[1, 0].remove()
gs_c = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=pos_c, wspace=0.35, width_ratios=[1.3, 1])

ax_c_title = fig.add_subplot(gs_c[:])
ax_c_title.axis("off")
ax_c_title.set_title("(c) Benign recovery and operational cost", fontsize=FONT_TITLE, pad=20)

ax_c1 = fig.add_subplot(gs_c[0, 0])
ax_c2 = fig.add_subplot(gs_c[0, 1])

bars_c1 = ax_c1.bar(
    ["Baseline", "EpochGuard"],
    [19.15, 20.85],
    yerr=[0.52, 0.88],
    color=[COLOR_BASE, COLOR_EPOCH],
    capsize=4,
    width=0.55,
    alpha=0.85,
)
ax_c1.set_ylabel("Service-ready time (s)", fontsize=FONT_LABEL)
ax_c1.set_title("Post-OTA service-ready", fontsize=FONT_LABEL, color="#333333")
ax_c1.tick_params(axis="y", labelsize=FONT_TICK)
ax_c1.grid(True, axis="y", linestyle="--", alpha=0.5)
ax_c1.set_ylim(0, 28)

for i, bar in enumerate(bars_c1):
    yval = bar.get_height()
    err = [0.52, 0.88][i]
    ax_c1.annotate(
        f"{yval:.2f}",
        xy=(bar.get_x() + bar.get_width() / 2, yval + err),
        xytext=(0, 3),
        textcoords="offset points",
        ha="center",
        va="bottom",
        fontsize=FONT_ANNOTATE,
    )

ax_c2.bar(["EpochGuard"], [850], yerr=[185], color=COLOR_EPOCH, width=0.32, alpha=0.85, capsize=4)
ax_c2.set_xlim(-0.5, 0.5)
ax_c2.set_ylabel("Recovery latency (ms)", fontsize=FONT_LABEL)
ax_c2.set_title("EpochGuard recovery latency", fontsize=FONT_LABEL, color="#333333")
ax_c2.tick_params(axis="y", labelsize=FONT_TICK)
ax_c2.grid(True, axis="y", linestyle="--", alpha=0.5)
ax_c2.set_ylim(0, 2000)
ax_c2.annotate(
    "850 ms\n(P95: 1240 ms)",
    xy=(0, 1035),
    xytext=(0, 5),
    textcoords="offset points",
    ha="center",
    va="bottom",
    fontsize=FONT_ANNOTATE,
    fontweight="bold",
)

annot_text = (
    "Operational Costs:\n"
    "- Idle power: +0.03 W\n"
    "- Validation energy: +14.3%\n"
    "- Cost/component: 56.0 mJ\n"
    "- App P95: +4.3%-6.6%"
)
ax_c2.text(
    0.5,
    0.98,
    annot_text,
    transform=ax_c2.transAxes,
    fontsize=FONT_ANNOTATE - 1,
    verticalalignment="top",
    horizontalalignment="center",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="#f8f9fa", edgecolor=COLOR_BASE, alpha=0.9),
    zorder=10,
)

# Fig. 5(d): RVR lookup scalability.
ax_d = axs[1, 1]

x_ins = [100, 1000, 10000, 100000]
y_warm = [1.1, 1.2, 1.3, 1.6]
y_cold = [158, 210, 450, 820]

ax_d.plot(x_ins, y_warm, marker="o", markersize=6, linestyle="-", color=COLOR_GREEN, linewidth=2, label="Warm-cache lookup")
ax_d.plot(x_ins, y_cold, marker="s", markersize=6, linestyle="-", color=COLOR_EPOCH, linewidth=2, label="Cold RVR lookup")
ax_d.set_xscale("log")
ax_d.set_yscale("log")
ax_d.set_xlabel("Managed components", fontsize=FONT_LABEL)
ax_d.set_ylabel("Lookup latency (us)", fontsize=FONT_LABEL)
ax_d.set_title("(d) RVR lookup scalability", fontsize=FONT_TITLE, pad=10)
ax_d.tick_params(axis="both", which="major", labelsize=FONT_TICK)
ax_d.grid(True, which="both", linestyle=":", alpha=0.4)

for i in range(len(x_ins)):
    ax_d.annotate(
        f"{y_warm[i]}",
        xy=(x_ins[i], y_warm[i]),
        xytext=(0, 6),
        textcoords="offset points",
        ha="center",
        va="bottom",
        fontsize=FONT_ANNOTATE,
        color=COLOR_GREEN,
    )
    ax_d.annotate(
        f"{y_cold[i]}",
        xy=(x_ins[i], y_cold[i]),
        xytext=(0, -12),
        textcoords="offset points",
        ha="center",
        va="top",
        fontsize=FONT_ANNOTATE,
        color=COLOR_EPOCH,
    )

ax_d.annotate(
    "2.4 MB metadata\nat $10^4$ components",
    xy=(10000, 450),
    xytext=(-20, -30),
    textcoords="offset points",
    ha="center",
    va="top",
    fontsize=FONT_ANNOTATE,
    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=COLOR_BASE, alpha=0.9),
    arrowprops=dict(arrowstyle="->", color=COLOR_BASE, connectionstyle="arc3,rad=-0.1"),
)
ax_d.set_ylim(0.5, 3000)
ax_d.legend(loc="upper left", fontsize=FONT_LEGEND, framealpha=0.9)

plt.subplots_adjust(left=0.06, right=0.98, top=0.93, bottom=0.08, wspace=0.28, hspace=0.48)

out_dir = Path(__file__).resolve().parent
plt.savefig(out_dir / "Fig5_Evaluation_Summary.pdf", format="pdf", dpi=600, bbox_inches="tight")
plt.savefig(out_dir / "Fig5_Evaluation_Summary.png", dpi=600, bbox_inches="tight")
print(f"Saved figures to: {out_dir}")

plt.show()
