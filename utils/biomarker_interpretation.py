
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
REFERENCE_PATH = (
    BASE_DIR / "model" / "voice_sense_biomarker_reference.json"
)


def load_biomarker_reference():
    if not REFERENCE_PATH.exists():
        return None

    with open(REFERENCE_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def interpret_biomarker(name, value, reference):
    if not reference or name not in reference.get("features", {}):
        return {
            "status": "Reference unavailable",
            "p05": None,
            "median": None,
            "p95": None,
        }

    limits = reference["features"][name]
    lower = limits["p05"]
    upper = limits["p95"]

    if value < lower:
        status = "Below healthy-dataset reference range"
    elif value > upper:
        status = "Above healthy-dataset reference range"
    else:
        status = "Within healthy-dataset reference range"

    return {
        "status": status,
        "p05": lower,
        "median": limits["median"],
        "p95": upper,
    }
