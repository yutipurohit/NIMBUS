import os
 
import pyrcel as pm
from pyrcel.thermo import sigma_w
 
from compound_database import get_compound
 
SURROGATE_PATH = "surrogate_model.pkl"
SURROGATE_SCALER_PATH = "surrogate_scaler.pkl"
 
MU = 0.05
SIGMA_LOGNORM = 2.0
N_TOTAL = 1000.0
BINS = 50
S0 = -0.02
P0 = 85000.0
 
 
def mix_kappa(kappa_a, kappa_b, f_b):
    return (1.0 - f_b) * kappa_a + f_b * kappa_b
 
 
def mix_sigma_linear(sigma_a, sigma_b, f_b):
    return (1.0 - f_b) * sigma_a + f_b * sigma_b
 
 
def resolve_mixture(compound_a_key, compound_b_key, f_b, T0):
    """Look up two compounds and compute their mixed kappa/sigma at a given T0."""
    a = get_compound(compound_a_key)
    b = get_compound(compound_b_key)
 
    sigma_a = a["sigma"] if a["sigma"] is not None else float(sigma_w(T0))
    sigma_b = b["sigma"] if b["sigma"] is not None else float(sigma_w(T0))
 
    return {
        "kappa_mix": mix_kappa(a["kappa"], b["kappa"], f_b),
        "sigma_mix": mix_sigma_linear(sigma_a, sigma_b, f_b),
        "compound_a": a,
        "compound_b": b,
        "sigma_a_used": sigma_a,
        "sigma_b_used": sigma_b,
        "any_derived_kappa": a["kappa_type"] == "derived" or b["kappa_type"] == "derived",
    }
 
 
def load_surrogate():
    """Returns (gp, scaler) if a trained model exists on disk, else (None, None)."""
    if os.path.exists(SURROGATE_PATH) and os.path.exists(SURROGATE_SCALER_PATH):
        import joblib
        return joblib.load(SURROGATE_PATH), joblib.load(SURROGATE_SCALER_PATH)
    return None, None
 
 
def run_live_simulation(kappa_mix, sigma_mix, V, T0):
    """Full pyrcel simulation"""
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
    return model, out, activated
 
 
def predict(kappa_mix, sigma_mix, V, T0, force_live=False):
    """Dispatch to the surrogate if trained, else run the real simulation.
 
    force_live=True always runs the real pyrcel simulation, even if a
    trained surrogate exists. Typically needed whenever the caller wants the actual
    trajectory/radius-profile data, which the surrogate can't provide since
    it never runs a real simulation.
     """
    gp, scaler = load_surrogate()
    if gp is not None and not force_live:
        X = scaler.transform([[kappa_mix, sigma_mix, V, T0]])
        nd_pred, nd_std = gp.predict(X, return_std=True)
        return {
            "Nd": float(nd_pred[0]),
            "Nd_std": float(nd_std[0]),
            "method": "surrogate",
        }
 
    model, out, activated = run_live_simulation(kappa_mix, sigma_mix, V, T0)
    return {
        "S_max": float(out.summary["S_max"]),
        "Nd": float(out.Nd),
        "activated": activated,
        "method": "live_simulation",
        "model": model,
        "out": out,
    }
