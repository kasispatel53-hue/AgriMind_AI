from typing import Tuple

import tensorflow as tf
from tensorflow.keras import Model
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D


class PlantDiseaseModelBuilder:
    """
    Builds an EfficientNetB0-based plant disease classification model.
    """

    def __init__(
        self,
        number_of_classes: int,
        input_shape: Tuple[int, int, int] = (224, 224, 3),
        dropout_rate: float = 0.3,
    ) -> None:
        if number_of_classes <= 1:
            raise ValueError(
                "Number of classes must be greater than 1."
            )

        self.number_of_classes = number_of_classes
        self.input_shape = input_shape
        self.dropout_rate = dropout_rate

    def build_model(self) -> Model:
        """
        Creates an EfficientNetB0 transfer-learning model.
        """

        base_model = EfficientNetB0(
            weights="imagenet",
            include_top=False,
            input_shape=self.input_shape,
        )

        base_model.trainable = False

        inputs = tf.keras.Input(shape=self.input_shape)

        features = base_model(
            inputs,
            training=False,
        )

        features = GlobalAveragePooling2D()(features)

        features = Dropout(
            self.dropout_rate
        )(features)

        outputs = Dense(
            self.number_of_classes,
            activation="softmax",
        )(features)

        model = Model(
            inputs=inputs,
            outputs=outputs,
            name="agrimind_plant_disease_model",
        )

        return model

    @staticmethod
    def compile_model(
        model: Model,
        learning_rate: float = 0.001,
    ) -> None:
        """
        Compiles the model for multi-class classification.
        """

        optimizer = tf.keras.optimizers.Adam(
            learning_rate=learning_rate
        )

        model.compile(
            optimizer=optimizer,
            loss="categorical_crossentropy",
            metrics=["accuracy"],
        )