from src.crop_recommender import CropRecommender


def main():
    recommender = CropRecommender()

    result = recommender.recommend_crop(
        nitrogen=90,
        phosphorus=42,
        potassium=43,
        temperature=20.8,
        humidity=82,
        soil_ph=6.5,
        rainfall=202,
    )

    print("Prediction result:")
    print(result)


if __name__ == "__main__":
    main()