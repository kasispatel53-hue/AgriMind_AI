class WeatherAnalyzer:
    """
    Converts raw weather data into practical farming guidance.
    """

    WEATHER_CODES = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snowfall",
        73: "Moderate snowfall",
        75: "Heavy snowfall",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Heavy rain showers",
        95: "Thunderstorm",
        96: "Thunderstorm with hail",
        99: "Severe thunderstorm with hail",
    }

    def get_weather_description(self, weather_code):
        return self.WEATHER_CODES.get(
            weather_code,
            "Unknown weather condition",
        )

    def analyze(self, weather_data):
        if not weather_data.get("success"):
            return {
                "success": False,
                "summary": None,
                "advice": [],
                "risk_level": None,
                "error": weather_data.get(
                    "error",
                    "Weather information is unavailable.",
                ),
            }

        temperature = weather_data["temperature"]
        humidity = weather_data["humidity"]
        rainfall = weather_data["rainfall"]
        wind_speed = weather_data["wind_speed"]
        weather_code = weather_data["weather_code"]

        advice = []
        risk_score = 0

        weather_description = self.get_weather_description(
            weather_code
        )

        # Temperature analysis
        if temperature >= 40:
            advice.append(
                "Extreme heat detected. Irrigate during early morning "
                "or evening and monitor crops for heat stress."
            )
            risk_score += 3

        elif temperature >= 35:
            advice.append(
                "High temperature detected. Check soil moisture and "
                "avoid irrigation during peak afternoon heat."
            )
            risk_score += 2

        elif temperature <= 10:
            advice.append(
                "Low temperature may slow crop growth. Monitor "
                "cold-sensitive crops."
            )
            risk_score += 2

        else:
            advice.append(
                "Temperature is within a generally moderate range."
            )

        # Humidity analysis
        if humidity >= 85:
            advice.append(
                "Very high humidity may increase the risk of fungal "
                "diseases. Inspect leaves regularly."
            )
            risk_score += 3

        elif humidity >= 70:
            advice.append(
                "Humidity is moderately high. Monitor crops for fungal "
                "spots and improve field ventilation where possible."
            )
            risk_score += 1

        elif humidity < 30:
            advice.append(
                "Low humidity may increase water loss from crops. "
                "Check soil moisture."
            )
            risk_score += 2

        # Rainfall analysis
        if rainfall >= 20:
            advice.append(
                "Heavy rainfall detected. Delay irrigation and inspect "
                "the field for waterlogging."
            )
            risk_score += 3

        elif rainfall > 0:
            advice.append(
                "Rainfall is occurring. Reduce or delay irrigation."
            )
            risk_score += 1

        else:
            advice.append(
                "No current rainfall detected. Irrigation should depend "
                "on soil moisture and crop requirements."
            )

        # Wind analysis
        if wind_speed >= 30:
            advice.append(
                "Strong wind detected. Avoid spraying pesticides or "
                "fertilizers because of spray drift."
            )
            risk_score += 3

        elif wind_speed >= 15:
            advice.append(
                "Moderate wind detected. Use caution before spraying."
            )
            risk_score += 1

        else:
            advice.append(
                "Wind speed is generally suitable for normal field work."
            )

        # Weather-code analysis
        if weather_code in [95, 96, 99]:
            advice.append(
                "Thunderstorm conditions detected. Postpone field work "
                "and move to a safe location."
            )
            risk_score += 4

        elif weather_code in [61, 63, 65, 80, 81, 82]:
            advice.append(
                "Rain conditions may affect spraying and harvesting."
            )
            risk_score += 2

        elif weather_code in [45, 48]:
            advice.append(
                "Fog may increase leaf wetness and reduce visibility."
            )
            risk_score += 1

        if risk_score >= 7:
            risk_level = "High"
        elif risk_score >= 3:
            risk_level = "Moderate"
        else:
            risk_level = "Low"

        summary = (
            f"{weather_description}, {temperature}°C, "
            f"{humidity}% humidity, {rainfall} mm rainfall "
            f"and {wind_speed} km/h wind."
        )

        return {
            "success": True,
            "summary": summary,
            "weather_description": weather_description,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "advice": advice,
            "raw_weather": weather_data,
        }