import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

df = pd.read_csv("composition_sweep_dataset.csv")
print(f"Loaded {len(df)} rows, {df['activated'].sum()} activated ({100*df['activated'].mean():.1f}%)")

CREAM = "#F4F1EA"
TEAL = "#2A9D8F"
DEEP_TEAL = "#1D3557"
CORAL = "#E76F51"
AMBER = "#E9C46A"
BLUE = "#457B9D"
RED = "#E63946"

seq_cmap = LinearSegmentedColormap.from_list("cream_teal", [CREAM, TEAL, DEEP_TEAL])
div_cmap = LinearSegmentedColormap.from_list("coral_teal", [CORAL, "#FFFFFF", TEAL])

plt.rcParams.update({
    "font.size": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
})

fig = plt.figure(figsize=(20,7))
gs = fig.add_gridspec(1, 3, wspace=0.65)

#Correlation heatmap
ax3 = fig.add_subplot(gs[0, 0])
corr_cols = ["kappa_B", "sigma_B", "f_B", "kappa_mix", "sigma_mix", "S_max", "Nd"]
corr = df[corr_cols].corr()
im = ax3.imshow(corr, cmap=div_cmap, vmin=-1, vmax=1)
ax3.set_xticks(range(len(corr_cols)))
ax3.set_yticks(range(len(corr_cols)))
ax3.set_xticklabels(corr_cols, rotation=45, ha="right")
ax3.set_yticklabels(corr_cols)
ax3.grid(False)
for i in range(len(corr_cols)):
    for j in range(len(corr_cols)):
        ax3.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center",
                  fontsize=4, color="white" if abs(corr.iloc[i, j]) > 0.5 else "black")
ax3.set_title("Correlation matrix")
fig.colorbar(im, ax=ax3, fraction=0.046)

#kappa_mix/sigma_mix landscape
ax4 = fig.add_subplot(gs[0, 1])
sc = ax4.scatter(df["kappa_mix"], df["sigma_mix"], c=df["Nd"], cmap=seq_cmap,
                  s=50, edgecolors="white", linewidths=0.4)
ax4.set_xlabel("kappa_mix (effective)")
ax4.set_ylabel("sigma_mix (effective), J/m^2")
ax4.set_title("Nd across the real physical drivers")
fig.colorbar(sc, ax=ax4, label="Nd (m^-3)", fraction=0.046)


#f_B lines for different combos
ax6 = fig.add_subplot(gs[0, 2])
kappa_b_vals = sorted(df["kappa_B"].unique())
sigma_b_vals = sorted(df["sigma_B"].unique())
combos_to_show = [
    (kappa_b_vals[0], sigma_b_vals[0], "low kappa_B, low sigma_B"),
    (kappa_b_vals[-1], sigma_b_vals[-1], "high kappa_B, high sigma_B"),
    (kappa_b_vals[0], sigma_b_vals[-1], "low kappa_B, high sigma_B"),
    (kappa_b_vals[-1], sigma_b_vals[0], "high kappa_B, low sigma_B"),
]
colors = [RED, TEAL, AMBER, BLUE]
for (kb, sb, label), color in zip(combos_to_show, colors):
    line_df = df[np.isclose(df["kappa_B"], kb) & np.isclose(df["sigma_B"], sb)].sort_values("f_B")
    ax6.plot(line_df["f_B"], line_df["Nd"], "o-", color=color, label=label, linewidth=2)
ax6.set_xlabel("f_B (fraction of aerosol population B)")
ax6.set_ylabel("Nd (m^-3)")
ax6.set_title("Does increasing the B fraction help or hurt activation?\n(depding on aerosol properties)")
ax6.legend(fontsize=8, frameon=False)

plt.savefig("Exploratory_Data_Analysis.png", dpi=180, bbox_inches="tight")
plt.show()

