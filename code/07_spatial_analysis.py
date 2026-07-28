"""
07_spatial_analysis.py
=========================
Reproduces the spatial autocorrelation analysis of within-herd FMD
prevalence (manuscript Section 3.7), Table 6, Figure 8 (prevalence map),
and Figure 9 (Moran scatterplot).

Village-level coordinates (data/raw/village_coordinates.csv) were
obtained by bulk geocoding via the Geoapify/OpenStreetMap Nominatim
service (see docs/DATA_DESCRIPTION.md for the full geocoding procedure
and the two low-confidence "Merkez" villages approximated at the
Tekkekoy district-center coordinate).

No pre-built Python package at the time of writing simultaneously
supported k-nearest-neighbor Moran's I with haversine distance and the
exact permutation-inference specification used here, so it is
implemented directly in NumPy (manuscript Sections 2.6/2.7).

Produces:
  output/Table6_moran_i_by_k.csv
  figures/Figure8_prevalence_map.png
  figures/Figure9_moran_scatterplot.png
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

from _paths import FARM_LEVEL_CSV, OUTPUT_DIR, FIG_DIR, FIGURE_DPI, SPECIES

mpl.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 12,
    "axes.spines.top": False, "axes.spines.right": False,
})

SEED = 42
N_PERMUTATIONS = 999
K_VALUES = [4, 6, 8, 10, 15]
K_FOR_FIGURES = 6


def haversine_distance_matrix(lat, lon):
    lat, lon = np.radians(lat), np.radians(lon)
    n = len(lat)
    R = 6371.0
    dlat = lat[:, None] - lat[None, :]
    dlon = lon[:, None] - lon[None, :]
    a = np.sin(dlat / 2) ** 2 + np.cos(lat[:, None]) * np.cos(lat[None, :]) * np.sin(dlon / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def knn_weights(dist, k):
    n = dist.shape[0]
    W = np.zeros((n, n))
    for i in range(n):
        order = np.argsort(dist[i])
        order = order[order != i][:k]
        W[i, order] = 1.0
    return W


def morans_i(x, W, seed=SEED, n_perm=N_PERMUTATIONS):
    n = len(x)
    xbar = x.mean()
    z = x - xbar
    Wsum = W.sum()
    I = (n / Wsum) * np.sum(W * np.outer(z, z)) / np.sum(z ** 2)

    rng = np.random.RandomState(seed)
    perm_Is = np.empty(n_perm)
    for i in range(n_perm):
        zp = rng.permutation(x) - x.mean()
        perm_Is[i] = (n / Wsum) * np.sum(W * np.outer(zp, zp)) / np.sum(zp ** 2)
    p_value = (np.sum(perm_Is >= I) + 1) / (n_perm + 1)
    return I, p_value


def main():
    df = pd.read_csv(FARM_LEVEL_CSV)
    total_animals = sum(df[f"{sp}_sayi"].fillna(0) for sp in SPECIES)
    total_sick = sum(df[f"{sp}_hastalanan"].fillna(0) for sp in SPECIES)
    df["herd_prevalence"] = total_sick / total_animals
    df = df[total_animals > 0].dropna(subset=["village_lat", "village_lon"]).copy()
    print(f"N farms with valid coordinates and herd data: {len(df)}")

    dist = haversine_distance_matrix(df["village_lat"].values, df["village_lon"].values)
    x = df["herd_prevalence"].values

    rows = []
    for k in K_VALUES:
        W = knn_weights(dist, k)
        I, p = morans_i(x, W)
        rows.append({"k": k, "morans_i": round(I, 4), "p_value": round(p, 3)})
    table6 = pd.DataFrame(rows)
    table6.to_csv(OUTPUT_DIR / "Table6_moran_i_by_k.csv", index=False)
    print("\nTable 6. Moran's I for within-herd FMD prevalence across k-nearest-neighbor specifications")
    print(table6.to_string(index=False))

    # ---- Figure 8: prevalence map ----
    fig, ax = plt.subplots(figsize=(8, 6.5))
    sc = ax.scatter(df["village_lon"], df["village_lat"], c=df["herd_prevalence"] * 100, cmap="YlOrRd",
                     s=55, edgecolor="gray", linewidth=0.4, alpha=0.9, vmin=0, vmax=df["herd_prevalence"].max() * 100)
    cbar = plt.colorbar(sc, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Within-herd prevalence (%)")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Figure 8. Village-level FMD prevalence by location", fontsize=13, loc="left")
    ax.set_aspect("equal", adjustable="datalim")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "Figure8_prevalence_map.png", dpi=FIGURE_DPI)
    plt.close()

    # ---- Figure 9: Moran scatterplot (k=6, matching manuscript figure) ----
    W6 = knn_weights(dist, K_FOR_FIGURES)
    W6_row = W6 / W6.sum(axis=1, keepdims=True)
    z = (x - x.mean()) / x.std()
    lag = W6_row @ z
    I6, p6 = morans_i(x, W6)

    fig2, ax2 = plt.subplots(figsize=(8, 6.5))
    ax2.scatter(z, lag, alpha=0.5, color="#4C72B0", s=35, edgecolor="white", linewidth=0.3)
    slope = np.polyfit(z, lag, 1)[0]
    xs = np.linspace(z.min(), z.max(), 100)
    ax2.plot(xs, slope * xs, color="#C44E52", linewidth=2.2,
             label=f"Moran's I (k={K_FOR_FIGURES}) = {I6:.3f}, p = {p6:.3f}")
    ax2.axhline(0, color="gray", linewidth=0.7)
    ax2.axvline(0, color="gray", linewidth=0.7)
    ax2.set_xlabel("Standardized within-herd prevalence (z)")
    ax2.set_ylabel("Spatial lag (neighbor average, z)")
    ax2.set_title("Figure 9. Moran scatterplot of FMD prevalence", fontsize=13, loc="left")
    ax2.legend(frameon=False, loc="upper left", fontsize=11)
    ax2.grid(alpha=0.3, linestyle="--")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "Figure9_moran_scatterplot.png", dpi=FIGURE_DPI)
    plt.close()
    print("\nSaved figures/Figure8_prevalence_map.png, Figure9_moran_scatterplot.png")


if __name__ == "__main__":
    main()
