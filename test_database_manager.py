from pathlib import Path

from src.database_manager import DatabaseManager


PROJECT_ROOT = Path(__file__).resolve().parent

TEST_DATABASE_PATH = (
    PROJECT_ROOT
    / "database"
    / "agrimind_test.db"
)


def main() -> None:
    try:
        if TEST_DATABASE_PATH.exists():
            TEST_DATABASE_PATH.unlink()

        database = DatabaseManager(
            database_path=TEST_DATABASE_PATH
        )

        crop_input = {
            "nitrogen": 90,
            "phosphorus": 42,
            "potassium": 43,
            "temperature": 20.8,
            "humidity": 82.0,
            "ph": 6.5,
            "rainfall": 202.9,
        }

        crop_result = {
            "success": True,
            "recommended_crop": "Rice",
            "confidence": 98.4,
        }

        crop_id = database.save_crop_prediction(
            input_data=crop_input,
            result=crop_result,
        )

        weather_result = {
            "success": True,
            "temperature": 29.0,
            "humidity": 72,
            "rainfall": 0.0,
            "wind_speed": 16.8,
            "weather_code": 3,
        }

        weather_analysis = {
            "summary": "Warm and humid conditions.",
            "risk_score": 55,
            "risk_level": "Medium",
            "advice": [
                "Monitor crops for fungal disease.",
                "Avoid unnecessary overhead irrigation.",
            ],
        }

        weather_id = database.save_weather_history(
            weather_result=weather_result,
            analysis_result=weather_analysis,
            location="Ahmedabad",
            latitude=23.0225,
            longitude=72.5714,
        )

        disease_result = {
            "success": True,
            "class_name": "Tomato___Late_blight",
            "crop": "Tomato",
            "disease": "Late Blight",
            "status": "diseased",
            "confidence": 91.0,
            "is_reliable": True,
            "risk_level": "High",
            "treatment": [
                "Remove infected leaves.",
                "Avoid overhead irrigation.",
            ],
            "prevention": [
                "Improve airflow.",
                "Avoid prolonged leaf wetness.",
            ],
        }

        disease_id = database.save_disease_prediction(
            result=disease_result,
            image_name="tomato_test.jpg",
        )

        chatbot_result = {
            "success": True,
            "answer": (
                "Remove infected leaves and avoid overhead irrigation."
            ),
            "model": "gemini-3.5-flash",
        }

        chat_id = database.save_chat_message(
            user_message=(
                "What should I do about tomato late blight?"
            ),
            chatbot_result=chatbot_result,
            context_used=True,
        )

        print("Database test completed successfully.")

        print("\nInserted record IDs:")
        print("Crop:", crop_id)
        print("Weather:", weather_id)
        print("Disease:", disease_id)
        print("Chat:", chat_id)

        print("\nRecord counts:")
        print(database.get_record_counts())

        print("\nLatest crop record:")
        print(database.get_crop_history(limit=1)[0])

        print("\nLatest weather record:")
        print(database.get_weather_history(limit=1)[0])

        print("\nLatest disease record:")
        print(database.get_disease_history(limit=1)[0])

        print("\nLatest chat record:")
        print(database.get_chat_history(limit=1)[0])

        print(
            f"\nTest database saved at:\n"
            f"{TEST_DATABASE_PATH}"
        )

    except Exception as error:
        print(f"\nDatabase test failed: {error}")
        raise


if __name__ == "__main__":
    main()