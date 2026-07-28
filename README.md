# Species-Specific Economic Burden of Foot-and-Mouth Disease in Mixed-Species Smallholder Livestock Systems: Evidence from Samsun, Turkiye

## Reproducibility Package

This repository contains the complete reproducibility package
accompanying a manuscript that quantifies and statistically compares
farm-level, FMD-attributable economic losses across cattle, water
buffalo, sheep, and goats on 286 mixed-species smallholder farms in
Samsun Province, Turkiye, surveyed during the 2022-2023 production
period -- a period that coincided with the officially documented 2023
incursion of FMD serotype SAT-2.

This package is intentionally organized around the *study* rather than
any single journal submission. If the manuscript title, framing, or
target journal changes during peer review, this repository and its
contents remain valid without modification.

---

## Repository Overview

This repository follows open science and computational reproducibility
principles and includes:

- Complete Python source code (descriptive statistics, non-parametric
  tests, farm-clustered regression, spatial autocorrelation analysis,
  figure generation)
- The complete farm-level analytical dataset (N = 286 mixed-species
  smallholder farms, 2022-2023)
- Village-level geographic coordinates used for the spatial analysis
- Comprehensive documentation of data provenance, sampling design, and
  known data-quality handling
- Software environment specifications

---

## Repository Structure

```text
FMD-Multispecies-Economics-Samsun/
├── code/
│   ├── _paths.py                          # shared path/config
│   ├── 01_sample_overview.py              # Table 1
│   ├── 02_demographics.py                 # Table 2
│   ├── 03_species_disease_comparison.py   # Table 3; Figure 2; KW/MW tests
│   ├── 04_regression_analysis.py          # Table 4; Figures 3-5; VIF; robustness
│   ├── 05_income_vulnerability.py         # Figure 6; Section 3.5 statistics
│   ├── 06_mortality_analysis.py           # Table 5; Figure 7; consistency check
│   ├── 07_spatial_analysis.py             # Table 6; Figures 8-9 (Moran's I)
│   ├── 08_benchmark_table.py              # Table 7
│   └── run_all.py
├── data/
│   ├── raw/
│   │   └── village_coordinates.csv
│   └── processed/
│       └── farm_level_data.csv            # N=286 farms, main analytical dataset
├── output/                                # generated tables (.csv)
├── figures/                               # Figure 1 (map) + generated Figures 2-9 (.png, 300 DPI)
├── docs/
│   ├── CODEBOOK.md
│   ├── DATA_DESCRIPTION.md
│   ├── REPRODUCIBILITY_CHECKLIST.md
│   └── Replication_Guide.md
├── README.md
├── CHANGELOG.md
├── CITATION.cff
├── .zenodo.json
├── LICENSE
├── requirements.txt
├── environment.yml
└── .gitignore
```

## Documentation

- **docs/CODEBOOK.md** -- analytical workflow and script-by-script description
- **docs/DATA_DESCRIPTION.md** -- data provenance, sampling design, full variable dictionary, and known data-quality notes
- **docs/REPRODUCIBILITY_CHECKLIST.md** -- reproducibility checklist
- **docs/Replication_Guide.md** -- complete, step-by-step replication guide

**Before reusing this dataset, read `docs/DATA_DESCRIPTION.md` in full.**
This is original human-subjects survey data, not third-party public
data; the document covers data governance, the distinction between two
similarly-named income fields, the sampling-stratum field, and several
data-quality issues identified and corrected during analysis.

## Installation

```bash
conda env create -f environment.yml
conda activate fmd-multispecies-econ-repro
```

or

```bash
pip install -r requirements.txt
```

## Run

```bash
cd code
python run_all.py
```

This reproduces the complete analytical workflow: the sampling-stratum
overview (Table 1), household socio-demographic characteristics (Table
2), the species-level FMD occurrence and loss comparison with
Kruskal-Wallis and Bonferroni-corrected pairwise Mann-Whitney tests
(Table 3, Figure 2), the farm-clustered regression with VIF diagnostics
and trimmed-sample robustness check (Table 4, Figures 3-5), farm-level
income vulnerability and the off-farm-income-diversification analysis
(Figure 6), cattle age-sex-class mortality with its data-consistency
check (Table 5, Figure 7), the Moran's I spatial autocorrelation
analysis across five neighborhood sizes (Table 6, Figures 8-9), and the
benchmarking comparison against published estimates (Table 7).

