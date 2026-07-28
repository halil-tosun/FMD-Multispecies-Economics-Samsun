# Reproducibility Checklist

This checklist follows standard computational reproducibility practice
(cf. the ACM/NISO reproducibility badging criteria and common journal
reproducibility policies).

## Code

- [x] Complete analysis code provided (`code/`), covering every table
      and statistically-derived figure in the manuscript.
- [x] Code runs end-to-end via a single entry point (`code/run_all.py`).
- [x] Each numbered script can also be run independently to regenerate
      one specific table/figure.
- [x] No hard-coded absolute file paths; all paths are relative and
      resolved via `code/_paths.py` regardless of the working directory
      the scripts are launched from.
- [x] Random seeds fixed and documented (`docs/CODEBOOK.md`) for the one
      script that uses randomization (`07_spatial_analysis.py`).
- [x] Software environment fully pinned (`requirements.txt`,
      `environment.yml`).

## Data

- [x] The complete analytical dataset is included
      (`data/processed/farm_level_data.csv`, N=286 farms).
- [x] Village-level geocoding data included
      (`data/raw/village_coordinates.csv`).
- [x] Every column is documented (`docs/DATA_DESCRIPTION.md`).
- [x] Data provenance, sampling design, and known data-quality issues
      are documented in full, including issues identified and corrected
      during analysis (`docs/DATA_DESCRIPTION.md`, Sections 3 and 6).
- [ ] **Action required before public deposition:** confirm that ethics
      approval / informed consent covers public release of this
      anonymized, village-level-identified dataset (see
      `docs/DATA_DESCRIPTION.md`, Section 2). This box is intentionally
      left unchecked in this package; check it only after that
      confirmation has been obtained.

## Outputs

- [x] Running `run_all.py` regenerates all 7 manuscript tables plus
      supporting statistical-test output files in `output/`.
- [x] Running `run_all.py` regenerates Figures 2-9 in `figures/` at
      300 DPI; Figure 1 is a static base map provided directly.
- [x] A script-to-output correspondence table is provided
      (`docs/CODEBOOK.md`, `README.md`).

## Verification Performed

- [x] Every script was executed and its console output compared,
      table-by-table, against the corresponding manuscript table before
      this package was finalized.
- [x] Tables 1, 4, 5, and 6 reproduce **exactly**.
- [x] Table 2, Table 3, and the Section 3.5 income-vulnerability
      statistics reproduce to within rounding (differences of less than
      approximately 1%; see `docs/CODEBOOK.md`).
- [x] All reported significance levels, effect directions, and species/
      age-class rankings reproduce exactly.

## Known Limitations of This Package

- Two of 195 villages are geocoded to an approximate (district-center)
  rather than exact coordinate (`docs/DATA_DESCRIPTION.md`, Section 5).
- Small (<1%) rounding-level differences in a subset of Table 3 figures
  (`docs/DATA_DESCRIPTION.md`, Section 6; `docs/CODEBOOK.md`).
