import os

from dotenv import load_dotenv
from google import genai


def main() -> None:
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("GEMINI_API_KEY was not found in the .env file.")
        return

    client = genai.Client(api_key=api_key)

    print("Models available to your Gemini API key:\n")

    try:
        found_models = 0

        for model in client.models.list():
            model_name = getattr(model, "name", "Unknown")
            supported_actions = getattr(
                model,
                "supported_actions",
                [],
            )

            if (
                "generateContent" in supported_actions
                or "generate_content" in supported_actions
            ):
                print(model_name)
                found_models += 1

        if found_models == 0:
            print(
                "No text-generation models were detected "
                "with the current filter."
            )

    except Exception as error:
        print("Could not retrieve the model list.")
        print("Error:", error)


if __name__ == "__main__":
    main()