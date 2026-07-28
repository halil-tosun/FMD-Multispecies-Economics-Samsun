"""
04_regression_analysis.py
============================
Reproduces Table 4 and Figures 3-5 (manuscript Section 3.4): the
multiple regression of log-transformed per-affected-animal economic
loss on species, herd size, illness duration, within-herd prevalence,
and production stratum, with farm-level cluster-robust (CR1) standard
errors, VIF diagnostics, and the 2.5%-trimmed robustness check.

No pre-built Python package at the time of writing simultaneously
supported farm-level clustered SEs with this exact specification, so
the CR1 sandwich estimator is implemented directly here in NumPy
(manuscript Section 2.7 / Section 2.5).

Produces:
  output/Table4_regression.csv
  output/regression_robustness_trimmed.csv
  output/vif_diagnostics.csv
  figures/Figure3_species_effects.png
  figures/Figure4_herd_covariates.png
  figures/Figure5_prevalence_effect.png
"""
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib as mpl

from _paths import OUTPUT_DIR, FIG_DIR, FIGURE_DPI, SPECIES

mpl.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 12,
    "axes.spines.top": False, "axes.spines.right": False,
})

REFERENCE_SPECIES = "sigir"  # cattle is the reference category


def build_design_matrix(long_df):
    """Builds the regression design matrix exactly as specified in the
    manuscript: log(per-animal loss) ~ species + herd_size + duration +
    prevalence + stratum (categorical, ref = stratum 1)."""
    df = long_df.copy()
    df["log_loss"] = np.log(df["per_animal_loss_try"])

    species_dummies = pd.get_dummies(df["species"], prefix="sp", drop_first=False).astype(float)
    species_dummies = species_dummies.drop(columns=[f"sp_{REFERENCE_SPECIES}"])

    tabaka_dummies = pd.get_dummies(df["tabaka"].astype(int), prefix="stratum", drop_first=True).astype(float)

    X = pd.concat([
        pd.Series(1.0, index=df.index, name="const"),
        species_dummies,
        df[["herd_size", "illness_duration_days", "prevalence"]].rename(
            columns={"herd_size": "herd_size", "illness_duration_days": "illness_duration", "prevalence": "prevalence"}),
        tabaka_dummies,
    ], axis=1)
    return X, df["log_loss"].values, df["farm_id"].values


def cluster_robust_ols(X, y, cluster_id):
    """OLS with CR1 cluster-robust standard errors (small-sample corrected)."""
    Xm = X.values.astype(float)
    n, k = Xm.shape
    XtX_inv = np.linalg.pinv(Xm.T @ Xm)
    beta = XtX_inv @ Xm.T @ y
    resid = y - Xm @ beta

    clusters = np.unique(cluster_id)
    G = len(clusters)
    meat = np.zeros((k, k))
    for c in clusters:
        idx = np.where(cluster_id == c)[0]
        Xg, ug = Xm[idx], resid[idx]
        score = Xg.T @ ug
        meat += np.outer(score, score)

    c_factor = (G / (G - 1)) * ((n - 1) / (n - k))
    V = c_factor * XtX_inv @ meat @ XtX_inv
    se = np.sqrt(np.diag(V))
    t_stat = beta / se
    p_val = 2 * (1 - stats.t.cdf(np.abs(t_stat), df=G - 1))
    r2 = 1 - np.sum(resid ** 2) / np.sum((y - y.mean()) ** 2)
    return beta, se, t_stat, p_val, r2, n, G


def compute_vif(X):
    vifs = {}
    cols = [c for c in X.columns if c != "const"]
    for col in cols:
        y_ = X[col].values
        Xo = X.drop(columns=[col, "const"]).values
        Xo1 = np.column_stack([np.ones(len(Xo)), Xo])
        beta, *_ = np.linalg.lstsq(Xo1, y_, rcond=None)
        pred = Xo1 @ beta
        ss_res = np.sum((y_ - pred) ** 2)
        ss_tot = np.sum((y_ - y_.mean()) ** 2)
        r2 = 1 - ss_res / ss_tot
        vifs[col] = 1 / (1 - r2) if r2 < 0.9999 else np.inf
    return vifs


