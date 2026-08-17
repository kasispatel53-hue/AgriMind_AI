from src.weather_service import WeatherService


weather = WeatherService()

# Ahmedabad coordinates
result = weather.get_current_weather(
    latitude=23.0225,
    longitude=72.5714
)

print(result)