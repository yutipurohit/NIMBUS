import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import joblib
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel, ConstantKernel
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

INPUT_CSV = "full_conditions_testing.csv"
FEATURES = ["kappa_mix", "sigma_mix", "V", "T0"]
TARGET = "Nd"

RANDOM_SEED = 0
N_TEST = 1000        
N_INITIAL = 20
N_ITERATIONS = 150   
CHECK_EVERY = 15     
CANDIDATE_SAMPLE = 500  

SURROGATE_PATH = "surrogate_model.pkl"
SURROGATE_SCALER_PATH = "surrogate_scaler.pkl"


def make_gp(n_restarts=3):
    kernel = (
        ConstantKernel(1.0, constant_value_bounds=(1e-2, 1e2))
        * RBF(length_scale=[1.0, 1.0, 1.0, 1.0], length_scale_bounds=(1e-2, 1e2))
        + WhiteKernel(noise_level=1e-3, noise_level_bounds=(1e-8, 1e0))
    )
    return GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=n_restarts, normalize_y=True)


def fit_and_score(X, y, scaler, test_X, test_y, n_restarts=10):
    gp = make_gp(n_restarts=n_restarts)
    gp.fit(scaler.transform(X), y)
    pred = gp.predict(scaler.transform(test_X))
    rmse = float(np.sqrt(mean_squared_error(test_y, pred)))
    return gp, rmse


df = pd.read_csv(INPUT_CSV)
print(f"Loaded {len(df)} rows")
df = df[df["activated"]].reset_index(drop=True)
print(f"{len(df)} rows after dropping non-activated (never reached interior S_max)")

rng = np.random.default_rng(RANDOM_SEED)
shuffled = df.sample(frac=1.0, random_state=RANDOM_SEED).reset_index(drop=True)

test_df = shuffled.iloc[:N_TEST]
pool_df = shuffled.iloc[N_TEST:].reset_index(drop=True)
print(f"Test set: {len(test_df)} rows | Candidate pool: {len(pool_df)} rows")

test_X = test_df[FEATURES].values
test_y = test_df[TARGET].values


def run_strategy(strategy, seed):
    local_rng = np.random.default_rng(seed)
    pool = pool_df.copy().reset_index(drop=True)

    init_idx = local_rng.choice(len(pool), size=N_INITIAL, replace=False)
    train_X = pool.loc[init_idx, FEATURES].values
    train_y = pool.loc[init_idx, TARGET].values
    pool = pool.drop(index=init_idx).reset_index(drop=True)

    scaler = StandardScaler().fit(train_X)
    gp, rmse = fit_and_score(train_X, train_y, scaler, test_X, test_y)
    rmse_history = [rmse]
    n_sims_history = [len(train_X)]

    picks_since_refit = 0
    for it in range(N_ITERATIONS):
        if len(pool) == 0:
            break

        if strategy == "active":
            n_candidates = min(CANDIDATE_SAMPLE, len(pool))
            candidate_idx = local_rng.choice(len(pool), size=n_candidates, replace=False)
            candidates = pool.iloc[candidate_idx]
            _, std = gp.predict(scaler.transform(candidates[FEATURES].values), return_std=True)
            next_idx = int(candidate_idx[np.argmax(std)])
        else:
            next_idx = int(local_rng.integers(0, len(pool)))

        row = pool.iloc[next_idx]
        train_X = np.vstack([train_X, row[FEATURES].values.astype(float)])
        train_y = np.append(train_y, row[TARGET])
        pool = pool.drop(index=pool.index[next_idx]).reset_index(drop=True)

        picks_since_refit += 1
        if picks_since_refit >= CHECK_EVERY or it == N_ITERATIONS - 1:
            scaler = StandardScaler().fit(train_X)
            gp, rmse = fit_and_score(train_X, train_y, scaler, test_X, test_y)
            rmse_history.append(rmse)
            n_sims_history.append(len(train_X))
            picks_since_refit = 0
            print(f"  [{strategy}] n_sims={len(train_X)} RMSE={rmse:.4e}")

    return rmse_history, n_sims_history, gp, train_X, train_y, scaler


print("\nActive learning strategy")
active_rmse, active_n, active_gp, active_X, active_y, active_scaler = run_strategy("active", RANDOM_SEED)

print("\nRandom sampling baseline")
random_rmse, random_n, _, _, _, _ = run_strategy("random", RANDOM_SEED + 1)

joblib.dump(active_gp, SURROGATE_PATH)
joblib.dump(active_scaler, SURROGATE_SCALER_PATH)
print(f"\nSaved surrogate model to {SURROGATE_PATH} / {SURROGATE_SCALER_PATH}")
print("app.py will automatically switch to surrogate mode on next run.")

final_pred = active_gp.predict(active_scaler.transform(test_X))
final_r2 = r2_score(test_y, final_pred)
final_mae = mean_absolute_error(test_y, final_pred)
print(f"\nFinal active-learning model performance (on held-out test set)")
print(f"RMSE: {active_rmse[-1]:.4e}")
print(f"MAE:  {final_mae:.4e}")
print(f"R^2:  {final_r2:.4f}  (fraction of variance in Nd explained by the model)")

fig1, ax1 = plt.subplots(figsize=(9, 6))
ax1.plot(active_n, active_rmse, "o-", color="#E63946", label="active learning (uncertainty sampling)")
ax1.plot(random_n, random_rmse, "o-", color="#457B9D", label="random sampling")
ax1.set_xlabel("Number of simulations used (out of 10,000 total)")
ax1.set_ylabel("Test RMSE (Nd, m^-3)")
ax1.set_title("Sample efficiency active learning vs random sampling")
ax1.legend(frameon=False)
ax1.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("active_learning_comparison.png", dpi=150)
print("Saved active_learning_comparison.png")

v_slices = [pool_df["V"].min(), pool_df["V"].median(), pool_df["V"].max()]
t_fixed = pool_df["T0"].median()

fig2, axes = plt.subplots(1, 3, figsize=(18, 5.5))
grid_k = np.linspace(df["kappa_mix"].min(), df["kappa_mix"].max(), 50)
grid_s = np.linspace(df["sigma_mix"].min(), df["sigma_mix"].max(), 50)
KK, SS = np.meshgrid(grid_k, grid_s)

for ax, v_val in zip(axes, v_slices):
    grid_points = np.column_stack([
        KK.ravel(), SS.ravel(),
        np.full(KK.size, v_val), np.full(KK.size, t_fixed),
    ])
    _, std = active_gp.predict(active_scaler.transform(grid_points), return_std=True)
    std = std.reshape(KK.shape)
    cf = ax.contourf(KK, SS, std, levels=20, cmap="OrRd")
    ax.set_xlabel("kappa_mix")
    ax.set_ylabel("sigma_mix")
    ax.set_title(f"Uncertainty at V={v_val:.2f} m/s, T0={t_fixed:.0f}K")
    fig2.colorbar(cf, ax=ax, label="std dev (Nd)")

plt.tight_layout()
plt.savefig("active_learning_heatmaps.png", dpi=150)
print("Saved active_learning_heatmaps.png")
plt.show()