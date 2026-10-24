
import csv
import json
import joblib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
FRONTEND = ROOT / "frontend"

def load_lookup(filename):
    lookup = {}
    path = DATA / filename

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        for row in csv.DictReader(file):
            code = row["Code"].strip()
            description = row["Description"].strip()

            if code and description:
                lookup[code] = description

    return lookup

airport_codes = load_lookup("L_AIRPORT.csv")
airport_ids = load_lookup("L_AIRPORT_ID.csv")

pipeline = joblib.load(
    ROOT / "models" / "final_flight_delay_pipeline.joblib"
)

encoder = (
    pipeline.named_steps["preprocessor"]
    .named_transformers_["cat"]
    .named_steps["onehot"]
)

origin_categories = [
    str(value) for value in encoder.categories_[1]
]
destination_categories = [
    str(value) for value in encoder.categories_[2]
]

def make_options(categories):
    options = []

    for value in categories:
        if value in airport_ids:
            description = airport_ids[value]
        elif value in airport_codes:
            description = airport_codes[value]
        else:
            description = f"Unmapped airport identifier: {value}"

        options.append({
            "value": value,
            "label": f"{description} ({value})"
        })

    return options

result = {
    "origin_airports": make_options(origin_categories),
    "destination_airports": make_options(destination_categories)
}

FRONTEND.mkdir(exist_ok=True)

output = FRONTEND / "airport-display-options.json"
with output.open("w", encoding="utf-8") as file:
    json.dump(result, file, indent=2, ensure_ascii=False)

print("Airport display options created.")
print("Origin options:", len(result["origin_airports"]))
print("Destination options:", len(result["destination_airports"]))
print("Output:", output)
print("Example:", result["origin_airports"][:3])
