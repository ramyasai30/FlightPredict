
import joblib
from sklearn.preprocessing import OneHotEncoder

model = joblib.load("models/final_flight_delay_pipeline.joblib")

print("Model loaded successfully:", type(model).__name__)

encoders = [
    obj
    for obj in model.get_params(deep=True).values()
    if isinstance(obj, OneHotEncoder) and hasattr(obj, "categories_")
]

if not encoders:
    raise RuntimeError("Could not find a fitted OneHotEncoder in the model.")

for encoder in encoders:
    feature_names = getattr(
        encoder, "feature_names_in_", None
    )

    if feature_names is None:
        feature_names = [
            f"Feature {i + 1}"
            for i in range(len(encoder.categories_))
        ]

    for name, categories in zip(
        feature_names, encoder.categories_
    ):
        categories = sorted(str(value) for value in categories)

        if name == "ROUTE":
            print(f"\n{name}: {len(categories)} categories")
            print("First 20 routes:", categories[:20])
        else:
            print(f"\n{name}: {len(categories)} categories")
            print(", ".join(categories))

