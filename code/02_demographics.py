"""
02_demographics.py
====================
Reproduces Table 2 (socio-demographic characteristics of surveyed farm
households, N=286; manuscript Section 3.1).

Education is recorded as years of formal schooling (0/5/8/12/16),
following the standard Turkish schooling-stage encoding:
  0  = Illiterate / no formal schooling
  5  = Primary school
  8  = Secondary school
  12 = High school
  16 = University

Produces:
  output/Table2_demographics.csv
"""
import pandas as pd
from _paths import FARM_LEVEL_CSV, OUTPUT_DIR

EDUCATION_LABELS = {
    0: "Illiterate / no formal schooling",
    5: "Primary school",
    8: "Secondary school",
    12: "High school",
    16: "University",
}


def main():
    df = pd.read_csv(FARM_LEVEL_CSV)
    n = len(df)

    # NOTE: "off-farm income" here follows the manuscript's definition exactly:
    # it uses only the `nonfarm_income` field ("Tarim disi gelir", i.e. income
    # from sources outside agriculture entirely). The dataset also contains a
    # distinct `offfarm_agri_income` field ("Isletme disi tarimsal gelir",
    # i.e. agricultural income earned off the farm, e.g. day labor on other
    # farms), which is NOT included here. Including both fields would give
    # 37.4% instead of the 33.9% reported in the manuscript (Table 2, Section
    # 3.1) -- see docs/DATA_DESCRIPTION.md for the full explanation.
    off_farm = (df["nonfarm_income"].fillna(0) > 0)

    rows = [
        {"characteristic": "Operator age (years), mean +/- SD",
         "value": f"{df['operator_age'].mean():.1f} +/- {df['operator_age'].std():.1f}"},
        {"characteristic": "Operator age, range",
         "value": f"{df['operator_age'].min():.0f}-{df['operator_age'].max():.0f}"},
        {"characteristic": "Farming experience (years), mean",
         "value": f"{df['farming_experience_years'].mean():.1f}"},
        {"characteristic": "Livestock-keeping experience (years), mean",
         "value": f"{df['livestock_experience_years'].mean():.1f}"},
        {"characteristic": "Household size, mean",
         "value": f"{df['household_size'].mean():.1f}"},
        {"characteristic": "Household members working in agriculture, mean",
         "value": f"{df['household_members_in_agriculture'].mean():.1f}"},
        {"characteristic": "Farms with off-farm income source (%)",
         "value": f"{100 * off_farm.mean():.1f}"},
    ]

    edu_counts = df["education_code"].value_counts(normalize=True).sort_index() * 100
    for code, label in EDUCATION_LABELS.items():
        pct = edu_counts.get(code, 0.0)
        rows.append({"characteristic": f"Education: {label}", "value": f"{pct:.1f}"})

    table2 = pd.DataFrame(rows)
    table2.to_csv(OUTPUT_DIR / "Table2_demographics.csv", index=False)

    print(f"Table 2. Socio-demographic characteristics of surveyed farm households (N={n})")
    print(table2.to_string(index=False))


if __name__ == "__main__":
    main()
