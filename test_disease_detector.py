from pathlib import Path

from src.disease_detector import DiseaseDetector


PROJECT_ROOT = Path(__file__).resolve().parent

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "plant_disease"
    / "raw"
    / "plant_disease"
    / "PlantVillage"
    / "val"
)


def find_test_image(
    class_name: str,
) -> Path:
    """Find the first image in a validation class folder."""

    class_folder = DATASET_PATH / class_name

    if not class_folder.exists():
        raise FileNotFoundError(
            f"Test class folder was not found:\n{class_folder}"
        )

    supported_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
    }

    for image_path in class_folder.iterdir():
        if (
            image_path.is_file()
            and image_path.suffix.lower()
            in supported_extensions
        ):
            return image_path

    raise FileNotFoundError(
        f"No test image was found inside:\n{class_folder}"
    )


def main() -> None:
    """Test the complete disease detection backend."""

    try:
        print("Loading plant disease detector...")

        detector = DiseaseDetector(
            confidence_threshold=0.60
        )

        print("Model loaded successfully.")

        print(
            "Supported classes:",
            len(detector.get_supported_classes()),
        )

        test_class = "Tomato___Late_blight"

        test_image_path = find_test_image(
            test_class
        )

        print(f"\nTest image:\n{test_image_path}")

        result = detector.predict(
            test_image_path
        )

        print("\nPrediction result:")

        if not result["success"]:
            print("Prediction failed.")
            print("Error:", result["error"])
            return

        print("Crop:", result["crop"])
        print("Disease:", result["disease"])
        print("Status:", result["status"])
        print("Confidence:", f"{result['confidence']}%")
        print("Reliable:", result["is_reliable"])
        print("Risk level:", result["risk_level"])
        print("Description:", result["description"])

        print("\nTreatment:")

        for item in result["treatment"]:
            print("-", item)

        print("\nPrevention:")

        for item in result["prevention"]:
            print("-", item)

        print("\nTop predictions:")

        for prediction in result["top_predictions"]:
            print(
                f"- {prediction['class_name']}: "
                f"{prediction['confidence']}%"
            )

        print("\nWarning:", result["warning"])

    except Exception as error:
        print(f"\nDisease detector test failed: {error}")


if __name__ == "__main__":
    main()