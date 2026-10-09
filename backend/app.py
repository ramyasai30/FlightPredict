
from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Find the project folder and load the saved ML pipeline.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "final_flight_delay_pipeline.joblib"
)

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Model file not found: {MODEL_PATH}"
    )

model = joblib.load(MODEL_PATH)

FEATURES = [
    "MONTH",
    "DAY",
    "DAY_OF_WEEK",
    "DISTANCE",
    "DEP_HOUR",
    "DEP_MINUTE",
    "ARR_HOUR",
    "ARR_MINUTE",
    "IS_WEEKEND",
    "AIRLINE",
    "ORIGIN_AIRPORT",
    "DESTINATION_AIRPORT",
    "ROUTE",
]


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Flight Delay Prediction API is running"
    })


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Please send flight details as JSON."
        }), 400

    missing = [
        feature for feature in FEATURES
        if feature not in data
    ]

    if missing:
        return jsonify({
            "error": "Missing required fields",
            "fields": missing
        }), 400

    try:
        # Send raw values to the saved pipeline.
        flight_data = pd.DataFrame(
            [{feature: data[feature] for feature in FEATURES}],
            columns=FEATURES
        )

        prediction = int(model.predict(flight_data)[0])

        if not hasattr(model, "predict_proba"):
            return jsonify({
                "error": "The model does not support probability predictions."
            }), 500

        classes = list(model.classes_)

        if 1 not in classes:
            return jsonify({
                "error": "The model has no delayed class (1)."
            }), 500

        delayed_index = classes.index(1)

        probability = float(
            model.predict_proba(flight_data)[0][delayed_index]
        )

        return jsonify({
            "prediction": (
                "DELAYED" if prediction == 1
                else "NOT DELAYED"
            ),
            "delay_probability": round(
                probability * 100, 2
            )
        })

    except (TypeError, ValueError) as error:
        return jsonify({
            "error": f"Invalid input: {error}"
        }), 400

    except Exception:
        app.logger.exception("Prediction failed")
        return jsonify({
            "error": "Prediction failed. Check the backend terminal."
        }), 500


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
