# NIMBUS
NIMBUS (Nucleation Inference via Mixture-Based Uncertainty-quantified Simulation) predicts cloud droplet activation from aerosol composition using a Gaussian Process trained through active learning on a modified pyrcel that accounts for variable surface tension. The model is wrapped in a console for instant predictions. NIMBUS is built to answer one question quickly instead of one lengthy physics simulation at a time: *given this mixture of an ionic salt compounmd and surfactnat, how many cloud droplets form?*

---

## What this actually is

NIMBUS is built from four distinct layers, stacked so the expensive layer (real physics) only has to run as often as necessary, and the first layer (the surrogate) inherits its trustworthiness from being validated against the real simulation.

```
┌─────────────────────────────────────────────────────────┐
│  CONSOLE  (Streamlit)                                    │
│  Pick compounds, mixing ratio, conditions → get a         │
│  prediction + diagnostic plots, instantly                 │
└───────────────────────┬───────────────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────────────┐
│  MIXING + QUERY LAYER                                       │
│  Compound lookup → ZSR/linear mixing rules → dispatches      │
│  to whichever layer below is faster/available                │
└──────────┬─────────────────────────────────┬─────────────────┘
           │                                 │
┌──────────▼───────────────┐    ┌────────────▼─────────────────┐
│  SURROGATE MODEL           │   │  GROUND-TRUTH SIMULATOR        │
│  Gaussian Process, trained │   │  A fork of pyrcel (Rothenberg  │
│  via active learning on a  │◄──┤  & Wang 2016), extended to     │
│  10,000-run dataset. Fast, │   │  support per-species surface   │
│  gives predictive          │   │  tension — the physics that    │
│  uncertainty, not just a   │   │  makes surfactant-based        │
│  point estimate.           │   │  seeding agents representable  │
└─────────────────────────────┘  │  at all. Always the fallback   │
                                  │  and the source of validation. │
                                  └─────────────────────────────────┘
```

## Component breakdown

### 1. The physics core
`pyrcel` is a peer-reviewed, open-source adiabatic cloud parcel model (Rothenberg & Wang 2016), implementing κ-Köhler theory (Petters & Kreidenweis 2007). Its original design assumed every aerosol species shares pure water's surface tension, a reasonable default for the inorganic salts it was built around, but one that makes it impossible to represent surfactant-based cloud-seeding agents, whose entire mechanism of action is *lowering* surface tension.

NIMBUS extends six core modules (`thermo.py`, `aerosol.py`, `equilibrate.py`, `parcel_aux.py`, `model.py`, `activation/_common.py`) to accept an optional per-species surface tension override, threaded through the full simulation pipeline (initial equilibration, the per-timestep growth ODE, and post-solve activation diagnostics) with every default path verified bit-for-bit identical to the unmodified library.

### 2. Simulation Data
`generate_composition_dataset.py` sweeps composition (mixing ratio, two components' κ and σ) and atmospheric conditions (updraft speed, temperature) across a 10,000-point grid, running the actual extended simulator at every point. Checkpointed to disk every 250 rows with automatic resume, since a run this size needs to survive interruption.

### 3. The compound database (some flagged values)
`compound_database.py` holds κ and σ for 20 real compounds, split between well-established atmospheric species (sourced directly from Petters & Kreidenweis 2007's own reference table) and surfactants (sourced from surfactant chemistry literature, since these aren't studied as CCN in atmospheric science). Every entry is tagged `measured` or `derived.` Several surfactant κ values are still placeholders pending proper molecular-property derivation, and the database says so inline rather than presenting them as equally trustworthy.

### 4. The surrogate model: Active learning on real data
`active_learning_surrogate.py` trains a Gaussian Process on the 10,000-row dataset using **pool-based active learning**: it asks, ""if I could only afford to look at a fraction of these, which ones would teach the model the most?" instead of treating all 10,000 values equally. — selecting by predictive uncertainty rather than randomly, and comparing directly against a random-sampling baseline on the same held-out test set.

**Results:** 

### 5. The console
`app.py`, a Streamlit application styled as an instrument panel (not a default form UI), automatically detects whether a trained surrogate exists on disk; if not, every query runs the real simulator directly and says so plainly in a status banner. A "Force live simulation" toggle lets you check any surrogate prediction against ground truth on demand, and a composition sweep tool works in both modes.
---

## Honest limitations

NIMBUS is built to say what it doesn't know, not just what it does:

- **The surface-tension mixing rule (linear averaging) is a stated approximation, not established physics** — unlike the κ mixing rule (ZSR), which is real, standard κ-Köhler theory. Every mixed prediction inherits this caveat.
- **Six surfactant κ values in the compound database are placeholders**, flagged `derived` with a note, pending proper computation from real molecular density data.
- **The simulator is a 0-D parcel model** meaning that there is no turbulence or spatial seeding delivery accounted for.
- **The surrogate only predicts `Nd` and the full trajectories are not reproduced, requiring the "Force live simulation" fallback
  
## Setup

```bash
# Install the physics core from this project's pyrcel fork
pip install "git+https://github.com/yutipurohit/pyrcel.git@add-surface-tension-support"
pip install numpy pandas matplotlib scipy scikit-learn streamlit joblib

# 1. Generate the dataset (long-running, checkpointed — safe to interrupt/resume)
python generate_composition_dataset.py

# 2. Train the surrogate via active learning
python active_learning_surrogate.py

# 3. Launch the console
streamlit run app.py
```

## Roadmap

- [ ] Compute real (not placeholder) κ for the six flagged surfactants
- [ ] Expand the compound database beyond 20 entries
- [ ] Merge upstream pyrcel PR, or maintain as a documented long-term fork
- [ ] *(Descoped for now)* An RL environment for seeding-agent release timing/dosage
      
## Citations

- Rothenberg, D. & Wang, C. (2016). Metamodeling of Droplet Activation for Global Climate Models. *Journal of the Atmospheric Sciences*, 73(3), 1255–1272.
- Petters, M.D. & Kreidenweis, S.M. (2007). A single parameter representation of hygroscopic growth and cloud condensation nucleus activity. *Atmospheric Chemistry and Physics*, 7, 1961–1971.
- Full compound-level citations in `compound_database.py`.
