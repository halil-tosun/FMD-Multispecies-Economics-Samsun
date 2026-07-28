"""
08_benchmark_table.py
========================
Reproduces Table 7 (manuscript Section 3.8): comparison of the present
study's per-unit FMD economic-loss estimates with selected previously
published farm/household-level estimates from other endemic settings.

The four "present study" rows are computed from
output/Table3_species_disease_comparison.csv (produced by script 03).
The remaining rows are fixed values drawn directly from the cited
published sources (they are not derived from this study's data) and are
hard-coded here with their full citations; see docs/DATA_DESCRIPTION.md
and the manuscript's reference list for the original sources.

Produces:
  output/Table7_benchmark_comparison.csv
"""
import pandas as pd
from _paths import OUTPUT_DIR


def main():
    table3 = pd.read_csv(OUTPUT_DIR / "Table3_species_disease_comparison.csv")

    rows = []
    for _, r in table3.iterrows():
        rows.append({
            "study_context": f"Present study - {r['species'].lower()} (Samsun, Turkiye)",
            "unit": "per affected animal",
            "estimated_loss_usd": r["mean_loss_per_affected_animal_usd"],
            "source": "This study (script 03)",
        })

    # Fixed values from cited published literature (not derived from this
    # study's dataset) -- see manuscript References and
    # docs/DATA_DESCRIPTION.md for full citations.
    rows += [
        {"study_context": "Uganda (mixed smallholder herds)", "unit": "per affected household",
         "estimated_loss_usd": 323, "source": "Ekou and Edwetu (2026)"},
        {"study_context": "Ethiopia - mixed crop-livestock system", "unit": "per affected herd",
         "estimated_loss_usd": 34, "source": "Tadesse et al. (2020)"},
        {"study_context": "Ethiopia - commercial dairy system", "unit": "per affected farm",
         "estimated_loss_usd": 459, "source": "Tadesse et al. (2020)"},
        {"study_context": "Global, endemic regions (aggregate)", "unit": "annual, regional/global",
         "estimated_loss_usd": "6.5-21 billion", "source": "Knight-Jones and Rushton (2013)"},
    ]

    table7 = pd.DataFrame(rows)
    table7.to_csv(OUTPUT_DIR / "Table7_benchmark_comparison.csv", index=False)
    print("Table 7. Comparison with published farm-level FMD economic-loss estimates")
    print(table7.to_string(index=False))
    print("\nNote: units of analysis differ across studies (per animal, household, herd, or")
    print("farm); comparison is descriptive, not a direct quantitative equivalence")
    print("(manuscript Section 3.8).")


if __name__ == "__main__":
    main()
