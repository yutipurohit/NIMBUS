import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from matplotlib.colors import LinearSegmentedColormap

from compound_database import COMPOUNDS, list_derived_kappa
from mixing_layer import resolve_mixture, predict, load_surrogate

st.set_page_config(page_title="Cloud-Seeding Composition Console", layout="wide")

#Design tokens
INK = "#0B132B"
PANEL = "#111A33"
PAPER = "#EEF1F5"
TEAL = "#2A9D8F"
GOLD = "#E9C46A"
CORAL = "#E76F51"
SLATE = "#5A6478"
LINE = "#2A3557"

DRAMATIC = LinearSegmentedColormap.from_list(
    "dramatic", ["#0B132B", "#1C7293", "#2A9D8F", "#E9C46A", "#E76F51"]
)

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap');

    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}

    .stApp {{ background: {PAPER}; }}

    section[data-testid="stSidebar"] {{
        background: {INK};
        border-right: 1px solid {LINE};
    }}
    section[data-testid="stSidebar"] * {{ color: #DCE1EC !important; }}
    section[data-testid="stSidebar"] label {{
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 11px !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: {SLATE}A0 !important;
    }}

    .console-title {{
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 30px;
        color: {INK};
        letter-spacing: -0.01em;
        margin-bottom: 2px;
    }}
    .console-sub {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 12px;
        color: {SLATE};
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }}

    .gauge {{
        background: {INK};
        border-radius: 4px;
        padding: 18px 22px;
        border-left: 4px solid {TEAL};
    }}
    .gauge-label {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: {SLATE}D0;
        margin-bottom: 6px;
    }}
    .gauge-value {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 30px;
        font-weight: 600;
        color: #F4F6FA;
        line-height: 1;
    }}
    .gauge-unit {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 13px;
        color: {SLATE}D0;
        margin-left: 4px;
    }}

    .status-banner {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 12px;
        padding: 10px 16px;
        border-radius: 4px;
        margin-bottom: 18px;
    }}
    .status-live {{ background: {GOLD}22; border: 1px solid {GOLD}; color: #7A5A00; }}
    .status-surrogate {{ background: {TEAL}22; border: 1px solid {TEAL}; color: #0E5148; }}

    .flag-note {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        color: {CORAL};
        background: {CORAL}15;
        border-left: 3px solid {CORAL};
        padding: 8px 12px;
        margin-top: 10px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

#Header
st.markdown('<div class="console-title">Cloud-Seeding Composition Console</div>', unsafe_allow_html=True)
st.markdown('<div class="console-sub">Kappa-Kohler mixture activation predictor</div>', unsafe_allow_html=True)
st.write("")

gp, scaler = load_surrogate()
if gp is None:
    st.markdown(
        '<div class="status-banner status-live">● LIVE SIMULATION MODE — surrogate model not yet trained. '
        'Every query runs a real pyrcel parcel simulation (slower, but ground truth).</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<div class="status-banner status-surrogate">● SURROGATE MODE — predictions from the trained '
        'Gaussian Process (fast, includes uncertainty). Check "Force live simulation" in the sidebar '
        'for trajectory/radius plots.</div>',
        unsafe_allow_html=True,
    )

#Sidebar controls
st.sidebar.markdown("CONTROL PANEL")
st.sidebar.write("")

compound_keys = sorted(COMPOUNDS.keys())
compound_labels = {k: COMPOUNDS[k]["display_name"] for k in compound_keys}
derived_flagged = set(list_derived_kappa())

compound_a_key = st.sidebar.selectbox(
    "Compound A (background)", compound_keys, format_func=lambda k: compound_labels[k], index=compound_keys.index("ammonium_sulfate") if "ammonium_sulfate" in compound_keys else 0,
)
compound_b_key = st.sidebar.selectbox(
    "Compound B (seeding agent)", compound_keys, format_func=lambda k: compound_labels[k], index=compound_keys.index("ctab") if "ctab" in compound_keys else 0,
)

f_b = st.sidebar.slider("Mixing fraction (compound B)", 0.0, 1.0, 0.3, 0.05)
V = st.sidebar.slider("Updraft speed V (m/s)", 0.1, 5.0, 1.0, 0.1)
T0 = st.sidebar.slider("Temperature T0 (K)", 273.0, 293.0, 283.0, 1.0)

run_button = st.sidebar.button("RUN QUERY", use_container_width=True)
force_live = st.sidebar.checkbox(
    "Force live simulation", value=False,
    help="Runs the real pyrcel simulation even if a trained surrogate is loaded -- "
         "needed to see the trajectory/radius plots, which the surrogate can't produce.",
)

if compound_a_key in derived_flagged or compound_b_key in derived_flagged:
    st.sidebar.markdown(
        '<div class="flag-note">⚠ One or both compounds use a DERIVED (estimated) kappa value, '
        'not a directly measured one. See compound_database.py notes.</div>',
        unsafe_allow_html=True,
    )

#Main panel
if run_button:
    with st.spinner("Running..."):
        mix = resolve_mixture(compound_a_key, compound_b_key, f_b, T0)
        result = predict(mix["kappa_mix"], mix["sigma_mix"], V, T0, force_live=force_live)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f'<div class="gauge"><div class="gauge-label">Activated Droplet Number</div>'
            f'<div class="gauge-value">{result["Nd"]:.3e}<span class="gauge-unit">m⁻³</span></div></div>',
            unsafe_allow_html=True,
        )
    with col2:
        if "S_max" in result:
            st.markdown(
                f'<div class="gauge"><div class="gauge-label">Peak Supersaturation</div>'
                f'<div class="gauge-value">{result["S_max"]*100:.4f}<span class="gauge-unit">%</span></div></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="gauge"><div class="gauge-label">Prediction Uncertainty</div>'
                f'<div class="gauge-value">±{result["Nd_std"]:.2e}<span class="gauge-unit">m⁻³</span></div></div>',
                unsafe_allow_html=True,
            )
    with col3:
        st.markdown(
            f'<div class="gauge"><div class="gauge-label">Mixed Properties</div>'
            f'<div class="gauge-value" style="font-size:16px;">κ={mix["kappa_mix"]:.3f}  σ={mix["sigma_mix"]:.4f}</div></div>',
            unsafe_allow_html=True,
        )

    if mix["any_derived_kappa"]:
        st.markdown(
            '<div class="flag-note">⚠ This prediction uses at least one DERIVED kappa value — treat '
            'with lower confidence than a fully-measured pairing.</div>',
            unsafe_allow_html=True,
        )

    st.write("")

    if result["method"] == "live_simulation":
        out = result["out"]
        model = result["model"]

        plot_col1, plot_col2 = st.columns(2)

        with plot_col1:
            fig, ax = plt.subplots(figsize=(6, 4.5))
            fig.patch.set_facecolor(PAPER)
            ax.set_facecolor(PAPER)
            ax.plot(out.time, out.S * 100, color=TEAL, linewidth=2.2)
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Supersaturation, S (%)")
            ax.set_title("Supersaturation Trajectory", fontsize=12, color=INK)
            ax.grid(alpha=0.25)
            st.pyplot(fig)

        with plot_col2:
            from pyrcel.equilibrate import kohler_crit_approx

            aer = model.aerosols[0]
            T_smax = out.summary["T_smax"]
            S_max = out.summary["S_max"]
            _, s_crits = kohler_crit_approx(T_smax, aer.r_drys, aer.kappa, aer.sigma)
            activated_mask = np.asarray(S_max >= s_crits)
            radii = out.state[:, 7 : 7 + aer.nr]
            heights = out.heights

            fig2, ax2 = plt.subplots(figsize=(6, 4.5))
            fig2.patch.set_facecolor(PAPER)
            ax2.set_facecolor(PAPER)
            for i in range(aer.nr):
                color = TEAL if activated_mask[i] else GOLD
                style = "-" if activated_mask[i] else "--"
                ax2.plot(radii[:, i] * 1e6, heights, color=color, linestyle=style, linewidth=1.1, alpha=0.8)
            ax2.set_xscale("log")
            ax2.set_xlabel("Droplet radius, μm")
            ax2.set_ylabel("Height (m)")
            n_act = int(activated_mask.sum())
            ax2.set_title(f"Radius Profile ({n_act}/{aer.nr} activated)", fontsize=12, color=INK)
            ax2.grid(alpha=0.25, which="both")
            st.pyplot(fig2)

    else:
        st.info("Surrogate mode doesn't run a real simulation, so trajectory/radius plots aren't available here — check 'Force live simulation' in the sidebar to see them for this query.")

    st.write("")
    sweep_label = (
        "Generate composition sweep around this mixture"
        if result["method"] == "surrogate"
        else "Generate composition sweep around this mixture (slow — runs several live simulations)"
    )
    with st.expander(sweep_label):
        if st.button("Run sweep"):
            sweep_f_b = np.linspace(0.0, 1.0, 7)
            sweep_nd = []
            sweep_nd_std = []
            progress = st.progress(0)
            for i, fb in enumerate(sweep_f_b):
                m = resolve_mixture(compound_a_key, compound_b_key, fb, T0)
                r = predict(m["kappa_mix"], m["sigma_mix"], V, T0, force_live=force_live)
                sweep_nd.append(r["Nd"])
                sweep_nd_std.append(r.get("Nd_std", 0.0))
                progress.progress((i + 1) / len(sweep_f_b))

            sweep_nd = np.array(sweep_nd)
            sweep_nd_std = np.array(sweep_nd_std)

            fig3, ax3 = plt.subplots(figsize=(9, 4.5))
            fig3.patch.set_facecolor(PAPER)
            ax3.set_facecolor(PAPER)
            if sweep_nd_std.any():
                ax3.fill_between(sweep_f_b, sweep_nd - sweep_nd_std, sweep_nd + sweep_nd_std,
                                  color=CORAL, alpha=0.15, label="±1 std (surrogate uncertainty)")
            ax3.plot(sweep_f_b, sweep_nd, "o-", color=CORAL, linewidth=2)
            ax3.axvline(f_b, color=INK, linestyle=":", alpha=0.5, label="current selection")
            ax3.set_xlabel(f"Mixing fraction of {compound_labels[compound_b_key]}")
            ax3.set_ylabel("Activated droplet number, Nd (m⁻³)")
            ax3.set_title("Composition Sweep", fontsize=12, color=INK)
            ax3.legend(frameon=False)
            ax3.grid(alpha=0.25)
            st.pyplot(fig3)
else:
    st.markdown(
        f'<p style="font-family:IBM Plex Mono, monospace; color:{SLATE}; font-size:13px;">'
        "Set compounds and conditions in the control panel, then RUN QUERY.</p>",
        unsafe_allow_html=True,
    )