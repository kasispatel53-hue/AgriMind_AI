from src.agri_assistant import AgriAssistant


def main() -> None:
    print("Loading AgriMind Assistant...")
    assistant = AgriAssistant()
    print("Assistant loaded successfully.\n")

    crop_result = {
        "success": True,
        "crop": "rice",
        "confidence": 98.4,
    }

    weather_result = {
        "success": True,
        "location": "Ahmedabad",
        "temperature": 29.1,
        "humidity": 72,
        "rainfall": 0.0,
        "wind_speed": 10.8,
        "weather_code": 3,
    }

    weather_analysis = {
        "risk_score": 55.0,
        "risk_level": "Medium",
        "summary": "Warm and humid conditions.",
        "advice": [
            "Monitor crops for fungal disease.",
            "Avoid unnecessary overhead irrigation.",
        ],
    }

    disease_result = {
        "success": True,
        "crop": "Tomato",
        "disease": "Late Blight",
        "status": "diseased",
        "confidence": 91.0,
        "risk_level": "High",
        "reliable": True,
        "treatment": [
            "Remove infected leaves.",
            "Avoid overhead irrigation.",
        ],
        "prevention": [
            "Improve airflow.",
            "Avoid prolonged leaf wetness.",
        ],
    }

    print("Local combined summary:")
    summary = assistant.create_summary(
        crop_result=crop_result,
        weather_result=weather_result,
        weather_analysis=weather_analysis,
        disease_result=disease_result,
    )
    print(summary)

    print("\nIntegrated AI advice:")
    response = assistant.generate_integrated_advice(
        question=(
            "Based on these crop, weather, and disease results, "
            "what should the farmer do today?"
        ),
        crop_result=crop_result,
        weather_result=weather_result,
        weather_analysis=weather_analysis,
        disease_result=disease_result,
    )

    if response.get("success"):
        print(response.get("answer"))
        print("\nContext available:", response.get("context_available"))
        print("Model:", response.get("model"))
    else:
        print("AI request failed.")
        print("Error:", response.get("error"))


if __name__ == "__main__":
    main()