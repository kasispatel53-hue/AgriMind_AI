from pathlib import Path
from typing import Optional, Tuple

import tensorflow as tf


class DiseaseDataLoader:
    """
    Loads and prepares plant-disease image datasets.

    Expected structure:

    PlantVillage/
    ├── train/
    │   ├── Class_1/
    │   └── Class_2/
    └── val/
        ├── Class_1/
        └── Class_2/
    """

    def __init__(
        self,
        dataset_path: str,
        image_size: Tuple[int, int] = (224, 224),
        batch_size: int = 32,
        seed: int = 42,
        selected_classes: Optional[list[str]] = None,
    ) -> None:
        self.dataset_path = Path(dataset_path)
        self.train_path = self.dataset_path / "train"
        self.validation_path = self.dataset_path / "val"

        self.image_size = image_size
        self.batch_size = batch_size
        self.seed = seed
        self.selected_classes = selected_classes

        self.class_names: list[str] = []

        self._validate_directories()
        self._validate_selected_classes()

    def _validate_directories(self) -> None:
        """Check whether the required dataset folders exist."""

        if not self.dataset_path.exists():
            raise FileNotFoundError(
                f"Dataset folder does not exist: {self.dataset_path}"
            )

        if not self.train_path.exists():
            raise FileNotFoundError(
                f"Training folder does not exist: {self.train_path}"
            )

        if not self.validation_path.exists():
            raise FileNotFoundError(
                f"Validation folder does not exist: {self.validation_path}"
            )

    def _validate_selected_classes(self) -> None:
        """Check whether every selected class exists."""

        if self.selected_classes is None:
            return

        train_classes = {
            folder.name
            for folder in self.train_path.iterdir()
            if folder.is_dir()
        }

        validation_classes = {
            folder.name
            for folder in self.validation_path.iterdir()
            if folder.is_dir()
        }

        missing_train_classes = (
            set(self.selected_classes) - train_classes
        )

        missing_validation_classes = (
            set(self.selected_classes) - validation_classes
        )

        if missing_train_classes:
            raise ValueError(
                "Selected classes missing from training folder: "
                f"{sorted(missing_train_classes)}"
            )

        if missing_validation_classes:
            raise ValueError(
                "Selected classes missing from validation folder: "
                f"{sorted(missing_validation_classes)}"
            )

    def load_datasets(
        self,
    ) -> tuple[tf.data.Dataset, tf.data.Dataset]:
        """Load training and validation datasets."""

        train_dataset = tf.keras.utils.image_dataset_from_directory(
            directory=self.train_path,
            class_names=self.selected_classes,
            image_size=self.image_size,
            batch_size=self.batch_size,
            label_mode="categorical",
            shuffle=True,
            seed=self.seed,
        )

        validation_dataset = tf.keras.utils.image_dataset_from_directory(
            directory=self.validation_path,
            class_names=self.selected_classes,
            image_size=self.image_size,
            batch_size=self.batch_size,
            label_mode="categorical",
            shuffle=False,
        )

        self.class_names = train_dataset.class_names

        self._verify_class_consistency(
            train_dataset.class_names,
            validation_dataset.class_names,
        )

        train_dataset = self._optimize_dataset(train_dataset)
        validation_dataset = self._optimize_dataset(
            validation_dataset
        )

        return train_dataset, validation_dataset

    @staticmethod
    def _verify_class_consistency(
        train_classes: list[str],
        validation_classes: list[str],
    ) -> None:
        """Ensure training and validation classes match."""

        if train_classes != validation_classes:
            raise ValueError(
                "Training and validation class folders do not match."
            )

    @staticmethod
    def _optimize_dataset(
        dataset: tf.data.Dataset,
    ) -> tf.data.Dataset:
        """Improve dataset loading performance."""

        return dataset.prefetch(
            buffer_size=tf.data.AUTOTUNE
        )

    def get_class_names(self) -> list[str]:
        """Return detected class names."""

        return self.class_names

    def get_number_of_classes(self) -> int:
        """Return number of detected classes."""

        return len(self.class_names) 