import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import tensorflow as tf

from src.disease_model import PlantDiseaseModelBuilder
from src.disease_preprocessing import DiseaseDataLoader


# =========================================================
# Paths
# =========================================================

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "plant_disease"
    / "raw"
    / "plant_disease"
    / "PlantVillage"
)

MODELS_DIRECTORY = PROJECT_ROOT / "models"

WEIGHTS_PATH = (
    MODELS_DIRECTORY
    / "plant_disease_model.weights.h5"
)

CLASS_NAMES_PATH = (
    MODELS_DIRECTORY
    / "disease_classes.json"
)

HISTORY_PATH = (
    MODELS_DIRECTORY
    / "disease_training_history.json"
)


# =========================================================
# Selected classes
# =========================================================

SELECTED_CLASSES = [
    "Pepper,_bell___Bacterial_spot",
    "Pepper,_bell___healthy",
    "Potato___Early_blight",
    "Potato___healthy",
    "Potato___Late_blight",
    "Tomato___Early_blight",
    "Tomato___healthy",
    "Tomato___Late_blight",
]


# =========================================================
# Fast training configuration
# =========================================================

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32

# Two epochs are enough for our first working version.
EPOCHS = 2

LEARNING_RATE = 0.001
SEED = 42


def save_class_names(class_names: list[str]) -> None:
    """Save class names in the exact model-output order."""

    with CLASS_NAMES_PATH.open(
        mode="w",
        encoding="utf-8",
    ) as file:
        json.dump(
            class_names,
            file,
            indent=4,
        )


def save_training_history(
    history: tf.keras.callbacks.History,
) -> None:
    """Save training metrics as JSON."""

    history_data = {
        metric: [float(value) for value in values]
        for metric, values in history.history.items()
    }

    with HISTORY_PATH.open(
        mode="w",
        encoding="utf-8",
    ) as file:
        json.dump(
            history_data,
            file,
            indent=4,
        )


def main() -> None:
    """Train the AgriMind AI disease model."""

    print("=" * 60)
    print("AgriMind AI - Plant Disease Model Training")
    print("=" * 60)

    tf.keras.utils.set_random_seed(SEED)

    MODELS_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found:\n{DATASET_PATH}"
        )

    print("\nLoading dataset...")

    data_loader = DiseaseDataLoader(
        dataset_path=str(DATASET_PATH),
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        seed=SEED,
        selected_classes=SELECTED_CLASSES,
    )

    train_dataset, validation_dataset = (
        data_loader.load_datasets()
    )

    class_names = data_loader.get_class_names()
    number_of_classes = data_loader.get_number_of_classes()

    print(f"\nNumber of classes: {number_of_classes}")

    for index, class_name in enumerate(
        class_names,
        start=1,
    ):
        print(f"{index}. {class_name}")

    save_class_names(class_names)

    print("\nBuilding EfficientNetB0 model...")

    model_builder = PlantDiseaseModelBuilder(
        number_of_classes=number_of_classes,
        input_shape=(224, 224, 3),
        dropout_rate=0.3,
    )

    model = model_builder.build_model()

    model_builder.compile_model(
        model=model,
        learning_rate=LEARNING_RATE,
    )

    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=1,
            restore_best_weights=True,
            verbose=1,
        ),
    ]

    print("\nStarting fast training...")
    print(f"Epochs: {EPOCHS}")
    print(f"Batch size: {BATCH_SIZE}")

    history = model.fit(
        train_dataset,
        validation_data=validation_dataset,
        epochs=EPOCHS,
        callbacks=callbacks,
        verbose=1,
    )

    print("\nSaving model weights...")

    model.save_weights(str(WEIGHTS_PATH))

    save_training_history(history)

    training_accuracy = history.history["accuracy"][-1]
    validation_accuracy = history.history["val_accuracy"][-1]

    print("\n" + "=" * 60)
    print("Training completed successfully")
    print("=" * 60)

    print(
        f"Training accuracy: "
        f"{training_accuracy * 100:.2f}%"
    )

    print(
        f"Validation accuracy: "
        f"{validation_accuracy * 100:.2f}%"
    )

    print(f"\nWeights saved at:\n{WEIGHTS_PATH}")
    print(f"\nClasses saved at:\n{CLASS_NAMES_PATH}")
    print(f"\nHistory saved at:\n{HISTORY_PATH}")


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print(
            "\nTraining was manually interrupted. "
            "Please run the command again and wait."
        )

    except Exception as error:
        print(f"\nTraining failed: {error}")
        raise