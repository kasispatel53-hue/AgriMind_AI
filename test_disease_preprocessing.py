from src.disease_preprocessing import DiseaseDataLoader


DATASET_PATH = (
    r"D:\Projects\AgriMind_AI\data\plant_disease"
    r"\raw\plant_disease\PlantVillage"
)


def main() -> None:
    try:
        data_loader = DiseaseDataLoader(
            dataset_path=DATASET_PATH,
            image_size=(224, 224),
            batch_size=32,
        )

        train_dataset, validation_dataset = data_loader.load_datasets()

        print("\nDataset loaded successfully.")
        print(f"Number of classes: {data_loader.get_number_of_classes()}")

        print("\nClass names:")

        for index, class_name in enumerate(
            data_loader.get_class_names(),
            start=1,
        ):
            print(f"{index}. {class_name}")

        for images, labels in train_dataset.take(1):
            print("\nFirst training batch:")
            print(f"Image batch shape: {images.shape}")
            print(f"Label batch shape: {labels.shape}")

        for images, labels in validation_dataset.take(1):
            print("\nFirst validation batch:")
            print(f"Image batch shape: {images.shape}")
            print(f"Label batch shape: {labels.shape}")

    except Exception as error:
        print(f"\nDataset loading failed: {error}")


if __name__ == "__main__":
    main()