def main():
    long_df = pd.read_csv(OUTPUT_DIR / "species_loss_per_animal_long.csv")
    X, y, farm_id = build_design_matrix(long_df)

    beta, se, t_stat, p_val, r2, n, n_clusters = cluster_robust_ols(X, y, farm_id)

    label_map = {
        "const": "Intercept",
        f"sp_manda": "Water buffalo (ref.: cattle)",
        f"sp_koyun": "Sheep",
        f"sp_keci": "Goat",
        "herd_size": "Herd size",
        "illness_duration": "Illness duration",
        "prevalence": "Within-herd prevalence",
        "stratum_2": "Stratum 2 (ref.: Stratum 1)",
        "stratum_3": "Stratum 3 (ref.: Stratum 1)",
    }
    table4 = pd.DataFrame({
        "variable": [label_map.get(c, c) for c in X.columns],
        "coefficient": np.round(beta, 4),
        "cluster_robust_se": np.round(se, 4),
        "p_value": p_val,
    })
    table4.to_csv(OUTPUT_DIR / "Table4_regression.csv", index=False)
    print(f"Table 4. Determinants of log per-animal economic loss (R2={r2:.3f}, N={n}, clusters={n_clusters})")
    print(table4.to_string(index=False))

    # ---- VIF ----
    vif = compute_vif(X)
    vif_df = pd.DataFrame({"variable": list(vif.keys()), "vif": [round(v, 2) for v in vif.values()]})
    vif_df.to_csv(OUTPUT_DIR / "vif_diagnostics.csv", index=False)
    print("\nVariance inflation factors:")
    print(vif_df.to_string(index=False))

    # ---- Robustness: trim top/bottom 2.5% of per-animal loss within each species ----
    lo = long_df.groupby("species")["per_animal_loss_try"].transform(lambda s: s.quantile(0.025))
    hi = long_df.groupby("species")["per_animal_loss_try"].transform(lambda s: s.quantile(0.975))
    trimmed = long_df[(long_df["per_animal_loss_try"] >= lo) & (long_df["per_animal_loss_try"] <= hi)].copy()
    X_t, y_t, farm_id_t = build_design_matrix(trimmed)
    beta_t, se_t, t_t, p_t, r2_t, n_t, g_t = cluster_robust_ols(X_t, y_t, farm_id_t)
    trim_df = pd.DataFrame({
        "variable": [label_map.get(c, c) for c in X_t.columns],
        "coefficient": np.round(beta_t, 4),
        "cluster_robust_se": np.round(se_t, 4),
        "p_value": p_t,
    })
    trim_df.to_csv(OUTPUT_DIR / "regression_robustness_trimmed.csv", index=False)
    print(f"\nRobustness check (2.5% trimmed, N={n_t}, R2={r2_t:.3f}):")
    print(trim_df.to_string(index=False))

    # ---- Figures 3-5 ----
    coefs = dict(zip(X.columns, beta))
    ses = dict(zip(X.columns, se))

    # Figure 3: species effects
    fig, ax = plt.subplots(figsize=(8, 6))
    sp_vars = ["sp_manda", "sp_koyun", "sp_keci"]
    sp_labels = ["Water buffalo\n(ref: cattle)", "Sheep", "Goat"]
    colors = ["#C44E52", "#55A868", "#DD8452"]
    y_pos = np.arange(len(sp_vars))[::-1]
    for v, yp, c in zip(sp_vars, y_pos, colors):
        ci = 1.96 * ses[v]
        ax.errorbar(coefs[v], yp, xerr=ci, fmt="o", color=c, capsize=5, markersize=10, elinewidth=2.5)
    ax.axvline(0, color="gray", linestyle="--", linewidth=1)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(sp_labels)
    ax.set_xlabel("Coefficient (log per-animal loss)")
    ax.set_title("Figure 3. Species effects on log per-animal economic loss", fontsize=13, loc="left")
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "Figure3_species_effects.png", dpi=FIGURE_DPI)
    plt.close()

    # Figure 4: herd/farm covariates (herd size and duration rescaled for display only)
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    disp_vars = ["herd_size", "illness_duration", "stratum_2", "stratum_3"]
    disp_scale = {"herd_size": 100, "illness_duration": 10, "stratum_2": 1, "stratum_3": 1}
    disp_labels = ["Herd size\n(x100)", "Illness duration\n(x10)", "Stratum 2", "Stratum 3"]
    y_pos2 = np.arange(len(disp_vars))[::-1]
    for v, yp, lab in zip(disp_vars, y_pos2, disp_labels):
        c_disp = coefs[v] * disp_scale[v]
        se_disp = ses[v] * disp_scale[v]
        sig = p_val[list(X.columns).index(v)] < 0.05
        color = "#4C72B0" if sig else "#AAAAAA"
        ax2.errorbar(c_disp, yp, xerr=1.96 * se_disp, fmt="o", color=color, capsize=5, markersize=10, elinewidth=2.5)
    ax2.axvline(0, color="gray", linestyle="--", linewidth=1)
    ax2.set_yticks(y_pos2)
    ax2.set_yticklabels(disp_labels)
    ax2.set_xlabel("Coefficient (rescaled; grey = n.s.)")
    ax2.set_title("Figure 4. Herd- and farm-level covariate effects", fontsize=13, loc="left")
    ax2.grid(axis="x", linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "Figure4_herd_covariates.png", dpi=FIGURE_DPI)
    plt.close()

    # Figure 5: prevalence effect
    fig3, ax3 = plt.subplots(figsize=(8, 4.5))
    ax3.errorbar(coefs["prevalence"], 0, xerr=1.96 * ses["prevalence"], fmt="o", color="#4C72B0",
                 capsize=5, markersize=10, elinewidth=2.5)
    ax3.axvline(0, color="gray", linestyle="--", linewidth=1)
    ax3.set_yticks([0])
    ax3.set_yticklabels(["Within-herd\nprevalence"])
    ax3.set_xlabel("Coefficient (log per-animal loss)")
    ax3.set_title("Figure 5. Within-herd prevalence effect", fontsize=13, loc="left")
    ax3.grid(axis="x", linestyle="--", alpha=0.3)
    ax3.set_ylim(-1, 1)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "Figure5_prevalence_effect.png", dpi=FIGURE_DPI)
    plt.close()
    print("\nSaved figures/Figure3_species_effects.png, Figure4_herd_covariates.png, Figure5_prevalence_effect.png")


if __name__ == "__main__":
    main()
