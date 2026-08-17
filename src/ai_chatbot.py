import os
import time
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import types

from src.context_builder import AgricultureContextBuilder
from src.prompt_templates import (
    AGRIMIND_SYSTEM_PROMPT,
    build_chat_prompt,
)


class AgriMindChatbot:
    """Gemini-powered agriculture chatbot for AgriMind AI."""

    def __init__(
        self,
        model: str | None = None,
    ) -> None:
        load_dotenv()

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY was not found. "
                "Add it to the project .env file."
            )

        self.model = (
            model
            or os.getenv("GEMINI_MODEL")
            or "gemini-2.5-flash"
        )

        self.client = genai.Client(
            api_key=api_key
        )

    def ask(
        self,
        user_message: str,
        context: str | None = None,
    ) -> dict[str, Any]:
        """Send a farming question to Gemini with automatic retries."""

        if not user_message or not user_message.strip():
            return {
                "success": False,
                "answer": "Please enter an agriculture question.",
                "error": "User message cannot be empty.",
            }

        prompt = build_chat_prompt(
            user_message=user_message.strip(),
            context=context,
        )

        maximum_attempts = 3
        last_error = ""

        for attempt in range(1, maximum_attempts + 1):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=AGRIMIND_SYSTEM_PROMPT,
                        temperature=0.3,
                        max_output_tokens=700,
                    ),
                )

                answer = (response.text or "").strip()

                if not answer:
                    raise RuntimeError(
                        "Gemini returned an empty response."
                    )

                return {
                    "success": True,
                    "answer": answer,
                    "model": self.model,
                    "attempts": attempt,
                }

            except Exception as error:
                last_error = str(error)

                temporary_error = any(
                    keyword in last_error.lower()
                    for keyword in [
                        "503",
                        "unavailable",
                        "high demand",
                        "temporarily",
                        "429",
                        "resource_exhausted",
                        "timeout",
                    ]
                )

                if temporary_error and attempt < maximum_attempts:
                    wait_time = attempt * 2

                    print(
                        f"Gemini server is busy. "
                        f"Retrying in {wait_time} seconds "
                        f"({attempt}/{maximum_attempts})..."
                    )

                    time.sleep(wait_time)
                    continue

                break

        return {
            "success": False,
            "answer": (
                "AgriMind AI is temporarily busy. "
                "Please try again after a few moments."
            ),
            "error": last_error,
            "model": self.model,
            "attempts": maximum_attempts,
        }

    def ask_with_project_context(
        self,
        user_message: str,
        crop_result: dict[str, Any] | None = None,
        weather_result: dict[str, Any] | None = None,
        weather_analysis: dict[str, Any] | None = None,
        disease_result: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Ask Gemini using results from AgriMind backend modules."""

        context = AgricultureContextBuilder.build_complete_context(
            crop_result=crop_result,
            weather_result=weather_result,
            weather_analysis=weather_analysis,
            disease_result=disease_result,
        )

        return self.ask(
            user_message=user_message,
            context=context,
        )