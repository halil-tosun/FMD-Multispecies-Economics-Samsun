"""
01_sample_overview.py
======================
Loads the farm-level dataset, reports the realized sample size (N=286),
and reproduces Table 1 (distribution of surveyed farms by sampling
stratum; manuscript Section 2.2).

Strata are defined by total livestock holdings (all species combined):
  Stratum 1:  20-49 head
  Stratum 2:  50-384 head
  Stratum 3:  >=385 head

Produces:
  output/Table1_stratum_distribution.csv
"""
import pandas as pd
from _paths import FARM_LEVEL_CSV, OUTPUT_DIR, SPECIES


def main():
    df = pd.read_csv(FARM_LEVEL_CSV)
    print(f"Total valid farms in dataset: {len(df)}")
    assert len(df) == 286, "Expected 286 valid farms; check data/processed/farm_level_data.csv"

    stratum_labels = {1: "20-49", 2: "50-384", 3: ">=385"}
    counts = df["tabaka"].value_counts().sort_index()

    rows = []
    for stratum, label in stratum_labels.items():
        rows.append({
            "stratum": stratum,
            "animal_holding_range": label,
            "sample_n": int(counts.get(stratum, 0)),
        })
    table1 = pd.DataFrame(rows)
    total_row = pd.DataFrame([{"stratum": "Total", "animal_holding_range": "", "sample_n": table1["sample_n"].sum()}])
    table1_out = pd.concat([table1, total_row], ignore_index=True)
    table1_out.to_csv(OUTPUT_DIR / "Table1_stratum_distribution.csv", index=False)

    print("\nTable 1. Distribution of surveyed farms by sampling stratum")
    print(table1_out.to_string(index=False))

    # Quick species-holding overview (used as a sanity check against Table 3, Section 3.2)
    print("\nFarms holding each species (sanity check vs. Table 3):")
    for sp, label in SPECIES.items():
        n_holding = (df[f"{sp}_sayi"] > 0).sum()
        print(f"  {label}: {n_holding}")


if __name__ == "__main__":
    main()
