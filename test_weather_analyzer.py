from src.weather_service import WeatherService
from src.weather_analyzer import WeatherAnalyzer


def main():
    weather_service = WeatherService()
    weather_analyzer = WeatherAnalyzer()

    weather_data = weather_service.get_current_weather(
        latitude=23.0225,
        longitude=72.5714,
    )

    analysis = weather_analyzer.analyze(weather_data)

    print("\nWeather analysis")
    print("----------------")

    if not analysis["success"]:
        print("Error:", analysis["error"])
        return

    print("Summary:", analysis["summary"])
    print("Risk level:", analysis["risk_level"])
    print("Risk score:", analysis["risk_score"])

    print("\nFarmer advice:")

    for number, advice in enumerate(
        analysis["advice"],
        start=1,
    ):
        print(f"{number}. {advice}")


if __name__ == "__main__":
    main()