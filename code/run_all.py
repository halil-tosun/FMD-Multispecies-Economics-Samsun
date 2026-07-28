"""
run_all.py
==========
Runs the full analytical pipeline in order and writes every table
(.csv) reported in the manuscript to ../output/, and Figures 2-9
(.png, 300 DPI) to ../figures/.

Expected runtime: well under one minute on a standard laptop. The
slowest step is the 999-permutation Moran's I inference in
07_spatial_analysis.py (999 permutations x 5 values of k).

Run individual numbered scripts directly to regenerate only one table
or figure, e.g.: python 04_regression_analysis.py

Figure 1 (the Samsun Province study-area map) is provided directly in
../figures/Figure1_study_area.png; it is a cartographic base map, not
a script-generated statistical figure, and is therefore not produced
by this pipeline. See docs/CODEBOOK.md.
"""
import importlib.util
import os
import time

HERE = os.path.dirname(__file__)


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if hasattr(mod, "main"):
        mod.main()
    return mod


if __name__ == "__main__":
    t0 = time.time()

    print("=== 01: Sample overview and Table 1 (stratum distribution) ===")
    _load("01_sample_overview")

    print("\n=== 02: Table 2 (socio-demographic characteristics) ===")
    _load("02_demographics")

    print("\n=== 03: Table 3, Figure 2, Kruskal-Wallis + Mann-Whitney tests ===")
    _load("03_species_disease_comparison")

    print("\n=== 04: Table 4, Figures 3-5, VIF, trimmed robustness check ===")
    _load("04_regression_analysis")

    print("\n=== 05: Income vulnerability, Figure 6 ===")
    _load("05_income_vulnerability")

    print("\n=== 06: Table 5, Figure 7 (cattle age-sex-class mortality) ===")
    _load("06_mortality_analysis")

    print("\n=== 07: Table 6, Figures 8-9 (Moran's I spatial autocorrelation) ===")
    _load("07_spatial_analysis")

    print("\n=== 08: Table 7 (benchmarking against published estimates) ===")
    _load("08_benchmark_table")

    print(f"\nAll done in {time.time() - t0:.0f} seconds.")
    print("See ../output/ for all tables and ../figures/ for Figures 2-9.")
    print("Figure 1 (Samsun Province map) is a static base map -- see docs/CODEBOOK.md.")
