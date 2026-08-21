"""Generate a 10,000 row training dataset that will span both composition
and atmospheric conditions"""


import itertools
import os

import numpy as np
import pandas as pd

import pyrcel as pm
from pyrcel.thermo import sigma_w

# Fixed particle size distribution 
MU = 0.05
SIGMA_LOGNORM = 2.0
N_TOTAL = 1000.0
BINS = 50

S0 = -0.02   
P0 = 85000.0 #can also be modified to test different pressures, but not the focus of this study 

#Component A: fixed, known background material
KAPPA_A = 0.61

# Sweep ranges
F_B_RANGE = np.linspace(0.0, 1.0, 10)
KAPPA_B_RANGE = np.linspace(0.10, 0.50, 5)
SIGMA_B_RANGE = np.linspace(0.020, 0.070, 5)
V_RANGE = np.linspace(0.1, 5.0, 8)     # m/s
T0_RANGE = np.linspace(273.0, 293.0, 5)  # K

OUTPUT_CSV = "full_conditions_testing.csv"
CHECKPOINT_EVERY = 250


def mix_kappa(kappa_a, kappa_b, f_b):
    return (1.0 - f_b) * kappa_a + f_b * kappa_b


def mix_sigma_linear(sigma_a, sigma_b, f_b):
    return (1.0 - f_b) * sigma_a + f_b * sigma_b


def run_mixture(kappa_mix, sigma_mix, V, T0):
    aerosol = pm.AerosolSpecies(
        "mixture",
        pm.Lognorm(mu=MU, sigma=SIGMA_LOGNORM, N=N_TOTAL),
        kappa=float(kappa_mix),
        sigma=float(sigma_mix),
        bins=BINS,
    )
    model = pm.ParcelModel([aerosol], V=float(V), T0=float(T0), S0=S0, P0=P0, console=False)
    out = model.run(t_end=300.0, output_dt=10.0, terminate=True)
    activated = bool(model._run_info.get("activated", True)) if model._run_info else True
    return {
        "S_max": float(out.summary["S_max"]),
        "Nd": float(out.Nd),
        "total_act_frac": float(out.summary["total_act_frac"]),
        "activated": activated,
    }


# Sweep, checkpointed saving
combos = list(itertools.product(F_B_RANGE, KAPPA_B_RANGE, SIGMA_B_RANGE, V_RANGE, T0_RANGE))
total = len(combos)
print(f"Total combinations to run: {total}")
print(f"Checkpointing to {OUTPUT_CSV} every {CHECKPOINT_EVERY} rows")

start_index = 0
if os.path.exists(OUTPUT_CSV):
    existing = pd.read_csv(OUTPUT_CSV)
    start_index = len(existing)
    print(f"Found existing {OUTPUT_CSV} with {start_index} rows -- resuming from there.")
    rows_buffer = []
else:
    existing = None
    rows_buffer = []

n_flagged = 0

for i in range(start_index, total):
    f_b, kappa_b, sigma_b, V, T0 = combos[i]

    sigma_a_t = float(sigma_w(T0))  # temperature-dependent -- recomputed every row
    kappa_mix = mix_kappa(KAPPA_A, kappa_b, f_b)
    sigma_mix = mix_sigma_linear(sigma_a_t, sigma_b, f_b)

    result = run_mixture(kappa_mix, sigma_mix, V, T0)
    if not result["activated"]:
        n_flagged += 1

    rows_buffer.append(
        {
            "kappa_A": KAPPA_A,
            "sigma_A": sigma_a_t,
            "kappa_B": kappa_b,
            "sigma_B": sigma_b,
            "f_B": f_b,
            "kappa_mix": kappa_mix,
            "sigma_mix": sigma_mix,
            "sigma_mixing_rule": "linear_approximation",
            "V": V,
            "T0": T0,
            "S_max": result["S_max"],
            "Nd": result["Nd"],
            "total_act_frac": result["total_act_frac"],
            "activated": result["activated"],
        }
    )

    if (i + 1) % 25 == 0 or (i + 1) == total:
        print(f"  [{i+1}/{total}] f_B={f_b:.2f} kappa_B={kappa_b:.3f} sigma_B={sigma_b:.4f} "
              f"V={V:.2f} T0={T0:.1f} -> S_max={result['S_max']*100:.4f}% "
              f"Nd={result['Nd']:.3e} activated={result['activated']}")

    if len(rows_buffer) >= CHECKPOINT_EVERY or (i + 1) == total:
        buffer_df = pd.DataFrame(rows_buffer)
        write_header = not os.path.exists(OUTPUT_CSV)
        buffer_df.to_csv(OUTPUT_CSV, mode="a", header=write_header, index=False)
        print(f"  [checkpoint] wrote {len(rows_buffer)} rows to {OUTPUT_CSV} "
              f"(total on disk: {i + 1 - start_index + start_index})")
        rows_buffer = []

print(f"\nDone. {total} total rows in {OUTPUT_CSV}")
print(f"Rows flagged as never reaching a genuine interior S_max: {n_flagged} "
      f"({100*n_flagged/(total - start_index):.1f}% of this run)")