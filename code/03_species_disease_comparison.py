"""
03_species_disease_comparison.py
===================================
Reproduces:
  - Table 3 (FMD occurrence, production losses, and economic losses by
    livestock species; manuscript Section 3.2)
  - The Kruskal-Wallis test and pairwise Bonferroni-corrected Mann-Whitney
    U tests reported in Section 3.3
  - Figure 2 (per-affected-animal economic loss by species, log scale)

Per-farm, per-species economic loss (manuscript Eq. in Section 2.4):
  L = (milk revenue baseline - milk revenue observed)
    + (meat revenue baseline - meat revenue observed)
    + additional treatment cost
Per-affected-animal loss = L / number of affected animals.

Produces:
  output/Table3_species_disease_comparison.csv
  output/species_loss_per_animal_long.csv   (long-format per-farm data
                                              underlying Table 3/Fig.2)
  output/kruskal_wallis_and_pairwise_tests.csv
  figures/Figure2_species_loss_boxplot.png
"""
import itertools
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib as mpl

from _paths import FARM_LEVEL_CSV, OUTPUT_DIR, FIG_DIR, FIGURE_DPI, TRY_PER_USD, SPECIES

mpl.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 12,
    "axes.spines.top": False, "axes.spines.right": False,
})


def per_animal_loss_long(df):
    """Builds a long-format dataframe: one row per (farm, species) with
    hastalanan > 0, containing per-affected-animal economic loss and the
    other per-species variables needed for Table 3 and later scripts."""
    records = []
    for sp in SPECIES:
        sub = df[df[f"{sp}_hastalanan"] > 0].copy()
        milk_loss = sub[f"{sp}_sut_geliri"] - sub[f"{sp}_hasta_sut_geliri"]
        meat_loss = sub[f"{sp}_et_geliri"] - sub[f"{sp}_hasta_et_geliri"]
        total_loss = milk_loss + meat_loss + sub[f"{sp}_ilave_masraf"]
        per_animal = total_loss / sub[f"{sp}_hastalanan"]
        for farm_id, tabaka, hastalanan, sure, sayi, loss, pa in zip(
            sub["farm_id"], sub["tabaka"], sub[f"{sp}_hastalanan"], sub[f"{sp}_hastalik_suresi_gun"],
            sub[f"{sp}_sayi"], total_loss, per_animal
        ):
            if pa > 0:  # matches manuscript's convention of positive realized losses
                records.append({
                    "farm_id": farm_id, "species": sp, "tabaka": tabaka, "herd_size": sayi,
                    "hastalanan": hastalanan, "prevalence": hastalanan / sayi if sayi else np.nan,
                    "illness_duration_days": sure, "total_loss_try": loss,
                    "per_animal_loss_try": pa, "per_animal_loss_usd": pa / TRY_PER_USD,
                })
    return pd.DataFrame(records)


