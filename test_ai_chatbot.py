from src.ai_chatbot import AgriMindChatbot


def main() -> None:
    try:
        print("Loading AgriMind Gemini chatbot...")

        chatbot = AgriMindChatbot()

        print("Chatbot loaded successfully.")

        question = (
            "My tomato leaf was detected with late blight. "
            "What should I do now?"
        )

        disease_result = {
            "success": True,
            "crop": "Tomato",
            "disease": "Late Blight",
            "status": "diseased",
            "confidence": 91.0,
            "is_reliable": True,
            "risk_level": "High",
            "description": (
                "Late blight can cause dark lesions and "
                "spread quickly in wet conditions."
            ),
            "treatment": [
                "Remove infected leaves and plants.",
                "Avoid overhead irrigation.",
                "Consult an agricultural expert before fungicide use.",
            ],
            "prevention": [
                "Improve spacing and airflow.",
                "Avoid prolonged leaf wetness.",
                "Monitor crops during humid weather.",
            ],
        }

        result = chatbot.ask_with_project_context(
            user_message=question,
            disease_result=disease_result,
        )

        print("\nQuestion:")
        print(question)

        print("\nAgriMind AI response:")

        if result["success"]:
            print(result["answer"])
            print("\nModel:", result["model"])
        else:
            print("Chatbot failed.")
            print("Error:", result["error"])

    except Exception as error:
        print(f"\nChatbot test failed: {error}")


if __name__ == "__main__":
    main()