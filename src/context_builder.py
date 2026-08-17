from typing import Any


class AgricultureContextBuilder:
    """Build chatbot context from AgriMind AI backend results."""

    @staticmethod
    def build_crop_context(
        crop_result: dict[str, Any] | None,
    ) -> str:
        if not crop_result or not crop_result.get("success", False):
            return ""

        crop = (
            crop_result.get("recommended_crop")
            or crop_result.get("crop")
            or crop_result.get("prediction")
            or "Unknown"
        )

        confidence = crop_result.get("confidence")

        lines = [
            "Crop recommendation result:",
            f"- Recommended crop: {crop}",
        ]

        if confidence is not None:
            lines.append(f"- Confidence: {confidence}%")

        return "\n".join(lines)

    @staticmethod
    def build_weather_context(
        weather_result: dict[str, Any] | None,
        weather_analysis: dict[str, Any] | None = None,
    ) -> str:
        if not weather_result or not weather_result.get("success", False):
            return ""

        lines = [
            "Current weather data from Open-Meteo:",
            f"- Observation time: {weather_result.get('time')}",
            f"- Temperature: {weather_result.get('temperature')} °C",
            f"- Humidity: {weather_result.get('humidity')}%",
            f"- Rainfall: {weather_result.get('rainfall')} mm",
            f"- Wind speed: {weather_result.get('wind_speed')} km/h",
            f"- Weather code: {weather_result.get('weather_code')}",
        ]

        if weather_analysis:
            lines.append("")
            lines.append("AgriMind weather analysis:")

            summary = weather_analysis.get("summary")
            risk_score = weather_analysis.get("risk_score")
            risk_level = weather_analysis.get("risk_level")
            advice = (
                weather_analysis.get("advice")
                or weather_analysis.get("farmer_advice")
            )

            if summary:
                lines.append(f"- Summary: {summary}")

            if risk_score is not None:
                lines.append(f"- Risk score: {risk_score}")

            if risk_level:
                lines.append(f"- Risk level: {risk_level}")

            if advice:
                if isinstance(advice, list):
                    lines.append("- Farmer advice:")
                    lines.extend(
                        f"  - {item}"
                        for item in advice
                    )
                else:
                    lines.append(f"- Farmer advice: {advice}")

        return "\n".join(lines)

    @staticmethod
    def build_disease_context(
        disease_result: dict[str, Any] | None,
    ) -> str:
        if not disease_result or not disease_result.get("success", False):
            return ""

        lines = [
            "Plant disease prediction:",
            f"- Crop: {disease_result.get('crop')}",
            f"- Disease: {disease_result.get('disease')}",
            f"- Status: {disease_result.get('status')}",
            f"- Confidence: {disease_result.get('confidence')}%",
            f"- Reliable prediction: {disease_result.get('is_reliable')}",
            f"- Risk level: {disease_result.get('risk_level')}",
        ]

        description = disease_result.get("description")

        if description:
            lines.append(f"- Description: {description}")

        treatment = disease_result.get("treatment", [])

        if treatment:
            lines.append("- Treatment:")
            lines.extend(
                f"  - {item}"
                for item in treatment
            )

        prevention = disease_result.get("prevention", [])

        if prevention:
            lines.append("- Prevention:")
            lines.extend(
                f"  - {item}"
                for item in prevention
            )

        return "\n".join(lines)

    @classmethod
    def build_complete_context(
        cls,
        crop_result: dict[str, Any] | None = None,
        weather_result: dict[str, Any] | None = None,
        weather_analysis: dict[str, Any] | None = None,
        disease_result: dict[str, Any] | None = None,
    ) -> str:
        sections = [
            cls.build_crop_context(crop_result),
            cls.build_weather_context(
                weather_result,
                weather_analysis,
            ),
            cls.build_disease_context(disease_result),
        ]

        return "\n\n".join(
            section
            for section in sections
            if section.strip()
        )