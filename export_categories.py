
import json
import joblib
from pathlib import Path

# Load the trained model
model = joblib.load("models/final_flight_delay_pipeline.joblib")

# Access the fitted categorical encoder
encoder = (
    model.named_steps["preprocessor"]
    .named_transformers_["cat"]
    .named_steps["onehot"]
)

# Match each category list to its feature
feature_names = [
    "AIRLINE",
    "ORIGIN_AIRPORT",
    "DESTINATION_AIRPORT",
    "ROUTE",
]

categories = {
    name: [str(value) for value in values]
    for name, values in zip(feature_names, encoder.categories_)
}

# Keep all options, including numeric airport identifiers
options = {
    "airlines": categories["AIRLINE"],
    "origin_airports": categories["ORIGIN_AIRPORT"],
    "destination_airports": categories["DESTINATION_AIRPORT"],
}

# Save the options for the frontend
output_path = Path("frontend") / "airport-options.json"
output_path.parent.mkdir(parents=True, exist_ok=True)

with output_path.open("w", encoding="utf-8") as file:
    json.dump(options, file, indent=2)

print("Dropdown options exported successfully!")
print("File:", output_path)
print("Airlines:", len(options["airlines"]))
print("Origin airports:", len(options["origin_airports"]))
print("Destination airports:", len(options["destination_airports"]))
