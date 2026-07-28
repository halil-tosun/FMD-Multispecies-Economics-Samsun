# Data Description

## 1. Overview

`data/processed/farm_level_data.csv` contains one row per surveyed farm
(N = 286) in Samsun Province, Turkiye, collected during the 2022-2023
production period. It is the single analytical dataset underlying every
table and figure in the manuscript.

`data/raw/village_coordinates.csv` contains geographic coordinates for
the 195 unique villages represented in the farm sample, obtained by bulk
geocoding (see Section 5 below).

## 2. Provenance and Data Governance

This is original, human-subjects survey data (farmer interviews), **not**
third-party public data. Before this dataset is made public (e.g., on
Zenodo), please confirm the following, consistent with the manuscript's
Ethics Statement (Section on ethics in the manuscript):

- The ethics approval covering the original data collection extends to
  public deposition of the anonymized dataset.
- No direct personal identifiers (respondent name, phone number, national
  ID) are present in this file. As distributed here, the dataset contains
  none of these. The finest geographic identifier retained is
  village/neighborhood (`koy`) within district (`ilce`) -- comparable in
  granularity to cluster-level identifiers commonly released in
  household survey microdata (e.g., DHS, LSMS) -- which is necessary to
  reproduce the village-level spatial analysis (Table 6, Figures 8-9).
  If your ethics approval or informed consent language does not cover
  release of village-level identifiers, aggregate `koy` before deposition
  (e.g., to `ilce` only) and note that Figures 8-9 and Table 6 will no
  longer be exactly reproducible at village resolution.

This dataset also previously supported a separate published analysis of
water buffalo milk production economics and environmental performance in
Samsun Province (Yildirim, 2024; see manuscript Section 2.2). Both
studies draw on the same underlying farm survey but ask different
research questions using different variables and methods.

## 3. Sampling Design

Farms were selected via Neyman-allocation stratified random sampling,
stratified into three strata by total livestock holdings (all species
combined): Stratum 1 (20-49 head), Stratum 2 (50-384 head), Stratum 3
(>=385 head). See manuscript Section 2.2 for the full allocation formula.

**A note on the `tabaka` (stratum) field:** the realized stratum
distribution (`tabaka` values 1/2/3 in this dataset: 119/117/50 farms)
does not perfectly correspond to a simple re-classification of *current*
total animal counts against the three ranges above (best match ~59%).
This is expected and is documented in the manuscript (Section 2.2 and
Limitations): stratum assignment reflects the sampling-frame data
available at the design stage, while the animal counts in this dataset
reflect the farm's holdings at the time of the survey, which can differ
due to ordinary herd turnover (purchases, sales, births) between frame
construction and data collection. **Use the `tabaka` field as provided;
do not attempt to re-derive it from current herd size.**

## 4. Column Definitions

| Column | Description |
|---|---|
| `farm_id` | Sequential farm identifier (1-286), assigned during data extraction; not a field from the original survey instrument. |
| `ilce` | District (ilce) name. |
| `koy` | Village/neighborhood (koy/mahalle) name. |
| `tabaka` | Sampling stratum (1/2/3); see Section 3 above. |
| `operator_age` | Farm operator's age (years). |
| `education_code` | Years of formal schooling: 0 = illiterate/no formal schooling, 5 = primary, 8 = secondary, 12 = high school, 16 = university. |
| `farming_experience_years` | Years the operator has farmed on their own account. |
| `livestock_experience_years` | Years the operator has kept livestock. |
| `household_size` | Number of people in the household. |
| `household_members_in_agriculture` | Number of household members working in agriculture. |
| `nonfarm_income` | Household income from sources entirely outside agriculture (TRY/year). This is the field used to define "off-farm income source" in Table 2 and Section 3.5. |
| `offfarm_agri_income` | Household income from agricultural work performed *off* the respondent's own farm (TRY/year) -- e.g., day labor on other farms. **Not** used in the manuscript's off-farm-income definition; kept here for completeness/reuse but must not be combined with `nonfarm_income` when reproducing Table 2 or Section 3.5 (doing so gives 37.4% instead of the reported 33.9%). |
| `crop_income` | Annual crop production income (TRY), summed across all reported crops. |
| `livestock_income` | Annual livestock production income (TRY): milk + meat + by-product sales, summed across all four species. |
| `{species}_sayi` | Number of animals of that species held by the farm (species keys: `sigir`=cattle, `manda`=water buffalo, `koyun`=sheep, `keci`=goat). |
| `{species}_hastalanan` | Number of animals of that species clinically diagnosed with FMD during the recall period. |
| `{species}_hastalik_suresi_gun` | Illness duration (days) reported for that species. A value of exactly 0 among farms reporting `hastalanan > 0` is treated as a missing response, not a true zero-day illness (affects water buffalo in particular: 39 of 85 affected farms) -- see `code/03_species_disease_comparison.py` and Section 6 below. |
| `{species}_sut_geliri` / `{species}_hasta_sut_geliri` | Milk revenue: farm-stated baseline (absent disease) / observed under disease conditions. |
| `{species}_et_geliri` / `{species}_hasta_et_geliri` | Meat (live-weight) revenue: baseline / observed under disease. |
| `{species}_ilave_masraf` | Additional producer-borne treatment cost (TRY) attributable to the disease episode. |
| `cattle_{ageclass}_satin_alinan` / `_dogan` / `_satilan` / `_olen` / `_evde_kesilen` / `_sene_sonu` | Herd-flow accounting for each cattle age-sex class (`boga`=bulls, `inek`=cows, `duve`=heifers, `tosun`=steers, `dana`=yearlings, `buzagi`=calves): purchased / born / sold / died / home-slaughtered / year-end count. Used to reconstruct exposure and mortality rate (Table 5). |
| `village_lat`, `village_lon` | Village-level latitude/longitude (WGS84), from `data/raw/village_coordinates.csv`. |

