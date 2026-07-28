"""
Shared path configuration. Every script imports this so the package runs
identically regardless of the current working directory it is launched
from.

Tables are written to ../output/ (as .csv). Figures (.png) are written to
../figures/ at 300 DPI.
"""
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
ROOT_DIR = CODE_DIR.parent
RAW_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
OUTPUT_DIR = ROOT_DIR / "output"
FIG_DIR = ROOT_DIR / "figures"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

FARM_LEVEL_CSV = PROCESSED_DIR / "farm_level_data.csv"
VILLAGE_COORDS_CSV = RAW_DIR / "village_coordinates.csv"

FIGURE_DPI = 300

# Currency conversion (Section 2.3 of the manuscript): average TCMB
# indicative USD selling rate for February-March 2023.
TRY_PER_USD = 18.94

# Species analyzed throughout (internal snake_case keys -> display labels)
SPECIES = {
    "sigir": "Cattle",
    "manda": "Water buffalo",
    "koyun": "Sheep",
    "keci": "Goat",
}

# Cattle age-sex classes (internal keys -> display labels), in the order
# reported in Table 5 / Figure 7 of the manuscript
CATTLE_AGE_CLASSES = {
    "boga": "Bulls",
    "buzagi": "Calves",
    "inek": "Cows",
    "duve": "Heifers",
    "dana": "Yearlings",
    "tosun": "Steers",
}
