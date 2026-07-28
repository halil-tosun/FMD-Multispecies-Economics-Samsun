"""
06_mortality_analysis.py
===========================
Reproduces the cattle age-sex-class mortality analysis (manuscript
Section 3.6), Table 5, and Figure 7.

Steps (matching the manuscript exactly):
  1. Verify internal consistency between reported FMD occurrence
     (cattle_hastalanan) and recorded mortality across the six age-sex
     classes (farms reporting no disease are expected to show zero
     disease-attributable deaths).
  2. Restrict the mortality-rate comparison to farms reporting FMD
     occurrence (N=122).
  3. Chi-square test of homogeneity across the six age-sex classes,
     followed by pairwise two-proportion z-tests.

Produces:
  output/mortality_consistency_check.csv
  output/Table5_mortality_by_ageclass.csv
  output/mortality_statistical_tests.csv
  figures/Figure7_mortality_by_ageclass.png
"""
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import Patch

from _paths import FARM_LEVEL_CSV, OUTPUT_DIR, FIG_DIR, FIGURE_DPI, CATTLE_AGE_CLASSES

mpl.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 12,
    "axes.spines.top": False, "axes.spines.right": False,
})

# Classes grouped as in the manuscript's Discussion (Section 4.1): calves
# and breeding/production stock (bulls, cows) vs. growing/finishing stock
HIGH_RISK_GROUP = {"buzagi", "boga", "inek"}


def two_prop_ztest(d1, n1, d2, n2):
    p1, p2 = d1 / n1, d2 / n2
    p_pool = (d1 + d2) / (n1 + n2)
    se = np.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
    z = (p1 - p2) / se
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    return p1, p2, z, p


def main():
    df = pd.read_csv(FARM_LEVEL_CSV)

    # ---- Consistency check ----
    cattle_farms = df[df["sigir_sayi"] > 0].copy()
    olen_cols = [f"cattle_{ac}_olen" for ac in CATTLE_AGE_CLASSES]
    cattle_farms["total_died"] = cattle_farms[olen_cols].sum(axis=1)

    no_disease = cattle_farms[cattle_farms["sigir_hastalanan"] == 0]
    n_no_disease = len(no_disease)
    n_zero_deaths = (no_disease["total_died"] == 0).sum()
    n_inconsistent = n_no_disease - n_zero_deaths

    consistency = pd.DataFrame([{
        "n_cattle_holding_farms": len(cattle_farms),
        "n_no_disease_reported": n_no_disease,
        "n_zero_deaths_among_no_disease": n_zero_deaths,
        "n_inconsistent_deaths_without_disease": n_inconsistent,
        "pct_consistent": round(100 * n_zero_deaths / n_no_disease, 1),
    }])
    consistency.to_csv(OUTPUT_DIR / "mortality_consistency_check.csv", index=False)
    print("Mortality data consistency check")
    print(consistency.to_string(index=False))

    # ---- Table 5: mortality rate by age-sex class, FMD-affected farms only ----
    affected = cattle_farms[cattle_farms["sigir_hastalanan"] > 0]
    rows = []
    exposure = {}
    deaths = {}
    for ac, label in CATTLE_AGE_CLASSES.items():
        died = affected[f"cattle_{ac}_olen"].sum()
        exposed = (affected[f"cattle_{ac}_sene_sonu"] + affected[f"cattle_{ac}_satilan"]
                   + affected[f"cattle_{ac}_olen"] + affected[f"cattle_{ac}_evde_kesilen"]).sum()
        rate = 100 * died / exposed if exposed else np.nan
        rows.append({"class": label, "mortality_rate_pct": round(rate, 2)})
        exposure[ac] = exposed
        deaths[ac] = died

    table5 = pd.DataFrame(rows).sort_values("mortality_rate_pct", ascending=False).reset_index(drop=True)
    table5.to_csv(OUTPUT_DIR / "Table5_mortality_by_ageclass.csv", index=False)
    print(f"\nTable 5. FMD-associated mortality by cattle age-sex class (N={len(affected)} affected farms)")
    print(table5.to_string(index=False))

    # ---- Statistical tests ----
    died_arr = np.array([deaths[ac] for ac in CATTLE_AGE_CLASSES])
    exposed_arr = np.array([exposure[ac] for ac in CATTLE_AGE_CLASSES])
    survived_arr = exposed_arr - died_arr
    chi2, p_chi2, dof, _ = stats.chi2_contingency(np.array([died_arr, survived_arr]))

    test_rows = [{"test": "Chi-square (6 age-sex classes, homogeneity)", "comparison": "-",
                  "statistic": round(chi2, 2), "df": dof, "p_value": p_chi2}]

    # Calf vs combined heifer+yearling+steer
    young_classes = [c for c in CATTLE_AGE_CLASSES if c not in HIGH_RISK_GROUP]
    d_young = sum(deaths[c] for c in young_classes)
    n_young = sum(exposure[c] for c in young_classes)
    p1, p2, z, p = two_prop_ztest(deaths["buzagi"], exposure["buzagi"], d_young, n_young)
    test_rows.append({"test": "Two-proportion z-test", "comparison": "Calves vs Heifers+Yearlings+Steers (combined)",
                       "statistic": round(z, 2), "df": np.nan, "p_value": p})

    for other in ["inek", "boga"]:
        p1, p2, z, p = two_prop_ztest(deaths["buzagi"], exposure["buzagi"], deaths[other], exposure[other])
        test_rows.append({"test": "Two-proportion z-test",
                           "comparison": f"Calves vs {CATTLE_AGE_CLASSES[other]}",
                           "statistic": round(z, 2), "df": np.nan, "p_value": p})

    test_df = pd.DataFrame(test_rows)
    test_df.to_csv(OUTPUT_DIR / "mortality_statistical_tests.csv", index=False)
    print("\nStatistical tests")
    print(test_df.to_string(index=False))

    # ---- Figure 7 ----
    order = ["boga", "buzagi", "inek", "duve", "dana", "tosun"]
    labels = [CATTLE_AGE_CLASSES[o] for o in order]
    rates = [100 * deaths[o] / exposure[o] for o in order]
    colors = ["#C44E52" if o in HIGH_RISK_GROUP else "#4C72B0" for o in order]

    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(labels, rates, color=colors, alpha=0.85, edgecolor="white")
    for b, r in zip(bars, rates):
        ax.text(b.get_x() + b.get_width() / 2, r + 0.05, f"{r:.2f}%", ha="center", fontsize=10)
    ax.set_ylabel("FMD-associated mortality rate (%)")
    ax.set_title("Figure 7. Mortality by cattle age-sex class", fontsize=13, loc="left")
    ax.set_ylim(0, max(rates) * 1.2)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    legend_elems = [Patch(facecolor="#C44E52", label="Calves & breeding/production stock"),
                    Patch(facecolor="#4C72B0", label="Growing/finishing stock")]
    ax.legend(handles=legend_elems, frameon=False, loc="upper right")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "Figure7_mortality_by_ageclass.png", dpi=FIGURE_DPI)
    plt.close()
    print("\nSaved figures/Figure7_mortality_by_ageclass.png")


if __name__ == "__main__":
    main()
