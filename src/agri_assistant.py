from typing import Any

from src.ai_chatbot import AgriMindChatbot
from src.context_builder import AgricultureContextBuilder


class AgriAssistant:
    """
    Central orchestration service for AgriMind AI.

    It combines results from:
    - Crop recommendation
    - Weather service
    - Weather analysis
    - Plant disease detection
    - Gemini chatbot
    """

    def __init__(self) -> None:
        self.chatbot = AgriMindChatbot()

    def ask_general_question(
        self,
        question: str,
    ) -> dict[str, Any]:
        """
        Ask a general agriculture question without backend context.
        """

        if not question or not question.strip():
            return {
                "success": False,
                "error": "Question cannot be empty.",
                "answer": "Please enter an agriculture question.",
            }

        return self.chatbot.ask(
            user_message=question.strip()
        )

    def generate_integrated_advice(
        self,
        question: str,
        crop_result: dict[str, Any] | None = None,
        weather_result: dict[str, Any] | None = None,
        weather_analysis: dict[str, Any] | None = None,
        disease_result: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Generate intelligent farming advice using available backend results.
        """

        if not question or not question.strip():
            return {
                "success": False,
                "error": "Question cannot be empty.",
                "answer": "Please enter a question.",
            }

        context = AgricultureContextBuilder.build_complete_context(
            crop_result=crop_result,
            weather_result=weather_result,
            weather_analysis=weather_analysis,
            disease_result=disease_result,
        )

        response = self.chatbot.ask(
            user_message=question.strip(),
            context=context,
        )

        response["context_available"] = bool(context.strip())

        return response

    def explain_crop_recommendation(
        self,
        crop_result: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Ask Gemini to explain a crop recommendation result.
        """

        return self.generate_integrated_advice(
            question=(
                "Explain why this crop may be suitable and give practical "
                "farming precautions."
            ),
            crop_result=crop_result,
        )

    def explain_weather(
        self,
        weather_result: dict[str, Any],
        weather_analysis: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Ask Gemini to explain current weather and farming risks.
        """

        return self.generate_integrated_advice(
            question=(
                "Explain the current weather conditions and tell the farmer "
                "what actions should be taken today."
            ),
            weather_result=weather_result,
            weather_analysis=weather_analysis,
        )

    def explain_disease_prediction(
        self,
        disease_result: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Ask Gemini to explain a plant-disease prediction.
        """

        return self.generate_integrated_advice(
            question=(
                "Explain this plant disease result in simple language and "
                "give safe treatment and prevention steps."
            ),
            disease_result=disease_result,
        )

    @staticmethod
    def create_summary(
        crop_result: dict[str, Any] | None = None,
        weather_result: dict[str, Any] | None = None,
        weather_analysis: dict[str, Any] | None = None,
        disease_result: dict[str, Any] | None = None,
    ) -> str:
        """
        Create a readable summary without making a Gemini API request.
        """

        context = AgricultureContextBuilder.build_complete_context(
            crop_result=crop_result,
            weather_result=weather_result,
            weather_analysis=weather_analysis,
            disease_result=disease_result,
        )

        if not context.strip():
            return "No AgriMind AI analysis results are currently available."

        return context