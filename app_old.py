import streamlit as st
import joblib
import numpy as np
from pathlib import Path


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="AgriMind AI",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)


# --------------------------------------------------
# Load trained model
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "crop_recommendation_model.pkl"


@st.cache_resource
def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model file was not found at: {MODEL_PATH}"
        )

    return joblib.load(MODEL_PATH)


try:
    model = load_model()
except Exception as error:
    st.error(f"Unable to load the crop recommendation model: {error}")
    st.stop()


# --------------------------------------------------
# Futuristic custom UI
# --------------------------------------------------

st.markdown(
    """
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
        --background: #05080d;
        --surface: rgba(14, 22, 31, 0.78);
        --surface-light: rgba(22, 34, 46, 0.72);
        --border: rgba(115, 255, 205, 0.16);
        --primary: #65f6bf;
        --primary-dark: #24c98c;
        --text-main: #f1f7f5;
        --text-muted: #8fa7a0;
        --danger: #ff7b88;
    }

    html,
    body,
    [class*="css"] {
        font-family: "Inter", sans-serif;
    }

    .stApp {
        background:
            radial-gradient(
                circle at 10% 10%,
                rgba(33, 210, 147, 0.13),
                transparent 30%
            ),
            radial-gradient(
                circle at 90% 20%,
                rgba(45, 116, 255, 0.12),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #04070b 0%,
                #071018 50%,
                #04080d 100%
            );
        color: var(--text-main);
    }

    .block-container {
        max-width: 1380px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    #MainMenu,
    footer {
        visibility: hidden;
    }

    .brand-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.85rem 1.1rem;
        margin-bottom: 1.5rem;
        border: 1px solid var(--border);
        border-radius: 18px;
        background: rgba(8, 14, 21, 0.68);
        backdrop-filter: blur(18px);
        box-shadow: 0 14px 50px rgba(0, 0, 0, 0.22);
    }

    .brand-name {
        font-family: "Space Grotesk", sans-serif;
        font-size: 1.05rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        color: var(--text-main);
    }

    .system-status {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        color: var(--text-muted);
        font-size: 0.78rem;
        font-weight: 500;
    }

    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--primary);
        box-shadow: 0 0 14px var(--primary);
    }

    .hero-panel {
        position: relative;
        overflow: hidden;
        padding: 3.2rem 3rem;
        margin-bottom: 1.5rem;
        border: 1px solid var(--border);
        border-radius: 28px;
        background:
            linear-gradient(
                145deg,
                rgba(15, 26, 36, 0.92),
                rgba(7, 14, 21, 0.78)
            );
        box-shadow: 0 30px 90px rgba(0, 0, 0, 0.35);
    }

    .hero-panel::before {
        content: "";
        position: absolute;
        width: 380px;
        height: 380px;
        top: -220px;
        right: -80px;
        border-radius: 50%;
        background: rgba(101, 246, 191, 0.13);
        filter: blur(12px);
    }

    .hero-label {
        display: inline-block;
        padding: 0.45rem 0.8rem;
        margin-bottom: 1.2rem;
        border: 1px solid rgba(101, 246, 191, 0.25);
        border-radius: 999px;
        color: var(--primary);
        background: rgba(101, 246, 191, 0.07);
        font-size: 0.73rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }

    .hero-title {
        max-width: 860px;
        margin: 0;
        font-family: "Space Grotesk", sans-serif;
        font-size: clamp(2.5rem, 5vw, 5.1rem);
        line-height: 0.98;
        letter-spacing: -0.055em;
        color: var(--text-main);
    }

    .gradient-text {
        background: linear-gradient(
            90deg,
            #f2fff9,
            #65f6bf 55%,
            #71b7ff
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-description {
        max-width: 720px;
        margin-top: 1.35rem;
        margin-bottom: 0;
        color: var(--text-muted);
        font-size: 1rem;
        line-height: 1.75;
    }

    .section-heading {
        margin-top: 1rem;
        margin-bottom: 0.25rem;
        font-family: "Space Grotesk", sans-serif;
        font-size: 1.55rem;
        font-weight: 600;
        color: var(--text-main);
    }

    .section-description {
        margin-top: 0;
        margin-bottom: 1.1rem;
        color: var(--text-muted);
        font-size: 0.9rem;
    }

    div[data-testid="stForm"] {
        padding: 1.5rem;
        border: 1px solid var(--border);
        border-radius: 24px;
        background: rgba(10, 17, 25, 0.78);
        backdrop-filter: blur(18px);
        box-shadow: 0 20px 65px rgba(0, 0, 0, 0.25);
    }

    div[data-testid="stNumberInput"] label {
        color: #cbdad5;
        font-size: 0.82rem;
        font-weight: 500;
    }

    div[data-testid="stNumberInput"] input {
        height: 3rem;
        border: 1px solid rgba(120, 170, 155, 0.18);
        border-radius: 12px;
        background: rgba(6, 12, 18, 0.88);
        color: var(--text-main);
        font-size: 0.95rem;
    }

    div[data-testid="stNumberInput"] input:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 1px var(--primary);
    }

    div[data-testid="stFormSubmitButton"] button {
        width: 100%;
        min-height: 3.4rem;
        margin-top: 0.8rem;
        border: 1px solid rgba(101, 246, 191, 0.5);
        border-radius: 14px;
        background:
            linear-gradient(
                100deg,
                #49e6ae,
                #67f5c2
            );
        color: #03110c;
        font-family: "Space Grotesk", sans-serif;
        font-weight: 700;
        letter-spacing: 0.02em;
        transition:
            transform 0.2s ease,
            box-shadow 0.2s ease;
    }

    div[data-testid="stFormSubmitButton"] button:hover {
        transform: translateY(-2px);
        border-color: #8dffd7;
        box-shadow: 0 12px 32px rgba(67, 230, 170, 0.2);
    }

    .parameter-card {
        min-height: 110px;
        padding: 1.15rem;
        border: 1px solid var(--border);
        border-radius: 18px;
        background: rgba(13, 22, 31, 0.63);
    }

    .parameter-title {
        color: var(--text-main);
        font-family: "Space Grotesk", sans-serif;
        font-size: 0.95rem;
        font-weight: 600;
    }

    .parameter-text {
        margin-top: 0.45rem;
        color: var(--text-muted);
        font-size: 0.78rem;
        line-height: 1.55;
    }

    .result-card {
        position: relative;
        overflow: hidden;
        margin-top: 1.5rem;
        padding: 2rem;
        border: 1px solid rgba(101, 246, 191, 0.3);
        border-radius: 24px;
        background:
            linear-gradient(
                135deg,
                rgba(22, 55, 45, 0.68),
                rgba(10, 22, 29, 0.88)
            );
        box-shadow: 0 25px 75px rgba(0, 0, 0, 0.28);
    }

    .result-card::after {
        content: "";
        position: absolute;
        width: 190px;
        height: 190px;
        top: -85px;
        right: -50px;
        border-radius: 50%;
        background: rgba(101, 246, 191, 0.14);
        filter: blur(3px);
    }

    .result-label {
        position: relative;
        z-index: 1;
        color: var(--primary);
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.14em;
        text-transform: uppercase;
    }

    .result-crop {
        position: relative;
        z-index: 1;
        margin-top: 0.45rem;
        font-family: "Space Grotesk", sans-serif;
        font-size: clamp(2rem, 5vw, 3.5rem);
        font-weight: 700;
        text-transform: capitalize;
        color: var(--text-main);
    }

    .result-description {
        position: relative;
        z-index: 1;
        max-width: 700px;
        margin-top: 0.65rem;
        color: #a8bcb5;
        line-height: 1.7;
    }

    .confidence-row {
        position: relative;
        z-index: 1;
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
        margin-top: 1.4rem;
    }

    .confidence-box {
        min-width: 160px;
        padding: 0.9rem 1rem;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        background: rgba(3, 10, 14, 0.35);
    }

    .confidence-value {
        color: var(--text-main);
        font-family: "Space Grotesk", sans-serif;
        font-size: 1.25rem;
        font-weight: 600;
    }

    .confidence-label {
        margin-top: 0.2rem;
        color: var(--text-muted);
        font-size: 0.72rem;
    }

    .footer-text {
        margin-top: 2.5rem;
        padding-top: 1.2rem;
        border-top: 1px solid rgba(255, 255, 255, 0.06);
        text-align: center;
        color: #61736d;
        font-size: 0.75rem;
    }

    div[data-testid="stAlert"] {
        border-radius: 15px;
        border: 1px solid rgba(255, 123, 136, 0.25);
        background: rgba(90, 20, 30, 0.26);
    }

    @media (max-width: 768px) {
        .block-container {
            padding-top: 1rem;
        }

        .hero-panel {
            padding: 2rem 1.4rem;
            border-radius: 22px;
        }

        .hero-title {
            font-size: 2.55rem;
        }

        .brand-bar {
            padding: 0.75rem 0.85rem;
        }

        .system-status {
            font-size: 0.68rem;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Navigation and hero section
# --------------------------------------------------

st.markdown(
    """
    <div class="brand-bar">
        <div class="brand-name">AGRIMIND AI</div>
        <div class="system-status">
            <span class="status-dot"></span>
            Prediction engine online
        </div>
    </div>

    <section class="hero-panel">
        <div class="hero-label">Intelligent crop planning system</div>

        <h1 class="hero-title">
            Data-driven farming for a
            <span class="gradient-text">smarter future.</span>
        </h1>

        <p class="hero-description">
            Analyse soil nutrients and climate conditions through a trained
            machine learning model to identify the crop most suitable for
            the selected environment.
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Information cards
# --------------------------------------------------

info_col1, info_col2, info_col3 = st.columns(3)

with info_col1:
    st.markdown(
        """
        <div class="parameter-card">
            <div class="parameter-title">Soil intelligence</div>
            <div class="parameter-text">
                Evaluates nitrogen, phosphorus, potassium and soil pH.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with info_col2:
    st.markdown(
        """
        <div class="parameter-card">
            <div class="parameter-title">Climate analysis</div>
            <div class="parameter-text">
                Processes temperature, humidity and rainfall conditions.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with info_col3:
    st.markdown(
        """
        <div class="parameter-card">
            <div class="parameter-title">Machine learning output</div>
            <div class="parameter-text">
                Generates a crop recommendation using the trained model.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------
# Input form
# --------------------------------------------------

st.markdown(
    """
    <div class="section-heading">Environmental input matrix</div>
    <p class="section-description">
        Enter the latest soil and climate measurements for the field.
    </p>
    """,
    unsafe_allow_html=True,
)

with st.form("crop_recommendation_form"):
    soil_column, climate_column = st.columns(2, gap="large")

    with soil_column:
        st.markdown("#### Soil parameters")

        nitrogen = st.number_input(
            "Nitrogen level",
            min_value=0.0,
            max_value=300.0,
            value=90.0,
            step=1.0,
            help="Estimated nitrogen content in the soil.",
        )

        phosphorus = st.number_input(
            "Phosphorus level",
            min_value=0.0,
            max_value=300.0,
            value=42.0,
            step=1.0,
            help="Estimated phosphorus content in the soil.",
        )

        potassium = st.number_input(
            "Potassium level",
            min_value=0.0,
            max_value=300.0,
            value=43.0,
            step=1.0,
            help="Estimated potassium content in the soil.",
        )

        soil_ph = st.number_input(
            "Soil pH",
            min_value=0.0,
            max_value=14.0,
            value=6.5,
            step=0.1,
            format="%.2f",
            help="Soil acidity or alkalinity on the pH scale.",
        )

    with climate_column:
        st.markdown("#### Climate parameters")

        temperature = st.number_input(
            "Temperature in Celsius",
            min_value=-20.0,
            max_value=70.0,
            value=20.8,
            step=0.1,
            format="%.2f",
        )

        humidity = st.number_input(
            "Humidity percentage",
            min_value=0.0,
            max_value=100.0,
            value=82.0,
            step=0.1,
            format="%.2f",
        )

        rainfall = st.number_input(
            "Rainfall in millimetres",
            min_value=0.0,
            max_value=1000.0,
            value=202.0,
            step=1.0,
            format="%.2f",
        )

    submitted = st.form_submit_button(
        "Generate crop recommendation",
        use_container_width=True,
    )


# --------------------------------------------------
# Prediction
# --------------------------------------------------

if submitted:
    validation_errors = []

    if not 0 <= soil_ph <= 14:
        validation_errors.append("Soil pH must be between 0 and 14.")

    if not 0 <= humidity <= 100:
        validation_errors.append("Humidity must be between 0 and 100 percent.")

    if validation_errors:
        for message in validation_errors:
            st.error(message)

    else:
        input_data = np.array(
            [
                [
                    nitrogen,
                    phosphorus,
                    potassium,
                    temperature,
                    humidity,
                    soil_ph,
                    rainfall,
                ]
            ],
            dtype=float,
        )

        try:
            prediction = model.predict(input_data)
            recommended_crop = str(prediction[0])

            confidence_html = ""

            if hasattr(model, "predict_proba"):
                probabilities = model.predict_proba(input_data)[0]
                confidence = float(np.max(probabilities)) * 100

                confidence_html = f"""
                    <div class="confidence-box">
                        <div class="confidence-value">
                            {confidence:.1f}%
                        </div>
                        <div class="confidence-label">
                            Model confidence
                        </div>
                    </div>
                """

            st.markdown(
                f"""
                <section class="result-card">
                    <div class="result-label">
                        Recommended crop
                    </div>

                    <div class="result-crop">
                        {recommended_crop}
                    </div>

                    <div class="result-description">
                        The model identified this crop as the most suitable
                        option based on the supplied soil nutrient and climate
                        measurements.
                    </div>

                    <div class="confidence-row">
                        {confidence_html}

                        <div class="confidence-box">
                            <div class="confidence-value">
                                7
                            </div>
                            <div class="confidence-label">
                                Parameters analysed
                            </div>
                        </div>

                        <div class="confidence-box">
                            <div class="confidence-value">
                                Active
                            </div>
                            <div class="confidence-label">
                                Prediction status
                            </div>
                        </div>
                    </div>
                </section>
                """,
                unsafe_allow_html=True,
            )

        except Exception as error:
            st.error(
                "The prediction could not be generated. "
                f"Technical details: {error}"
            )


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.markdown(
    """
    <div class="footer-text">
        AgriMind AI · Intelligent Crop Recommendation Platform
    </div>
    """,
    unsafe_allow_html=True,
)