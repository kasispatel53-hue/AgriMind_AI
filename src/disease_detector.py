import json
from pathlib import Path
from typing import Any, Union

import numpy as np
import tensorflow as tf
from PIL import Image, UnidentifiedImageError

from src.disease_information import get_disease_information
from src.disease_model import PlantDiseaseModelBuilder


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_WEIGHTS_PATH = (
    PROJECT_ROOT
    / "models"
    / "plant_disease_model.weights.h5"
)

DEFAULT_CLASSES_PATH = (
    PROJECT_ROOT
    / "models"
    / "disease_classes.json"
)


class DiseaseDetector:
    """
    Plant disease prediction service for AgriMind AI.

    Responsibilities:
    - Load class names
    - Rebuild the EfficientNetB0 architecture
    - Load trained weights
    - Validate and preprocess images
    - Predict disease class and confidence
    - Return treatment and prevention information
    """

    SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png"}

    def __init__(
        self,
        weights_path: Union[str, Path] = DEFAULT_WEIGHTS_PATH,
        classes_path: Union[str, Path] = DEFAULT_CLASSES_PATH,
        image_size: tuple[int, int] = (224, 224),
        confidence_threshold: float = 0.60,
    ) -> None:
        self.weights_path = Path(weights_path)
        self.classes_path = Path(classes_path)
        self.image_size = image_size
        self.confidence_threshold = confidence_threshold

        self.class_names: list[str] = []
        self.model: tf.keras.Model | None = None

        self._validate_configuration()
        self._load_class_names()
        self._load_model()

    def _validate_configuration(self) -> None:
        """Validate model paths and configuration."""

        if not self.weights_path.exists():
            raise FileNotFoundError(
                f"Disease model weights were not found:\n"
                f"{self.weights_path}"
            )

        if not self.classes_path.exists():
            raise FileNotFoundError(
                f"Disease class file was not found:\n"
                f"{self.classes_path}"
            )

        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ValueError(
                "Confidence threshold must be between 0 and 1."
            )

    def _load_class_names(self) -> None:
        """Load model class names from JSON."""

        with self.classes_path.open(
            mode="r",
            encoding="utf-8",
        ) as file:
            class_names = json.load(file)

        if not isinstance(class_names, list) or len(class_names) < 2:
            raise ValueError(
                "disease_classes.json must contain a list "
                "with at least two classes."
            )

        if not all(isinstance(name, str) for name in class_names):
            raise ValueError(
                "Every disease class name must be a string."
            )

        self.class_names = class_names

    def _load_model(self) -> None:
        """Rebuild the architecture and load trained weights."""

        model_builder = PlantDiseaseModelBuilder(
            number_of_classes=len(self.class_names),
            input_shape=(
                self.image_size[0],
                self.image_size[1],
                3,
            ),
            dropout_rate=0.3,
        )

        self.model = model_builder.build_model()

        self.model.load_weights(
            str(self.weights_path)
        )

    def _validate_image_path(self, image_path: Path) -> None:
        """Validate the supplied image path."""

        if not image_path.exists():
            raise FileNotFoundError(
                f"Image file was not found:\n{image_path}"
            )

        if not image_path.is_file():
            raise ValueError(
                f"The supplied path is not a file:\n{image_path}"
            )

        if image_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                "Unsupported image format. "
                "Use JPG, JPEG, or PNG."
            )

    def _preprocess_image(
        self,
        image_source: Union[str, Path, Image.Image],
    ) -> np.ndarray:
        """
        Open and prepare an image for EfficientNet prediction.
        """

        try:
            if isinstance(image_source, Image.Image):
                image = image_source.copy()

            else:
                image_path = Path(image_source)
                self._validate_image_path(image_path)

                with Image.open(image_path) as opened_image:
                    image = opened_image.copy()

            image = image.convert("RGB")
            image = image.resize(
                self.image_size,
                Image.Resampling.LANCZOS,
            )

            image_array = np.asarray(
                image,
                dtype=np.float32,
            )

            image_batch = np.expand_dims(
                image_array,
                axis=0,
            )

            return image_batch

        except UnidentifiedImageError as error:
            raise ValueError(
                "The selected file is not a valid image."
            ) from error

        except OSError as error:
            raise ValueError(
                f"The image could not be opened: {error}"
            ) from error

    @staticmethod
    def _format_top_predictions(
        probabilities: np.ndarray,
        class_names: list[str],
        limit: int = 3,
    ) -> list[dict[str, Any]]:
        """Return the model's strongest predictions."""

        top_indices = np.argsort(
            probabilities
        )[::-1][:limit]

        return [
            {
                "class_name": class_names[index],
                "confidence": round(
                    float(probabilities[index]) * 100,
                    2,
                ),
            }
            for index in top_indices
        ]

    def predict(
        self,
        image_source: Union[str, Path, Image.Image],
    ) -> dict[str, Any]:
        """
        Predict plant crop and disease from a leaf image.
        """

        try:
            if self.model is None:
                raise RuntimeError(
                    "Disease model has not been loaded."
                )

            image_batch = self._preprocess_image(
                image_source
            )

            predictions = self.model.predict(
                image_batch,
                verbose=0,
            )

            probabilities = predictions[0]

            predicted_index = int(
                np.argmax(probabilities)
            )

            predicted_class = self.class_names[
                predicted_index
            ]

            confidence = float(
                probabilities[predicted_index]
            )

            disease_information = (
                get_disease_information(predicted_class)
            )

            confidence_percentage = round(
                confidence * 100,
                2,
            )

            is_reliable = (
                confidence >= self.confidence_threshold
            )

            message = (
                "Prediction completed successfully."
                if is_reliable
                else (
                    "The model confidence is low. "
                    "Upload a clearer leaf image and consult "
                    "an agricultural expert."
                )
            )

            return {
                "success": True,
                "class_name": predicted_class,
                "crop": disease_information["crop"],
                "disease": disease_information["disease"],
                "status": disease_information["status"],
                "confidence": confidence_percentage,
                "is_reliable": is_reliable,
                "risk_level": disease_information["risk_level"],
                "description": disease_information["description"],
                "treatment": disease_information["treatment"],
                "prevention": disease_information["prevention"],
                "top_predictions": self._format_top_predictions(
                    probabilities=probabilities,
                    class_names=self.class_names,
                ),
                "message": message,
                "warning": (
                    "This is an AI-based prediction and should "
                    "not replace advice from a qualified "
                    "agricultural expert."
                ),
            }

        except Exception as error:
            return {
                "success": False,
                "error": str(error),
                "message": (
                    "Plant disease prediction could not "
                    "be completed."
                ),
            }

    def get_supported_classes(self) -> list[str]:
        """Return all classes supported by the model."""

        return self.class_names.copy()