# Changelog

All notable changes to this reproducibility package are documented in
this file.

## [1.0.0] - 2026-07-28

### Added
- Initial public reproducibility package accompanying the manuscript
  "Species-Specific Economic Burden of Foot-and-Mouth Disease in
  Mixed-Species Smallholder Livestock Systems: Evidence from Samsun,
  Turkiye."
- Complete analytical dataset (`data/processed/farm_level_data.csv`,
  N = 286 farms) and village-level geocoding data
  (`data/raw/village_coordinates.csv`).
- Eight numbered analysis scripts (`code/01_*.py` - `code/08_*.py`)
  reproducing Tables 1-7 and Figures 2-9, plus `run_all.py`.
- Full documentation set (`docs/CODEBOOK.md`,
  `docs/DATA_DESCRIPTION.md`, `docs/REPRODUCIBILITY_CHECKLIST.md`,
  `docs/Replication_Guide.md`).

### Known Issues (see `docs/DATA_DESCRIPTION.md` for full detail)
- Two of 195 villages are geocoded to an approximate rather than exact
  coordinate.
- A subset of Table 3 figures reproduce to within ~1% rather than
  exactly, due to minor rounding/ordering choices in the original
  iterative analysis.