def main():
    df = pd.read_csv(FARM_LEVEL_CSV)
    long_df = per_animal_loss_long(df)
    long_df.to_csv(OUTPUT_DIR / "species_loss_per_animal_long.csv", index=False)

    # ---- Table 3 ----
    rows = []
    for sp, label in SPECIES.items():
        n_holding = int((df[f"{sp}_sayi"] > 0).sum())
        n_disease = int((df[f"{sp}_hastalanan"] > 0).sum())
        prevalence = 100 * n_disease / n_holding
        sub_disease = df[df[f"{sp}_hastalanan"] > 0]
        # A recorded illness duration of 0 days on a farm that reports
        # affected animals is implausible and is treated as a missing
        # response (not a true zero-day illness) rather than a valid
        # observation -- this affects water buffalo in particular (39 of
        # 85 affected farms). The mean is then weighted by the number of
        # affected animals per farm. See docs/DATA_DESCRIPTION.md.
        dur_nonmissing = sub_disease[sub_disease[f"{sp}_hastalik_suresi_gun"] > 0]
        mean_duration = dur_nonmissing[f"{sp}_hastalik_suresi_gun"].mean()

        # Yield-loss percentages are derived exactly as in the manuscript's
        # disease-loss model: (baseline - observed) / baseline, averaged
        # across affected farms for that species.
        milk_base = sub_disease[f"{sp}_sut_geliri"]
        milk_obs = sub_disease[f"{sp}_hasta_sut_geliri"]
        with np.errstate(divide="ignore", invalid="ignore"):
            milk_loss_pct = np.where(milk_base > 0, 100 * (milk_base - milk_obs) / milk_base, np.nan)
        # Sheep: no farm reports a nonzero milk-revenue baseline (flocks
        # are predominantly meat-oriented and not routinely milked), so
        # this is reported as 0.00% rather than undefined -- see
        # manuscript Table 3, footnote (a).
        mean_milk_loss_pct = np.nanmean(milk_loss_pct) if np.any(~np.isnan(milk_loss_pct)) else 0.0

        meat_base = sub_disease[f"{sp}_et_geliri"]
        meat_obs = sub_disease[f"{sp}_hasta_et_geliri"]
        with np.errstate(divide="ignore", invalid="ignore"):
            weight_loss_pct = np.where(meat_base > 0, 100 * (meat_base - meat_obs) / meat_base, np.nan)
        mean_weight_loss_pct = np.nanmean(weight_loss_pct)

        sp_long = long_df[long_df["species"] == sp]
        rows.append({
            "species": label,
            "farms_holding_species": n_holding,
            "farms_reporting_disease": n_disease,
            "prevalence_pct": round(prevalence, 1),
            "mean_illness_duration_days": round(mean_duration, 1),
            "mean_milk_yield_loss_pct": round(mean_milk_loss_pct, 2),
            "mean_weight_loss_pct": round(mean_weight_loss_pct, 2),
            "mean_loss_per_affected_animal_try": round(sp_long["per_animal_loss_try"].mean()),
            "mean_loss_per_affected_animal_usd": round(sp_long["per_animal_loss_usd"].mean()),
        })
    table3 = pd.DataFrame(rows)
    table3.to_csv(OUTPUT_DIR / "Table3_species_disease_comparison.csv", index=False)
    print("Table 3. FMD occurrence, production losses, and economic losses by species")
    print(table3.to_string(index=False))

    # ---- Kruskal-Wallis + pairwise Mann-Whitney (Section 3.3) ----
    groups = {sp: long_df.loc[long_df["species"] == sp, "per_animal_loss_try"].values for sp in SPECIES}
    h_stat, p_kw = stats.kruskal(*groups.values())
    print(f"\nKruskal-Wallis: H = {h_stat:.2f}, p = {p_kw:.3e}")

    pair_rows = [{"test": "Kruskal-Wallis (all species)", "comparison": "-", "statistic": round(h_stat, 2), "p_value": p_kw}]
    n_pairs = len(list(itertools.combinations(SPECIES, 2)))
    bonferroni_alpha = 0.05 / n_pairs
    for sp_a, sp_b in itertools.combinations(SPECIES, 2):
        u_stat, p_mw = stats.mannwhitneyu(groups[sp_a], groups[sp_b], alternative="two-sided")
        pair_rows.append({
            "test": "Mann-Whitney U (Bonferroni-corrected)",
            "comparison": f"{SPECIES[sp_a]} vs {SPECIES[sp_b]}",
            "statistic": round(u_stat, 1),
            "p_value": p_mw,
        })
    pair_df = pd.DataFrame(pair_rows)
    pair_df["bonferroni_alpha"] = bonferroni_alpha
    pair_df["significant_after_correction"] = pair_df["p_value"] < bonferroni_alpha
    pair_df.to_csv(OUTPUT_DIR / "kruskal_wallis_and_pairwise_tests.csv", index=False)
    print(f"\nPairwise Mann-Whitney U tests (Bonferroni alpha = {bonferroni_alpha:.4f}):")
    print(pair_df.to_string(index=False))

    # ---- Figure 2 ----
    order = list(SPECIES.keys())
    labels = ["Cattle", "Water\nbuffalo", "Sheep", "Goat"]
    colors = ["#4C72B0", "#C44E52", "#55A868", "#DD8452"]
    data = [groups[sp] for sp in order]

    fig, ax = plt.subplots(figsize=(7, 5))
    bp = ax.boxplot(data, tick_labels=labels, patch_artist=True, showfliers=True,
                     flierprops=dict(marker="o", markersize=3, alpha=0.4, markerfacecolor="gray", markeredgecolor="none"),
                     medianprops=dict(color="black", linewidth=1.5))
    for patch, c in zip(bp["boxes"], colors):
        patch.set_facecolor(c)
        patch.set_alpha(0.75)
    ax.set_yscale("log")
    ax.set_ylabel("Economic loss per affected animal (TRY, log scale)")
    ax.set_title("Figure 2. FMD-attributable economic loss per affected animal by species", fontsize=11, loc="left")
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "Figure2_species_loss_boxplot.png", dpi=FIGURE_DPI)
    plt.close()
    print("\nSaved figures/Figure2_species_loss_boxplot.png")


if __name__ == "__main__":
    main()
