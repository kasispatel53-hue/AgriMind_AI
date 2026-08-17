from src.disease_model import PlantDiseaseModelBuilder


def main() -> None:
    try:
        model_builder = PlantDiseaseModelBuilder(
            number_of_classes=38,
            input_shape=(224, 224, 3),
            dropout_rate=0.3,
        )

        model = model_builder.build_model()

        model_builder.compile_model(
            model=model,
            learning_rate=0.001,
        )

        print("\nModel created successfully.\n")

        model.summary()

        print("\nInput shape:", model.input_shape)
        print("Output shape:", model.output_shape)

    except Exception as error:
        print(f"\nModel creation failed: {error}")


if __name__ == "__main__":
    main()