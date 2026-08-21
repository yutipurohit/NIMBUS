"""Generating a synthetic training dataset"""

import itertools

import numpy as np
import pandas as pd

import pyrcel as pm
from pyrcel.thermo import sigma_w

#Unchanging parcel initial conditions
V = 1.0
T0 = 283.0
S0 = -0.02
P0 = 85000.0

#Unchanging particle size distribution
MU = 0.05       #median dry radius, micron
SIGMA_LOGNORM = 2.0
N_TOTAL = 1000.0
BINS = 50

# Component A: fixed, known background material (ammonium-sulfate-like)
KAPPA_A = 0.61
SIGMA_A = float(sigma_w(T0))#same as pure water since inorganic salts don't reduce surface tension

# Component B: surfactant-like component
KAPPA_B_RANGE = np.linspace(0.10, 0.50, 5)
SIGMA_B_RANGE = np.linspace(0.020, 0.070, 5)

# Mixing ratio sweep
F_B_RANGE = np.linspace(0.0, 1.0, 11)

OUTPUT_CSV = "composition_sweep_dataset.csv"


def mix_kappa(kappa_a, kappa_b, f_b):
    #ZSR volume-fraction weighted average
    return (1.0 - f_b) * kappa_a + f_b * kappa_b


def mix_sigma_linear(sigma_a, sigma_b, f_b):
    #Simple linear approximation - NOT ESTABLISHED RULE
    return (1.0 - f_b) * sigma_a + f_b * sigma_b


def run_mixture(kappa_mix, sigma_mix):
    #Run one parcel simulation for given effective pair
    aerosol = pm.AerosolSpecies(
        "mixture",
        pm.Lognorm(mu=MU, sigma=SIGMA_LOGNORM, N=N_TOTAL),
        kappa=float(kappa_mix),
        sigma=float(sigma_mix),
        bins=BINS,
    )
    model = pm.ParcelModel([aerosol], V=V, T0=T0, S0=S0, P0=P0, console=False)
    out = model.run(t_end=300.0, output_dt=10.0, terminate=True)

    activated = bool(model._run_info.get("activated", True)) if model._run_info else True

    return {
        "S_max": float(out.summary["S_max"]),
        "Nd": float(out.Nd),
        "total_act_frac": float(out.summary["total_act_frac"]),
        "activated": activated,
    }


#Sweep
combos = list(itertools.product(F_B_RANGE, KAPPA_B_RANGE, SIGMA_B_RANGE))
print(f"Total combinations to run: {len(combos)}")

rows = []
n_flagged = 0

for i, (f_b, kappa_b, sigma_b) in enumerate(combos):
    kappa_mix = mix_kappa(KAPPA_A, kappa_b, f_b)
    sigma_mix = mix_sigma_linear(SIGMA_A, sigma_b, f_b)

    result = run_mixture(kappa_mix, sigma_mix)
    if not result["activated"]:
        n_flagged += 1

    rows.append(
        {
            "kappa_A": KAPPA_A,
            "sigma_A": SIGMA_A,
            "kappa_B": kappa_b,
            "sigma_B": sigma_b,
            "f_B": f_b,
            "kappa_mix": kappa_mix,
            "sigma_mix": sigma_mix,
            "sigma_mixing_rule": "linear_approximation",  # flagged, not established physics
            "S_max": result["S_max"],
            "Nd": result["Nd"],
            "total_act_frac": result["total_act_frac"],
            "activated": result["activated"],
        }
    )

    if (i + 1) % 25 == 0 or (i + 1) == len(combos):
        print(f"  [{i+1}/{len(combos)}] f_B={f_b:.2f} kappa_B={kappa_b:.3f} "
              f"sigma_B={sigma_b:.4f} -> S_max={result['S_max']*100:.4f}% "
              f"Nd={result['Nd']:.3e} activated={result['activated']}")

df = pd.DataFrame(rows)
df.to_csv(OUTPUT_CSV, index=False)

print(f"\nSaved {len(df)} rows to {OUTPUT_CSV}")
print(f"Rows never reaching interior S_max: {n_flagged} "
      f"({100*n_flagged/len(df):.1f}%)")