Expected runtime: well under one minute on a standard laptop. The
slowest step is the 999-permutation Moran's I inference in
`07_spatial_analysis.py`.

Figure 1 (the Samsun Province study-area map) was constructed as a
cartographic base map rather than a Python script output; see
`docs/CODEBOOK.md` for details. The finished figure is provided directly
in `figures/Figure1_study_area.png`.

## Script-to-Output Correspondence

| Script | Produces |
|---|---|
| `01_sample_overview.py` | Table 1 (stratum distribution) |
| `02_demographics.py` | Table 2 (socio-demographic characteristics) |
| `03_species_disease_comparison.py` | Table 3 (FMD occurrence and losses by species); Figure 2; Kruskal-Wallis and pairwise Mann-Whitney tests |
| `04_regression_analysis.py` | Table 4 (regression); Figures 3 (species effects), 4 (herd/farm covariates), 5 (prevalence effect); VIF diagnostics; trimmed-sample robustness check |
| `05_income_vulnerability.py` | Figure 6 (income-vulnerability distribution); farm-level income statistics; buffalo-holding and off-farm-income comparisons |
| `06_mortality_analysis.py` | Table 5 (mortality by age-sex class); Figure 7; mortality data-consistency check; chi-square and two-proportion z-tests |
| `07_spatial_analysis.py` | Table 6 (Moran's I by k); Figure 8 (prevalence map); Figure 9 (Moran scatterplot) |
| `08_benchmark_table.py` | Table 7 (benchmarking against published estimates) |
| *(static base map; see docs/CODEBOOK.md)* | Figure 1 (Samsun Province map) |

## A Note on Two Similarly Named Income Variables

The analytical dataset intentionally carries two distinct off-farm
income measures; using the wrong one will not reproduce the reported
statistics. This is documented in full in `docs/DATA_DESCRIPTION.md`:

- `nonfarm_income` ("Tarim disi gelir") -- income from sources entirely
  outside agriculture. **This is the field used** to define "off-farm
  income source" throughout the manuscript (Table 2: 33.9% of farms;
  Section 3.5 diversification analysis).
- `offfarm_agri_income` ("Isletme disi tarimsal gelir") -- agricultural
  income earned off the respondent's own farm (e.g., day labor on other
  farms). **Not** used in the manuscript's off-farm-income statistics;
  including it changes the reported figure from 33.9% to 37.4%.

## Verification Status

Every script in this package was run and its output compared table-by-
table against the manuscript before this package was finalized. Tables
1, 4, 5, and 6 reproduce **exactly**. Table 2, Table 3, and the income-
vulnerability statistics in Section 3.5 reproduce to within
approximately 1% (minor rounding/ordering differences from the original
iterative analysis; no reported significance level, effect direction, or
ranking is affected). Full detail in `docs/CODEBOOK.md` and
`docs/DATA_DESCRIPTION.md`.

## Citation

Please cite both the published article (once available) and this
archived repository. Citation metadata are provided in `CITATION.cff`
and `.zenodo.json`.

## License

MIT License (code in this repository). The underlying farm-level survey
dataset is original human-subjects research data governed separately;
see `docs/DATA_DESCRIPTION.md` for provenance, anonymization, and terms
of reuse, and `docs/REPRODUCIBILITY_CHECKLIST.md` for the ethics-approval
confirmation required before public deposition.

## Contact

**Halil Tosun**

Department of Animal Science, School of Agricultural and Food Sciences,
ADA University, Baku, Azerbaijan

ORCID: https://orcid.org/0000-0001-5117-0390

Email: halilibrahimtosun@gmail.com

**Hatice Turkten**

Department of Agricultural Economics, Faculty of Agriculture, Ondokuz
Mayis University, Samsun, Turkiye

ORCID: https://orcid.org/0000-0003-2037-7756

## DOI

**Zenodo DOI:** https://doi.org/xxxx *(placeholder -- to be updated upon deposition)*

The manuscript's own DOI (once published) will be added to this file and
to the citation metadata files at that time.

## Version

**Version:** 1.0.0
