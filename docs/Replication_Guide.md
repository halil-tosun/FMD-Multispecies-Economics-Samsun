# Replication Guide

This guide walks through reproducing every table and figure in the
accompanying manuscript, step by step.

## 1. Set Up the Environment

**Option A -- Conda (recommended)**

```bash
conda env create -f environment.yml
conda activate fmd-multispecies-econ-repro
```

**Option B -- pip**

```bash
python -m venv .venv
source .venv/bin/activate        # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Run the Full Pipeline

```bash
cd code
python run_all.py
```

You should see console output for eight steps, each printing the
table(s)/statistics it produces, followed by a total runtime (well
under one minute on a standard laptop).

## 3. Verify the Outputs

After running, check that the following files exist:

```
output/Table1_stratum_distribution.csv
output/Table2_demographics.csv
output/Table3_species_disease_comparison.csv
output/species_loss_per_animal_long.csv
output/kruskal_wallis_and_pairwise_tests.csv
output/Table4_regression.csv
output/vif_diagnostics.csv
output/regression_robustness_trimmed.csv
output/income_vulnerability_summary.csv
output/income_vulnerability_by_buffalo_status.csv
output/income_vulnerability_by_offfarm_income.csv
output/mortality_consistency_check.csv
output/Table5_mortality_by_ageclass.csv
output/mortality_statistical_tests.csv
output/Table6_moran_i_by_k.csv
output/Table7_benchmark_comparison.csv

figures/Figure2_species_loss_boxplot.png
figures/Figure3_species_effects.png
figures/Figure4_herd_covariates.png
figures/Figure5_prevalence_effect.png
figures/Figure6_income_vulnerability.png
figures/Figure7_mortality_by_ageclass.png
figures/Figure8_prevalence_map.png
figures/Figure9_moran_scatterplot.png
```

`figures/Figure1_study_area.png` is already present in the repository as
a finished cartographic base map (see `docs/CODEBOOK.md`).

## 4. Cross-Check Against the Manuscript

Open each CSV in `output/` and compare its values against the
corresponding table in the manuscript. Tables 1, 4, 5, and 6 should
match exactly. Table 2, Table 3, and the income-vulnerability statistics
should match to within approximately 1% (rounding-level differences; see
`docs/DATA_DESCRIPTION.md`, Section 6, and `docs/CODEBOOK.md`). All
significance levels, effect directions, and rankings match exactly. If
you find a larger discrepancy than described here, please open an issue,
including your Python and package versions.

## 5. Regenerate a Single Table or Figure

Each numbered script can be run independently, for example:

```bash
cd code
python 07_spatial_analysis.py
```

This is useful if you only want to re-verify one specific result (e.g.,
the Moran's I spatial analysis) without rerunning the full pipeline.

## 6. Understanding the Data

Before reusing or extending this dataset, read `docs/DATA_DESCRIPTION.md`
in full, particularly:

- Section 3, on the sampling stratum (`tabaka`) field -- it should be
  used as provided, not re-derived from current herd size.
- Section 4 (full column dictionary), particularly the distinction
  between `nonfarm_income` and `offfarm_agri_income` -- using the wrong
  one (or both) will not reproduce the manuscript's off-farm-income
  statistics.
- Section 6, on known data-quality handling (water buffalo illness
  duration; sheep milk-yield loss; one excluded spurious spreadsheet row).

## 7. Troubleshooting

- **`ModuleNotFoundError`**: confirm the environment from Step 1 is
  activated before running `run_all.py`.
- **Moran's I p-values differ from the manuscript**: confirm you have
  not modified `SEED` in `code/07_spatial_analysis.py`. With the default
  seed (42) and the pinned package versions in `requirements.txt`,
  results should match exactly.
- **Figures look different from the manuscript**: confirm your
  matplotlib version matches `requirements.txt`; minor rendering
  differences across matplotlib versions do not affect the reported
  statistics, only cosmetic details (marker size, font rendering).
- **Small numerical differences in Table 3 / Table 2**: expected; see
  Step 4 above and `docs/DATA_DESCRIPTION.md`, Section 6.
