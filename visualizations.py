import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 -- registers 3d projection
from scipy.interpolate import griddata
 
df = pd.read_csv("composition_sweep_dataset.csv")
 
DRAMATIC = LinearSegmentedColormap.from_list(
    "dramatic", ["#0B132B", "#1C7293", "#2A9D8F", "#E9C46A", "#E76F51"]
)
 
plt.rcParams.update({
    "font.size": 11,
    "axes.edgecolor": "#333333",
})
 

#Interpolation grid (kappa_mix, sigma_mix)
grid_k = np.linspace(df["kappa_mix"].min(), df["kappa_mix"].max(), 120)
grid_s = np.linspace(df["sigma_mix"].min(), df["sigma_mix"].max(), 120)
GK, GS = np.meshgrid(grid_k, grid_s)
GNd = griddata(
    (df["kappa_mix"], df["sigma_mix"]), df["Nd"], (GK, GS), method="cubic"
)
 
 
#Gradient field
fig2, ax2 = plt.subplots(figsize=(11, 9))
 
cf = ax2.contourf(GK, GS, GNd, levels=30, cmap=DRAMATIC)
ax2.contour(GK, GS, GNd, levels=10, colors="white", linewidths=0.4, alpha=0.4)
 
ax2.scatter(df["kappa_mix"], df["sigma_mix"], color="white", edgecolor="#0B132B",
            s=18, alpha=0.5, zorder=5)
 
ax2.set_xlabel("kappa_mix")
ax2.set_ylabel("sigma_mix (J/m^2)")
fig2.colorbar(cf, ax=ax2, label="Nd (m^-3)")
 
plt.tight_layout()
plt.savefig("viz_gradient_field.png", dpi=180, bbox_inches="tight")
print("Saved viz_gradient_field.png")
 
#Flipbook across f_B
f_b_vals = sorted(df["f_B"].unique())
show_indices = np.linspace(0, len(f_b_vals) - 1, 6).astype(int)
show_f_b = [f_b_vals[i] for i in show_indices]
 
fig3, axes = plt.subplots(1, 6, figsize=(22, 4.2), sharey=True)
 
kb_grid = np.linspace(df["kappa_B"].min(), df["kappa_B"].max(), 80)
sb_grid = np.linspace(df["sigma_B"].min(), df["sigma_B"].max(), 80)
KB, SB = np.meshgrid(kb_grid, sb_grid)
 
vmin, vmax = df["Nd"].min(), df["Nd"].max()
 
for ax, f_b in zip(axes, show_f_b):
    slice_df = df[np.isclose(df["f_B"], f_b)]
    Z = griddata((slice_df["kappa_B"], slice_df["sigma_B"]), slice_df["Nd"], (KB, SB), method="cubic")
    cf3 = ax.contourf(KB, SB, Z, levels=20, cmap=DRAMATIC, vmin=vmin, vmax=vmax)
    ax.set_title(f"f_B = {f_b:.1f}", fontsize=12)
    ax.set_xlabel("kappa_B")
    if ax is axes[0]:
        ax.set_ylabel("sigma_B")
 
fig3.suptitle("The Activation Landscape Evolving as Surfactant Fraction Increases",
               fontsize=15, y=1.05)
fig3.colorbar(cf3, ax=axes, orientation="horizontal", fraction=0.05, pad=0.25,
              label="Nd (m^-3)", aspect=40)
 
plt.savefig("viz_flipbook.png", dpi=180, bbox_inches="tight")
print("Saved viz_flipbook.png")
 
plt.show()
