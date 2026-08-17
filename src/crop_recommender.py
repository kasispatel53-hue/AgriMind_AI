from pathlib import Path

import joblib
import numpy as np


# --------------------------------------------------
# Model path
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "crop_recommendation_model.pkl"
)


# --------------------------------------------------
# Crop recommender backend
# --------------------------------------------------

class CropRecommender:
    def __init__(self):
        self.model = self.load_model()

    def load_model(self):
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                "Crop recommendation model was not found at:\n"
                f"{MODEL_PATH}"
            )

        return joblib.load(MODEL_PATH)

    def validate_inputs(
        self,
        nitrogen,
        phosphorus,
        potassium,
        temperature,
        humidity,
        soil_ph,
        rainfall,
    ):
        errors = []

        if nitrogen < 0:
            errors.append("Nitrogen cannot be negative.")

        if phosphorus < 0:
            errors.append("Phosphorus cannot be negative.")

        if potassium < 0:
            errors.append("Potassium cannot be negative.")

        if not -20 <= temperature <= 70:
            errors.append(
                "Temperature must be between -20°C and 70°C."
            )

        if not 0 <= humidity <= 100:
            errors.append(
                "Humidity must be between 0 and 100 percent."
            )

        if not 0 <= soil_ph <= 14:
            errors.append(
                "Soil pH must be between 0 and 14."
            )

        if rainfall < 0:
            errors.append("Rainfall cannot be negative.")

        return errors

    def recommend_crop(
        self,
        nitrogen,
        phosphorus,
        potassium,
        temperature,
        humidity,
        soil_ph,
        rainfall,
    ):
        errors = self.validate_inputs(
            nitrogen=nitrogen,
            phosphorus=phosphorus,
            potassium=potassium,
            temperature=temperature,
            humidity=humidity,
            soil_ph=soil_ph,
            rainfall=rainfall,
        )

        if errors:
            return {
                "success": False,
                "crop": None,
                "confidence": None,
                "errors": errors,
            }

        input_data = np.array(
            [
                [
                    nitrogen,
                    phosphorus,
                    potassium,
                    temperature,
                    humidity,
                    soil_ph,
                    rainfall,
                ]
            ],
            dtype=float,
        )

        prediction = self.model.predict(input_data)[0]

        confidence = None

        if hasattr(self.model, "predict_proba"):
            probabilities = self.model.predict_proba(
                input_data
            )[0]

            confidence = round(
                float(np.max(probabilities)) * 100,
                2,
            )

        return {
            "success": True,
            "crop": str(prediction),
            "confidence": confidence,
            "errors": [],
        }