## 5. Village Geocoding

Village coordinates were obtained via bulk geocoding (Geoapify API, using
the OpenStreetMap Nominatim database) of all 195 unique district-village
name pairs in the sample. 193 of 195 villages matched with high
confidence. Two villages sharing an ambiguous "Merkez" designation in
Tekkekoy district were geocoded to incorrect locations elsewhere in
Turkiye by the automated service (identified by manual bounding-box and
province-name inspection) and were instead assigned the Tekkekoy
district-center coordinate (41.213265 N, 36.463127 E) as an approximation.
This affects only 2 of 286 farms and only the exact within-district
position of those two farms in Figures 8-9; it does not affect any other
result.

## 6. Known Data-Quality Notes

- **Water buffalo illness duration:** 39 of 85 buffalo-affected farms
  recorded a duration of exactly 0 days, which is biologically
  implausible for an animal recorded as clinically affected. These are
  treated as missing (not zero) when computing mean illness duration in
  `code/03_species_disease_comparison.py`. No other variable is affected
  for these farms.
- **Sheep milk-yield loss:** recorded as 0% for all sheep-affected farms.
  This reflects that surveyed sheep flocks are predominantly meat-oriented
  and not routinely milked, rather than a data-recording error (weight-loss
  data for sheep are non-zero and consistent with disease impact).
- **One spurious spreadsheet row:** the original raw spreadsheet
  contained one additional row past the 286 valid farm records that was
  an AVERAGE-formula artifact (non-integer values across all fields,
  `#DIV/0!` in text columns), not a genuine farm record. It has already
  been excluded from `farm_level_data.csv`.
- **Minor rounding differences:** a small number of manuscript-reported
  figures (illness duration, yield-loss percentages, per-animal loss in
  TRY/USD) may differ from this package's output by less than
  approximately 1% due to minor, undocumented rounding/ordering choices
  made during the original iterative analysis. No statistical
  conclusion, ranking, or significance level reported in the manuscript
  is affected. Tables 1, 4, 5, and 6 reproduce exactly.

## 7. Currency Conversion

TRY-to-USD conversion throughout uses a single fixed rate, 1 USD = 18.94
TRY, the average Central Bank of the Republic of Turkiye (TCMB)
indicative USD selling rate for February-March 2023 (the period during
which all surveys were completed). See `code/_paths.py` (`TRY_PER_USD`).

## 8. External Benchmark Data (Table 7)

Four of the eight rows in Table 7 are not derived from this dataset;
they are fixed values transcribed directly from previously published
studies, for descriptive benchmarking only (manuscript Section 3.8):

| Source | Value used |
|---|---|
| Ekou, J., Edwetu, M. (2026). *Discover Animals*, 3, 16. | USD 323 per affected household (Uganda) |
| Tadesse, B. et al. (2020). *Veterinary Medicine and Science*, 6(4), 815-824. | USD 34 (mixed crop-livestock) and USD 459 (commercial dairy) per Ethiopian herd/farm |
| Knight-Jones, T.J.D., Rushton, J. (2013). *Preventive Veterinary Medicine*, 112(3-4), 161-173. | USD 6.5-21 billion, global annual endemic-region losses |

See `code/08_benchmark_table.py` and the manuscript's reference list for
full citation details.
