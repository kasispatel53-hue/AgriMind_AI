from pathlib import Path

import joblib
import numpy as np


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "crop_recommendation_model.pkl"


class CropPredictor:
    def __init__(self):
        self.model = self._load_model()

    def _load_model(self):
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Crop recommendation model not found at: {MODEL_PATH}"
            )

        return joblib.load(MODEL_PATH)

    def validate_inputs(
        self,
        nitrogen,
        phosphorus,
        potassium,
        temperature,
        humidity,
        ph,
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

        if not 0 <= ph <= 14:
            errors.append(
                "Soil pH must be between 0 and 14."
            )

        if rainfall < 0:
            errors.append("Rainfall cannot be negative.")

        return errors

    def predict(
        self,
        nitrogen,
        phosphorus,
        potassium,
        temperature,
        humidity,
        ph,
        rainfall,
    ):
        errors = self.validate_inputs(
            nitrogen,
            phosphorus,
            potassium,
            temperature,
            humidity,
            ph,
            rainfall,
        )

        if errors:
            return {
                "success": False,
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
                    ph,
                    rainfall,
                ]
            ],
            dtype=float,
        )

        prediction = self.model.predict(input_data)[0]

        result = {
            "success": True,
            "crop": str(prediction),
            "confidence": None,
        }

        if hasattr(self.model, "predict_proba"):
            probabilities = self.model.predict_proba(input_data)[0]
            confidence = float(np.max(probabilities)) * 100
            result["confidence"] = round(confidence, 2)

        return result