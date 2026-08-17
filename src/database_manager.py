import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_DATABASE_PATH = (
    PROJECT_ROOT
    / "database"
    / "agrimind.db"
)


class DatabaseManager:
    """
    SQLite database service for AgriMind AI.

    Stores:
    - Crop recommendation history
    - Weather history
    - Plant disease prediction history
    - Chat history
    """

    def __init__(
        self,
        database_path: str | Path = DEFAULT_DATABASE_PATH,
    ) -> None:
        self.database_path = Path(database_path)

        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._create_tables()

    def _connect(self) -> sqlite3.Connection:
        """Create and return a SQLite connection."""

        connection = sqlite3.connect(
            self.database_path
        )

        connection.row_factory = sqlite3.Row

        return connection

    def _create_tables(self) -> None:
        """Create all required database tables."""

        with self._connect() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS crop_predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nitrogen REAL NOT NULL,
                    phosphorus REAL NOT NULL,
                    potassium REAL NOT NULL,
                    temperature REAL NOT NULL,
                    humidity REAL NOT NULL,
                    ph REAL NOT NULL,
                    rainfall REAL NOT NULL,
                    predicted_crop TEXT NOT NULL,
                    confidence REAL,
                    created_at TEXT NOT NULL
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS weather_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    location TEXT,
                    latitude REAL,
                    longitude REAL,
                    temperature REAL,
                    humidity REAL,
                    rainfall REAL,
                    wind_speed REAL,
                    weather_code INTEGER,
                    risk_score REAL,
                    risk_level TEXT,
                    summary TEXT,
                    advice_json TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS disease_predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    image_name TEXT,
                    crop TEXT NOT NULL,
                    disease TEXT NOT NULL,
                    class_name TEXT NOT NULL,
                    confidence REAL,
                    status TEXT,
                    risk_level TEXT,
                    reliable INTEGER,
                    treatment_json TEXT,
                    prevention_json TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_message TEXT NOT NULL,
                    assistant_response TEXT NOT NULL,
                    model_name TEXT,
                    context_used INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                )
                """
            )

            connection.commit()

    @staticmethod
    def _current_time() -> str:
        """Return current timestamp in ISO format."""

        return datetime.now().isoformat(
            timespec="seconds"
        )

    @staticmethod
    def _to_json(value: Any) -> str:
        """Convert Python value to JSON text."""

        return json.dumps(
            value if value is not None else [],
            ensure_ascii=False,
        )

    @staticmethod
    def _rows_to_dicts(
        rows: list[sqlite3.Row],
    ) -> list[dict[str, Any]]:
        """Convert SQLite rows into dictionaries."""

        return [
            dict(row)
            for row in rows
        ]

    def save_crop_prediction(
        self,
        input_data: dict[str, Any],
        result: dict[str, Any],
    ) -> int:
        """Store a crop recommendation result."""

        predicted_crop = (
            result.get("recommended_crop")
            or result.get("crop")
            or result.get("prediction")
        )

        if not predicted_crop:
            raise ValueError(
                "Crop result does not contain a prediction."
            )

        values = (
            float(input_data["nitrogen"]),
            float(input_data["phosphorus"]),
            float(input_data["potassium"]),
            float(input_data["temperature"]),
            float(input_data["humidity"]),
            float(input_data["ph"]),
            float(input_data["rainfall"]),
            str(predicted_crop),
            (
                float(result["confidence"])
                if result.get("confidence") is not None
                else None
            ),
            self._current_time(),
        )

        with self._connect() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO crop_predictions (
                    nitrogen,
                    phosphorus,
                    potassium,
                    temperature,
                    humidity,
                    ph,
                    rainfall,
                    predicted_crop,
                    confidence,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                values,
            )

            connection.commit()

            return int(cursor.lastrowid)

    def save_weather_history(
        self,
        weather_result: dict[str, Any],
        analysis_result: dict[str, Any] | None = None,
        location: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> int:
        """Store weather data and analysis."""

        analysis_result = analysis_result or {}

        advice = (
            analysis_result.get("advice")
            or analysis_result.get("farmer_advice")
            or []
        )

        values = (
            location,
            latitude,
            longitude,
            weather_result.get("temperature"),
            weather_result.get("humidity"),
            weather_result.get("rainfall"),
            weather_result.get("wind_speed"),
            weather_result.get("weather_code"),
            analysis_result.get("risk_score"),
            analysis_result.get("risk_level"),
            analysis_result.get("summary"),
            self._to_json(advice),
            self._current_time(),
        )

        with self._connect() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO weather_history (
                    location,
                    latitude,
                    longitude,
                    temperature,
                    humidity,
                    rainfall,
                    wind_speed,
                    weather_code,
                    risk_score,
                    risk_level,
                    summary,
                    advice_json,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                values,
            )

            connection.commit()

            return int(cursor.lastrowid)

    def save_disease_prediction(
        self,
        result: dict[str, Any],
        image_name: str | None = None,
    ) -> int:
        """Store a plant-disease prediction."""

        if not result.get("success", False):
            raise ValueError(
                "Only successful disease predictions can be saved."
            )

        values = (
            image_name,
            result["crop"],
            result["disease"],
            result["class_name"],
            result.get("confidence"),
            result.get("status"),
            result.get("risk_level"),
            int(bool(result.get("is_reliable"))),
            self._to_json(result.get("treatment")),
            self._to_json(result.get("prevention")),
            self._current_time(),
        )

        with self._connect() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO disease_predictions (
                    image_name,
                    crop,
                    disease,
                    class_name,
                    confidence,
                    status,
                    risk_level,
                    reliable,
                    treatment_json,
                    prevention_json,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                values,
            )

            connection.commit()

            return int(cursor.lastrowid)

    def save_chat_message(
        self,
        user_message: str,
        chatbot_result: dict[str, Any],
        context_used: bool = False,
    ) -> int:
        """Store one chatbot interaction."""

        if not chatbot_result.get("success", False):
            raise ValueError(
                "Only successful chatbot responses can be saved."
            )

        values = (
            user_message.strip(),
            chatbot_result["answer"],
            chatbot_result.get("model"),
            int(context_used),
            self._current_time(),
        )

        with self._connect() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO chat_history (
                    user_message,
                    assistant_response,
                    model_name,
                    context_used,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                values,
            )

            connection.commit()

            return int(cursor.lastrowid)

    def get_crop_history(
        self,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Return recent crop recommendations."""

        return self._get_recent_rows(
            table_name="crop_predictions",
            limit=limit,
        )

    def get_weather_history(
        self,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Return recent weather records."""

        return self._get_recent_rows(
            table_name="weather_history",
            limit=limit,
        )

    def get_disease_history(
        self,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Return recent disease predictions."""

        return self._get_recent_rows(
            table_name="disease_predictions",
            limit=limit,
        )

    def get_chat_history(
        self,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Return recent chatbot conversations."""

        return self._get_recent_rows(
            table_name="chat_history",
            limit=limit,
        )

    def _get_recent_rows(
        self,
        table_name: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        """Return recent rows from an approved table."""

        allowed_tables = {
            "crop_predictions",
            "weather_history",
            "disease_predictions",
            "chat_history",
        }

        if table_name not in allowed_tables:
            raise ValueError(
                "Invalid database table requested."
            )

        if limit <= 0:
            raise ValueError(
                "Limit must be greater than zero."
            )

        query = (
            f"SELECT * FROM {table_name} "
            "ORDER BY id DESC LIMIT ?"
        )

        with self._connect() as connection:
            cursor = connection.cursor()

            cursor.execute(
                query,
                (limit,),
            )

            rows = cursor.fetchall()

        return self._rows_to_dicts(rows)

    def get_record_counts(self) -> dict[str, int]:
        """Return total records in every table."""

        counts: dict[str, int] = {}

        tables = {
            "crop_predictions": "crop",
            "weather_history": "weather",
            "disease_predictions": "disease",
            "chat_history": "chat",
        }

        with self._connect() as connection:
            cursor = connection.cursor()

            for table_name, result_name in tables.items():
                cursor.execute(
                    f"SELECT COUNT(*) FROM {table_name}"
                )

                counts[result_name] = int(
                    cursor.fetchone()[0]
                )

        return counts