import html
from typing import Any

import pandas as pd
import requests
import streamlit as st
from PIL import Image

from src.agri_assistant import AgriAssistant
from src.crop_recommender import CropRecommender
from src.database_manager import DatabaseManager
from src.disease_detector import DiseaseDetector
from src.weather_analyzer import WeatherAnalyzer
from src.weather_service import WeatherService


st.set_page_config(
    page_title="AgriMind AI",
    layout="wide",
    initial_sidebar_state="expanded",
)


DEFAULT_STATE = {
    "current_page": "Dashboard",
    "latest_crop": None,
    "latest_crop_inputs": None,
    "latest_disease": None,
    "latest_weather": None,
    "latest_weather_analysis": None,
    "latest_weather_location": None,
    "chat_messages": [],
    "activity": [],
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


@st.cache_resource
def load_crop_recommender() -> CropRecommender:
    return CropRecommender()


@st.cache_resource
def load_disease_detector() -> DiseaseDetector:
    return DiseaseDetector()


@st.cache_resource
def load_weather_service() -> WeatherService:
    return WeatherService()


@st.cache_resource
def load_weather_analyzer() -> WeatherAnalyzer:
    return WeatherAnalyzer()


@st.cache_resource
def load_agri_assistant() -> AgriAssistant:
    return AgriAssistant()


@st.cache_resource
def load_database() -> DatabaseManager:
    return DatabaseManager()


def safe_load(loader):
    try:
        return loader(), None
    except Exception as error:
        return None, str(error)


crop_recommender, crop_backend_error = safe_load(load_crop_recommender)
disease_detector, disease_backend_error = safe_load(load_disease_detector)
weather_service, weather_backend_error = safe_load(load_weather_service)
weather_analyzer, weather_analyzer_error = safe_load(load_weather_analyzer)
agri_assistant, assistant_backend_error = safe_load(load_agri_assistant)
database_manager, database_backend_error = safe_load(load_database)


def add_activity(message: str) -> None:
    st.session_state.activity.insert(0, message)
    st.session_state.activity = st.session_state.activity[:12]


def backend_status(error: str | None) -> str:
    return "Online" if error is None else "Unavailable"


def geocode_city(city: str) -> dict[str, Any]:
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": city.strip(),
        "count": 1,
        "language": "en",
        "format": "json",
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        results = response.json().get("results") or []

        if not results:
            return {
                "success": False,
                "error": f"No location was found for '{city}'.",
            }

        result = results[0]
        return {
            "success": True,
            "name": result.get("name", city),
            "admin1": result.get("admin1", ""),
            "country": result.get("country", ""),
            "latitude": float(result["latitude"]),
            "longitude": float(result["longitude"]),
        }
    except Exception as error:
        return {"success": False, "error": str(error)}


def render_hero(label: str, title: str, description: str) -> None:
    st.markdown(
        f"""
<div class="hero-container">
    <div class="hero-label">{html.escape(label)}</div>
    <div class="hero-title">{html.escape(title)}</div>
    <div class="hero-description">{html.escape(description)}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_result_card(label: str, value: str, description: str) -> None:
    st.markdown(
        f"""
<div class="result-box">
    <div class="result-label">{html.escape(label)}</div>
    <div class="result-value">{html.escape(str(value))}</div>
    <div class="result-description">{html.escape(description)}</div>
</div>
""",
        unsafe_allow_html=True,
    )


st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* { font-family: "Inter", sans-serif; box-sizing: border-box; }

.stApp {
    background:
        radial-gradient(circle at 10% 10%, rgba(23, 211, 255, 0.07), transparent 25%),
        radial-gradient(circle at 90% 90%, rgba(55, 243, 161, 0.04), transparent 28%),
        #060b18;
    color: #ffffff;
}

.block-container { max-width: 1500px; padding-top: 1.7rem; padding-bottom: 3rem; }
header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer, div[data-testid="stToolbar"] { visibility: hidden; }
section[data-testid="stSidebar"] { background: #070d1c; border-right: 1px solid rgba(148, 163, 184, 0.12); }
section[data-testid="stSidebar"] > div { padding-top: 1.2rem; }

.brand-container { padding: 0.6rem 0.3rem 1.4rem 0.3rem; }
.brand-title { color: #ffffff; font-size: 1.45rem; font-weight: 700; letter-spacing: -0.03em; }
.brand-subtitle { color: #64748b; font-size: 0.72rem; letter-spacing: 0.13em; text-transform: uppercase; margin-top: 0.3rem; }

.system-box {
    background: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(55, 243, 161, 0.20);
    border-radius: 14px;
    padding: 0.85rem 0.9rem;
    margin-top: 1.4rem;
}
.system-status { color: #cbd5e1; font-size: 0.78rem; }
.status-indicator {
    display: inline-block; width: 7px; height: 7px; border-radius: 50%;
    background: #37f3a1; box-shadow: 0 0 12px rgba(55, 243, 161, 0.9);
    margin-right: 0.55rem;
}

.top-header {
    display: flex; align-items: center; justify-content: space-between;
    background: rgba(15, 24, 39, 0.70);
    border: 1px solid rgba(148, 163, 184, 0.12);
    border-radius: 18px; padding: 1rem 1.25rem; margin-bottom: 1.3rem;
    backdrop-filter: blur(18px);
}
.top-header-title { color: #f8fafc; font-size: 0.94rem; font-weight: 600; }
.top-header-status { color: #37f3a1; font-size: 0.74rem; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; }

.hero-container {
    background: linear-gradient(135deg, rgba(16, 24, 39, 0.95), rgba(10, 18, 34, 0.88));
    border: 1px solid rgba(148, 163, 184, 0.13);
    border-radius: 24px; padding: 2rem 2.1rem;
    box-shadow: 0 20px 55px rgba(0, 0, 0, 0.26);
    margin-bottom: 1.4rem;
}
.hero-label {
    display: inline-block; color: #8beaff; background: rgba(25, 211, 255, 0.07);
    border: 1px solid rgba(25, 211, 255, 0.18); border-radius: 999px;
    padding: 0.38rem 0.7rem; font-size: 0.68rem; font-weight: 600;
    letter-spacing: 0.1em; text-transform: uppercase;
}
.hero-title { color: #ffffff; font-size: clamp(2.2rem, 4vw, 3.8rem); line-height: 1.05; font-weight: 700; letter-spacing: -0.055em; margin-top: 1rem; }
.hero-description { color: #94a3b8; max-width: 760px; font-size: 0.96rem; line-height: 1.75; margin-top: 0.8rem; }

.section-title { color: #f8fafc; font-size: 1.08rem; font-weight: 600; margin-top: 1.6rem; margin-bottom: 0.2rem; }
.section-description { color: #64748b; font-size: 0.78rem; margin-bottom: 1rem; }

.module-card, .content-panel, .result-box {
    background: linear-gradient(145deg, rgba(15, 24, 39, 0.86), rgba(9, 16, 31, 0.82));
    border: 1px solid rgba(148, 163, 184, 0.12);
    border-radius: 19px; box-shadow: 0 16px 35px rgba(0, 0, 0, 0.20);
}
.module-card { padding: 1.2rem; min-height: 150px; transition: 0.25s ease; }
.module-card:hover { transform: translateY(-4px); border-color: rgba(25, 211, 255, 0.28); }
.module-name, .result-label { color: #94a3b8; font-size: 0.71rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; }
.module-value, .result-value { color: #ffffff; font-size: 1.55rem; font-weight: 700; margin-top: 1rem; }
.module-description, .result-description { color: #64748b; font-size: 0.76rem; line-height: 1.5; margin-top: 0.45rem; }
.content-panel, .result-box { padding: 1.3rem; margin-bottom: 1rem; }
.result-box { border-color: rgba(55, 243, 161, 0.20); }
.panel-title { color: #f8fafc; font-size: 0.95rem; font-weight: 600; }
.panel-description { color: #64748b; font-size: 0.75rem; margin-top: 0.35rem; }
.placeholder-line { border: 1px dashed rgba(148, 163, 184, 0.18); border-radius: 14px; color: #64748b; text-align: center; padding: 2.2rem 1rem; margin-top: 1rem; font-size: 0.8rem; }

.stButton > button, .stFormSubmitButton > button {
    width: 100%; min-height: 44px; background: rgba(15, 24, 39, 0.78);
    border: 1px solid rgba(148, 163, 184, 0.13); color: #cbd5e1;
    border-radius: 12px; font-size: 0.82rem; font-weight: 500; transition: 0.2s ease;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    color: #ffffff; border-color: rgba(25, 211, 255, 0.35); background: rgba(25, 211, 255, 0.07);
}
.stTextInput input, .stNumberInput input, .stTextArea textarea {
    background: rgba(7, 13, 28, 0.92); border: 1px solid rgba(148, 163, 184, 0.14);
    border-radius: 12px; color: #ffffff;
}
div[data-testid="stFileUploader"] {
    background: rgba(7, 13, 28, 0.75); border: 1px dashed rgba(25, 211, 255, 0.26);
    border-radius: 16px; padding: 0.7rem;
}
</style>
""",
    unsafe_allow_html=True,
)


navigation_items = [
    "Dashboard",
    "Crop Recommendation",
    "Disease Detection",
    "Weather Intelligence",
    "AI Agronomist",
    "Analytics",
    "History",
    "About",
]

with st.sidebar:
    st.markdown(
        """
<div class="brand-container">
    <div class="brand-title">AgriMind AI</div>
    <div class="brand-subtitle">Agriculture Intelligence</div>
</div>
""",
        unsafe_allow_html=True,
    )

    for item in navigation_items:
        if st.button(item, key=f"nav_{item}", use_container_width=True):
            st.session_state.current_page = item
            st.rerun()

    st.markdown(
        """
<div class="system-box">
    <div class="system-status">
        <span class="status-indicator"></span>
        Connected backend modules
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

current_page = st.session_state.current_page

st.markdown(
    f"""
<div class="top-header">
    <div class="top-header-title">{html.escape(current_page)}</div>
    <div class="top-header-status">System Online</div>
</div>
""",
    unsafe_allow_html=True,
)


def render_dashboard() -> None:
    render_hero(
        "Smart Agriculture Intelligence Platform",
        "AgriMind AI",
        "Crop recommendation, plant disease detection, live weather intelligence, and AI-powered agricultural support in one platform.",
    )

    st.markdown('<div class="section-title">Core Intelligence Modules</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-description">Live backend status and latest session results.</div>', unsafe_allow_html=True)

    crop_value = (
        st.session_state.latest_crop.get("crop", "Ready").title()
        if st.session_state.latest_crop
        else backend_status(crop_backend_error)
    )
    disease_value = (
        st.session_state.latest_disease.get("disease", "Ready")
        if st.session_state.latest_disease
        else backend_status(disease_backend_error)
    )
    weather_value = (
        f'{st.session_state.latest_weather.get("temperature")} °C'
        if st.session_state.latest_weather
        else backend_status(weather_backend_error)
    )
    ai_value = backend_status(assistant_backend_error)

    cards = [
        ("Crop Recommendation", crop_value, "Soil and climate based crop prediction."),
        ("Disease Detection", disease_value, "Leaf image disease recognition and guidance."),
        ("Weather Intelligence", weather_value, "Current conditions and farming risk analysis."),
        ("AI Agronomist", ai_value, "Gemini-powered agriculture assistance."),
    ]

    columns = st.columns(4)
    for column, (name, value, description) in zip(columns, cards):
        with column:
            st.markdown(
                f"""
<div class="module-card">
    <div class="module-name">{html.escape(name)}</div>
    <div class="module-value">{html.escape(str(value))}</div>
    <div class="module-description">{html.escape(description)}</div>
</div>
""",
                unsafe_allow_html=True,
            )

    st.markdown('<div class="section-title">Latest Intelligence</div>', unsafe_allow_html=True)
    left, right = st.columns([1.2, 1])

    with left:
        st.markdown(
            """
<div class="content-panel">
    <div class="panel-title">Current Session Results</div>
    <div class="panel-description">The newest crop, disease, and weather outputs.</div>
</div>
""",
            unsafe_allow_html=True,
        )

        if st.session_state.latest_crop:
            result = st.session_state.latest_crop
            st.write(f"**Crop:** {result.get('crop', 'Unknown').title()} ({result.get('confidence', 'N/A')}% confidence)")

        if st.session_state.latest_disease:
            result = st.session_state.latest_disease
            st.write(f"**Disease:** {result.get('crop', 'Unknown')} — {result.get('disease', 'Unknown')} ({result.get('confidence', 'N/A')}% confidence)")

        if st.session_state.latest_weather:
            weather = st.session_state.latest_weather
            analysis = st.session_state.latest_weather_analysis or {}
            st.write(f"**Weather:** {weather.get('temperature')} °C, {weather.get('humidity')}% humidity, risk {analysis.get('risk_level', 'Unknown')}")

        if not any([st.session_state.latest_crop, st.session_state.latest_disease, st.session_state.latest_weather]):
            st.markdown('<div class="placeholder-line">No analysis has been run in this session.</div>', unsafe_allow_html=True)

    with right:
        st.markdown(
            """
<div class="content-panel">
    <div class="panel-title">Recent Activity</div>
    <div class="panel-description">Latest actions completed in this session.</div>
</div>
""",
            unsafe_allow_html=True,
        )

        if st.session_state.activity:
            for activity in st.session_state.activity[:6]:
                st.write(f"• {activity}")
        else:
            st.markdown('<div class="placeholder-line">No activity recorded yet.</div>', unsafe_allow_html=True)


def render_crop_page() -> None:
    render_hero(
        "Soil and Climate Intelligence",
        "Crop Recommendation",
        "Enter soil nutrients and environmental values to identify a suitable crop.",
    )

    if crop_backend_error:
        st.error("Crop backend could not be loaded.")
        st.code(crop_backend_error)
        return

    with st.form("crop_recommendation_form"):
        row1 = st.columns(3)
        nitrogen = row1[0].number_input("Nitrogen (N)", 0.0, 300.0, 90.0, 1.0)
        phosphorus = row1[1].number_input("Phosphorus (P)", 0.0, 300.0, 42.0, 1.0)
        potassium = row1[2].number_input("Potassium (K)", 0.0, 300.0, 43.0, 1.0)

        row2 = st.columns(3)
        temperature = row2[0].number_input("Temperature (°C)", -20.0, 70.0, 25.0, 0.1)
        humidity = row2[1].number_input("Humidity (%)", 0.0, 100.0, 80.0, 0.1)
        rainfall = row2[2].number_input("Rainfall (mm)", 0.0, 1000.0, 200.0, 1.0)

        soil_ph = st.number_input("Soil pH", 0.0, 14.0, 6.5, 0.1)
        submitted = st.form_submit_button("Generate Recommendation", use_container_width=True)

    if submitted:
        with st.spinner("Analyzing soil and climate values..."):
            result = crop_recommender.recommend_crop(
                nitrogen=nitrogen,
                phosphorus=phosphorus,
                potassium=potassium,
                temperature=temperature,
                humidity=humidity,
                soil_ph=soil_ph,
                rainfall=rainfall,
            )

        if not result.get("success"):
            for error in result.get("errors", ["Prediction failed."]):
                st.error(error)
            return

        inputs = {
            "nitrogen": nitrogen,
            "phosphorus": phosphorus,
            "potassium": potassium,
            "temperature": temperature,
            "humidity": humidity,
            "ph": soil_ph,
            "rainfall": rainfall,
        }

        st.session_state.latest_crop = result
        st.session_state.latest_crop_inputs = inputs
        add_activity(f"Crop recommendation generated: {result['crop'].title()}")

        if database_manager:
            try:
                database_manager.save_crop_prediction(input_data=inputs, result=result)
            except Exception as error:
                st.warning(f"Prediction worked, but history save failed: {error}")

        st.success("Crop recommendation completed.")
        col1, col2 = st.columns(2)
        with col1:
            render_result_card("Recommended Crop", result.get("crop", "Unknown").title(), "Best matching crop for the entered soil and climate values.")
        with col2:
            confidence = result.get("confidence")
            render_result_card("Model Confidence", f"{confidence:.2f}%" if confidence is not None else "Unavailable", "The model's certainty for this recommendation.")

        if agri_assistant and st.button("Generate AI Explanation", use_container_width=True):
            with st.spinner("Generating explanation..."):
                explanation = agri_assistant.explain_crop_recommendation(result)
            if explanation.get("success"):
                st.markdown("### AI Explanation")
                st.write(explanation.get("answer"))
            else:
                st.error(explanation.get("answer") or explanation.get("error"))


def render_disease_page() -> None:
    render_hero(
        "Plant Vision Intelligence",
        "Disease Detection",
        "Upload a clear plant leaf image to identify disease and receive guidance.",
    )

    if disease_backend_error:
        st.error("Disease backend could not be loaded.")
        st.code(disease_backend_error)
        return

    uploaded_file = st.file_uploader("Upload plant leaf image", type=["jpg", "jpeg", "png"])

    if uploaded_file is None:
        st.info("Upload a JPG, JPEG, or PNG leaf image to begin.")
        return

    try:
        image = Image.open(uploaded_file).convert("RGB")
    except Exception as error:
        st.error(f"The image could not be opened: {error}")
        return

    left, right = st.columns([1, 1])
    with left:
        st.image(image, caption="Uploaded leaf image", use_container_width=True)
    with right:
        st.markdown(
            """
<div class="content-panel">
    <div class="panel-title">Image Ready</div>
    <div class="panel-description">Press Detect Disease to run the trained vision model.</div>
</div>
""",
            unsafe_allow_html=True,
        )
        detect_button = st.button("Detect Disease", use_container_width=True)

    if detect_button:
        with st.spinner("Analyzing leaf image..."):
            result = disease_detector.predict(image)

        if not result.get("success"):
            st.error(result.get("error") or result.get("message"))
            return

        st.session_state.latest_disease = result
        add_activity(f"Disease analysis completed: {result.get('crop')} — {result.get('disease')}")

        if database_manager:
            try:
                database_manager.save_disease_prediction(result=result, image_name=uploaded_file.name)
            except Exception as error:
                st.warning(f"Detection worked, but history save failed: {error}")

        st.success(result.get("message", "Disease detection completed."))

        result_cols = st.columns(4)
        result_cols[0].metric("Crop", result.get("crop", "Unknown"))
        result_cols[1].metric("Disease", result.get("disease", "Unknown"))
        result_cols[2].metric("Confidence", f"{result.get('confidence', 0):.2f}%")
        result_cols[3].metric("Risk Level", result.get("risk_level", "Unknown"))

        st.markdown("### Description")
        st.write(result.get("description", "No description available."))

        treatment_col, prevention_col = st.columns(2)
        with treatment_col:
            st.markdown("### Treatment")
            for item in result.get("treatment") or []:
                st.write(f"• {item}")
        with prevention_col:
            st.markdown("### Prevention")
            for item in result.get("prevention") or []:
                st.write(f"• {item}")

        top_predictions = result.get("top_predictions") or []
        if top_predictions:
            st.markdown("### Top Predictions")
            st.dataframe(pd.DataFrame(top_predictions), use_container_width=True, hide_index=True)

        st.warning(result.get("warning", ""))

        if agri_assistant and st.button("Generate AI Disease Explanation", use_container_width=True):
            with st.spinner("Generating explanation..."):
                explanation = agri_assistant.explain_disease_prediction(result)
            if explanation.get("success"):
                st.write(explanation.get("answer"))
            else:
                st.error(explanation.get("answer") or explanation.get("error"))


def render_weather_page() -> None:
    render_hero(
        "Live Environmental Intelligence",
        "Weather Intelligence",
        (
            "Search a city to view current weather, rainfall information, "
            "a five-day forecast, and agriculture-focused risk analysis."
        ),
    )

    if weather_backend_error or weather_analyzer_error:
        st.error("Weather backend could not be loaded.")

        if weather_backend_error:
            st.code(weather_backend_error)

        if weather_analyzer_error:
            st.code(weather_analyzer_error)

        return

    with st.form("weather_form"):
        city = st.text_input(
            "City",
            value="Ahmedabad",
            placeholder="Enter city name",
        )

        submitted = st.form_submit_button(
            "Get Weather Forecast",
            use_container_width=True,
        )

    if not submitted:
        st.info(
            "Enter a city and press Get Weather Forecast."
        )
        return

    if not city.strip():
        st.warning("Please enter a city.")
        return

    with st.spinner(
        "Finding location and retrieving the five-day forecast..."
    ):
        location = geocode_city(city)

        if not location.get("success"):
            st.error(
                location.get(
                    "error",
                    "Location could not be found.",
                )
            )
            return

        weather = weather_service.get_current_weather(
            latitude=location["latitude"],
            longitude=location["longitude"],
        )

        if not weather.get("success"):
            st.error(
                weather.get(
                    "error",
                    "Weather could not be retrieved.",
                )
            )
            return

        analysis = weather_analyzer.analyze(weather)

    st.session_state.latest_weather = weather
    st.session_state.latest_weather_analysis = analysis
    st.session_state.latest_weather_location = location

    location_name = ", ".join(
        part
        for part in [
            location.get("name"),
            location.get("admin1"),
            location.get("country"),
        ]
        if part
    )

    add_activity(
        f"Five-day weather forecast retrieved for {location_name}"
    )

    if database_manager:
        try:
            database_manager.save_weather_history(
                weather_result=weather,
                analysis_result=analysis,
                location=location_name,
                latitude=location["latitude"],
                longitude=location["longitude"],
            )
        except Exception as error:
            st.warning(
                "Weather worked, but history save failed: "
                f"{error}"
            )

    st.success(
        f"Weather forecast retrieved for {location_name}"
    )

    st.markdown("### Current Weather")

    current_columns = st.columns(6)

    temperature = weather.get("temperature")
    humidity = weather.get("humidity")
    rainfall = weather.get("rainfall", 0.0)
    apparent_temperature = weather.get(
        "apparent_temperature"
    )
    wind_speed = weather.get("wind_speed")
    risk_level = analysis.get("risk_level", "Unknown")

    current_columns[0].metric(
        "Temperature",
        (
            f"{temperature:.1f} °C"
            if temperature is not None
            else "Unavailable"
        ),
    )

    current_columns[1].metric(
        "Feels Like",
        (
            f"{apparent_temperature:.1f} °C"
            if apparent_temperature is not None
            else "Unavailable"
        ),
    )

    current_columns[2].metric(
        "Humidity",
        (
            f"{humidity:.0f}%"
            if humidity is not None
            else "Unavailable"
        ),
    )

    current_columns[3].metric(
        "Rain Now",
        f"{float(rainfall or 0):.1f} mm",
    )

    current_columns[4].metric(
        "Wind Speed",
        (
            f"{wind_speed:.1f} km/h"
            if wind_speed is not None
            else "Unavailable"
        ),
    )

    current_columns[5].metric(
        "Risk Level",
        risk_level,
    )

    rain_columns = st.columns(3)

    rain_columns[0].metric(
        "Today's Forecast Rain",
        f"{float(weather.get('today_rainfall', 0) or 0):.1f} mm",
    )

    rain_columns[1].metric(
        "Today's Precipitation",
        (
            f"{float(weather.get('today_precipitation', 0) or 0):.1f} mm"
        ),
    )

    rain_columns[2].metric(
        "Rain Probability",
        (
            f"{int(weather.get('today_rain_probability', 0) or 0)}%"
        ),
    )

    render_result_card(
        "Weather Summary",
        weather.get(
            "weather_description",
            analysis.get(
                "weather_description",
                "Current conditions",
            ),
        ),
        analysis.get(
            "summary",
            "No weather summary is available.",
        ),
    )

    st.markdown("### Five-Day Forecast")

    forecast = weather.get("forecast") or []

    if forecast:
        forecast_table = []

        for day in forecast:
            forecast_table.append(
                {
                    "Date": day.get("date"),
                    "Condition": day.get(
                        "weather_description",
                        "Unknown",
                    ),
                    "Maximum Temperature": (
                        f"{float(day.get('temperature_max', 0) or 0):.1f} °C"
                    ),
                    "Minimum Temperature": (
                        f"{float(day.get('temperature_min', 0) or 0):.1f} °C"
                    ),
                    "Rainfall": (
                        f"{float(day.get('rainfall', 0) or 0):.1f} mm"
                    ),
                    "Rain Probability": (
                        f"{int(day.get('rain_probability', 0) or 0)}%"
                    ),
                    "Maximum Wind Speed": (
                        f"{float(day.get('wind_speed_max', 0) or 0):.1f} km/h"
                    ),
                }
            )

        st.dataframe(
            pd.DataFrame(forecast_table),
            use_container_width=True,
            hide_index=True,
        )

        chart_data = pd.DataFrame(
            {
                "Date": [
                    day.get("date")
                    for day in forecast
                ],
                "Maximum Temperature": [
                    day.get("temperature_max", 0)
                    for day in forecast
                ],
                "Minimum Temperature": [
                    day.get("temperature_min", 0)
                    for day in forecast
                ],
            }
        ).set_index("Date")

        st.markdown("### Temperature Forecast")
        st.line_chart(chart_data)

        rainfall_chart = pd.DataFrame(
            {
                "Date": [
                    day.get("date")
                    for day in forecast
                ],
                "Forecast Rainfall": [
                    day.get("rainfall", 0)
                    for day in forecast
                ],
            }
        ).set_index("Date")

        st.markdown("### Rainfall Forecast")
        st.bar_chart(rainfall_chart)

    else:
        st.info("The five-day forecast is unavailable.")

    st.markdown("### Farming Advice")

    advice_items = analysis.get("advice") or []

    if advice_items:
        for advice in advice_items:
            st.write(f"• {advice}")
    else:
        st.info("No farming advice is available.")

    if agri_assistant and st.button(
        "Generate AI Weather Explanation",
        use_container_width=True,
    ):
        with st.spinner(
            "Generating AI weather explanation..."
        ):
            explanation = agri_assistant.explain_weather(
                weather,
                analysis,
            )

        if explanation.get("success"):
            st.markdown("### AI Weather Explanation")
            st.write(explanation.get("answer"))
        else:
            st.error(
                explanation.get("answer")
                or explanation.get("error")
                or "The explanation could not be generated."
            )

def render_chat_page() -> None:
    render_hero(
        "Gemini-Powered Agriculture Assistant",
        "AI Agronomist",
        "Ask questions about crops, diseases, weather risks, and farm management.",
    )

    if assistant_backend_error:
        st.error("AI assistant could not be loaded.")
        st.code(assistant_backend_error)
        return

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask AgriMind AI")

    if prompt:
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Generating agricultural advice..."):
                response = agri_assistant.generate_integrated_advice(
                    question=prompt,
                    crop_result=st.session_state.latest_crop,
                    weather_result=st.session_state.latest_weather,
                    weather_analysis=st.session_state.latest_weather_analysis,
                    disease_result=st.session_state.latest_disease,
                )
            answer = response.get("answer") or response.get("error") or "No response was generated."
            st.markdown(answer)

        st.session_state.chat_messages.append({"role": "assistant", "content": answer})
        add_activity("AI Agronomist response generated")

        if database_manager and response.get("success"):
            try:
                database_manager.save_chat_message(
                    user_message=prompt,
                    chatbot_result=response,
                    context_used=bool(response.get("context_available")),
                )
            except Exception as error:
                st.warning(f"Chat worked, but history save failed: {error}")


def render_analytics_page() -> None:
    render_hero(
        "Prediction Intelligence",
        "Analytics",
        "Review database totals and recent platform activity.",
    )

    if database_backend_error:
        st.error("Database could not be loaded.")
        st.code(database_backend_error)
        return

    try:
        counts = database_manager.get_record_counts()
    except Exception as error:
        st.error(f"Analytics could not be loaded: {error}")
        return

    cols = st.columns(4)
    cols[0].metric("Crop Predictions", counts.get("crop", 0))
    cols[1].metric("Disease Analyses", counts.get("disease", 0))
    cols[2].metric("Weather Records", counts.get("weather", 0))
    cols[3].metric("AI Conversations", counts.get("chat", 0))

    chart_data = pd.DataFrame(
        {
            "Module": ["Crop", "Disease", "Weather", "Chat"],
            "Records": [
                counts.get("crop", 0),
                counts.get("disease", 0),
                counts.get("weather", 0),
                counts.get("chat", 0),
            ],
        }
    ).set_index("Module")
    st.bar_chart(chart_data)


def render_history_page() -> None:
    render_hero(
        "Saved Intelligence Records",
        "History",
        "Review previous crop, disease, weather, and AI records saved in SQLite.",
    )

    if database_backend_error:
        st.error("Database could not be loaded.")
        st.code(database_backend_error)
        return

    try:
        crop_history = database_manager.get_crop_history(limit=50)
        disease_history = database_manager.get_disease_history(limit=50)
        weather_history = database_manager.get_weather_history(limit=50)
        chat_history = database_manager.get_chat_history(limit=50)
    except Exception as error:
        st.error(f"History could not be loaded: {error}")
        return

    tabs = st.tabs(["Crop", "Disease", "Weather", "AI Chat"])

    with tabs[0]:
        if crop_history:
            st.dataframe(pd.DataFrame(crop_history), use_container_width=True, hide_index=True)
        else:
            st.info("No crop prediction history is available.")

    with tabs[1]:
        if disease_history:
            st.dataframe(pd.DataFrame(disease_history), use_container_width=True, hide_index=True)
        else:
            st.info("No disease prediction history is available.")

    with tabs[2]:
        if weather_history:
            st.dataframe(pd.DataFrame(weather_history), use_container_width=True, hide_index=True)
        else:
            st.info("No weather history is available.")

    with tabs[3]:
        if chat_history:
            st.dataframe(pd.DataFrame(chat_history), use_container_width=True, hide_index=True)
        else:
            st.info("No AI chat history is available.")

def render_about_page() -> None:
    render_hero(
        "Developer & Project",
        "About AgriMind AI",
        (
            "An intelligent agriculture platform combining machine learning, "
            "deep learning, live weather intelligence, and generative AI to "
            "support smarter agricultural decisions."
        ),
    )

    st.markdown(
        """
<div class="content-panel">
    <div class="panel-title">Developed by Kasis Patel</div>
    <div class="panel-description">
        Artificial Intelligence and Machine Learning student at Gujarat University,
        based in Ahmedabad, Gujarat, India.
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    developer_col, project_col = st.columns([1, 1.4])

    with developer_col:
        st.markdown("### Developer Profile")
        st.write("**Name:** Kasis Patel")
        st.write("**Field:** Artificial Intelligence & Machine Learning")
        st.write("**University:** Gujarat University")
        st.write("**Location:** Ahmedabad, Gujarat, India")
        st.write(
            "I am passionate about building practical AI-powered solutions "
            "for agriculture, healthcare, smart cities, automation, and data science."
        )

        st.markdown("### Contact")
        st.write("**Email:** kasispatel53@gmail.com")
        st.markdown(
            "[Open LinkedIn Profile]"
            "(https://www.linkedin.com/in/kasis-patel-6351362b7)"
        )

    with project_col:
        st.markdown("### About the Project")
        st.write(
            "AgriMind AI is an end-to-end Smart Agriculture Assistant created "
            "to bring multiple agricultural intelligence services into one "
            "modern platform. It helps users select suitable crops, identify "
            "plant diseases, understand live weather conditions, and receive "
            "context-aware agricultural guidance."
        )

        st.markdown("### Project Objective")
        st.info(
            "To support better farming decisions through accessible, "
            "data-driven, and AI-powered agricultural assistance."
        )

    st.divider()

    st.markdown("### Core Intelligence Modules")
    feature_columns = st.columns(3)

    features = [
        (
            "Crop Recommendation",
            "Machine-learning prediction using soil nutrients and climate values.",
        ),
        (
            "Disease Detection",
            "Deep-learning analysis of plant leaf images with treatment guidance.",
        ),
        (
            "Weather Intelligence",
            "Live weather retrieval and agriculture-focused risk analysis.",
        ),
        (
            "AI Agronomist",
            "Generative-AI guidance using crop, disease, and weather context.",
        ),
        (
            "Analytics",
            "A summary of prediction and conversation records stored by the platform.",
        ),
        (
            "History",
            "SQLite-based access to previous crop, weather, disease, and chat records.",
        ),
    ]

    for index, (title, description) in enumerate(features):
        with feature_columns[index % 3]:
            st.markdown(
                f"""
<div class="module-card">
    <div class="module-name">{html.escape(title)}</div>
    <div class="module-description" style="margin-top:0.8rem;">
        {html.escape(description)}
    </div>
</div>
""",
                unsafe_allow_html=True,
            )

    st.divider()

    st.markdown("### Technology Stack")
    tech1, tech2, tech3 = st.columns(3)

    with tech1:
        st.markdown(
            """
**Application**
- Python
- Streamlit
- HTML and CSS
- Pandas
"""
        )

    with tech2:
        st.markdown(
            """
**AI and Machine Learning**
- Scikit-learn
- TensorFlow / Keras
- Plant disease vision model
- Weather risk analyzer
"""
        )

    with tech3:
        st.markdown(
            """
**Services and Storage**
- Google Gemini AI
- Open-Meteo API
- SQLite
- Pillow
"""
        )

    st.divider()

    st.markdown("### Future Enhancements")
    st.write(
        "Fertilizer recommendation, irrigation prediction, multilingual support, "
        "voice assistance, satellite and drone data integration, and a mobile application."
    )

    st.caption("© 2026 AgriMind AI | Developed by Kasis Patel")


# =========================================================
# PAGE ROUTING
# =========================================================

if current_page == "Dashboard":
    render_dashboard()

elif current_page == "Crop Recommendation":
    render_crop_page()

elif current_page == "Disease Detection":
    render_disease_page()

elif current_page == "Weather Intelligence":
    render_weather_page()

elif current_page == "AI Agronomist":
    render_chat_page()

elif current_page == "Analytics":
    render_analytics_page()

elif current_page == "History":
    render_history_page()

elif current_page == "About":
    render_about_page()

else:
    st.session_state.current_page = "Dashboard"
    st.rerun()