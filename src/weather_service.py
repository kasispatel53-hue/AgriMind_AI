from typing import Any

import requests


class WeatherService:
    """Retrieve current weather and a 5-day forecast from Open-Meteo."""

    BASE_URL = "https://api.open-meteo.com/v1/forecast"

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
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snowfall",
        73: "Moderate snowfall",
        75: "Heavy snowfall",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Heavy rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail",
    }

    def __init__(self, timeout: int = 20) -> None:
        self.timeout = timeout

    def get_weather_description(
        self,
        weather_code: int | None,
    ) -> str:
        if weather_code is None:
            return "Unknown conditions"

        try:
            code = int(weather_code)
        except (TypeError, ValueError):
            return "Unknown conditions"

        return self.WEATHER_CODES.get(
            code,
            "Unknown conditions",
        )

    @staticmethod
    def _safe_value(
        values: list[Any] | None,
        index: int,
        default: Any = None,
    ) -> Any:
        if not values:
            return default

        if index >= len(values):
            return default

        value = values[index]

        if value is None:
            return default

        return value

    def get_current_weather(
        self,
        latitude: float,
        longitude: float,
    ) -> dict[str, Any]:
        try:
            latitude = float(latitude)
            longitude = float(longitude)

        except (TypeError, ValueError):
            return {
                "success": False,
                "error": "Latitude and longitude must be valid numbers.",
            }

        if not -90 <= latitude <= 90:
            return {
                "success": False,
                "error": "Latitude must be between -90 and 90.",
            }

        if not -180 <= longitude <= 180:
            return {
                "success": False,
                "error": "Longitude must be between -180 and 180.",
            }

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": ",".join(
                [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "apparent_temperature",
                    "precipitation",
                    "rain",
                    "weather_code",
                    "wind_speed_10m",
                    "wind_direction_10m",
                ]
            ),
            "daily": ",".join(
                [
                    "weather_code",
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "apparent_temperature_max",
                    "apparent_temperature_min",
                    "precipitation_sum",
                    "rain_sum",
                    "precipitation_probability_max",
                    "wind_speed_10m_max",
                    "sunrise",
                    "sunset",
                ]
            ),
            "timezone": "auto",
            "forecast_days": 5,
        }

        try:
            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=self.timeout,
            )

            response.raise_for_status()
            data = response.json()

        except requests.Timeout:
            return {
                "success": False,
                "error": "The weather service took too long to respond.",
            }

        except requests.ConnectionError:
            return {
                "success": False,
                "error": "Could not connect to the weather service.",
            }

        except requests.HTTPError as error:
            api_error = ""

            try:
                api_error = response.json().get("reason", "")
            except Exception:
                pass

            return {
                "success": False,
                "error": api_error or f"Weather API error: {error}",
            }

        except requests.RequestException as error:
            return {
                "success": False,
                "error": f"Weather request failed: {error}",
            }

        except ValueError:
            return {
                "success": False,
                "error": "The weather service returned invalid data.",
            }

        current = data.get("current") or {}
        current_units = data.get("current_units") or {}
        daily = data.get("daily") or {}

        forecast_dates = daily.get("time") or []
        forecast: list[dict[str, Any]] = []

        for index, forecast_date in enumerate(forecast_dates):
            weather_code = self._safe_value(
                daily.get("weather_code"),
                index,
            )

            forecast.append(
                {
                    "date": forecast_date,
                    "weather_code": weather_code,
                    "weather_description": (
                        self.get_weather_description(weather_code)
                    ),
                    "temperature_max": self._safe_value(
                        daily.get("temperature_2m_max"),
                        index,
                        0.0,
                    ),
                    "temperature_min": self._safe_value(
                        daily.get("temperature_2m_min"),
                        index,
                        0.0,
                    ),
                    "apparent_temperature_max": self._safe_value(
                        daily.get("apparent_temperature_max"),
                        index,
                        0.0,
                    ),
                    "apparent_temperature_min": self._safe_value(
                        daily.get("apparent_temperature_min"),
                        index,
                        0.0,
                    ),
                    "precipitation_sum": self._safe_value(
                        daily.get("precipitation_sum"),
                        index,
                        0.0,
                    ),
                    "rainfall": self._safe_value(
                        daily.get("rain_sum"),
                        index,
                        0.0,
                    ),
                    "rain_probability": self._safe_value(
                        daily.get(
                            "precipitation_probability_max"
                        ),
                        index,
                        0,
                    ),
                    "wind_speed_max": self._safe_value(
                        daily.get("wind_speed_10m_max"),
                        index,
                        0.0,
                    ),
                    "sunrise": self._safe_value(
                        daily.get("sunrise"),
                        index,
                    ),
                    "sunset": self._safe_value(
                        daily.get("sunset"),
                        index,
                    ),
                }
            )

        today = forecast[0] if forecast else {}

        current_weather_code = current.get("weather_code")

        return {
            "success": True,
            "latitude": data.get("latitude", latitude),
            "longitude": data.get("longitude", longitude),
            "timezone": data.get("timezone"),
            "time": current.get("time"),
            "temperature": current.get("temperature_2m"),
            "temperature_unit": current_units.get(
                "temperature_2m",
                "°C",
            ),
            "apparent_temperature": current.get(
                "apparent_temperature"
            ),
            "humidity": current.get(
                "relative_humidity_2m"
            ),
            "rainfall": float(
                current.get("rain") or 0.0
            ),
            "precipitation": float(
                current.get("precipitation") or 0.0
            ),
            "wind_speed": current.get("wind_speed_10m"),
            "wind_direction": current.get(
                "wind_direction_10m"
            ),
            "weather_code": current_weather_code,
            "weather_description": (
                self.get_weather_description(
                    current_weather_code
                )
            ),
            "today_rainfall": float(
                today.get("rainfall") or 0.0
            ),
            "today_precipitation": float(
                today.get("precipitation_sum") or 0.0
            ),
            "today_rain_probability": int(
                today.get("rain_probability") or 0
            ),
            "forecast": forecast,
        }


if __name__ == "__main__":
    service = WeatherService()

    result = service.get_current_weather(
        latitude=23.0225,
        longitude=72.5714,
    )

    print(result)