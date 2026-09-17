import os
import sys
from datetime import datetime, timedelta

import psycopg2
from dotenv import load_dotenv

# Allow imports from project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml.predict_irrigation import predict_irrigation, get_supported_crops

load_dotenv()


def get_db_connection():
    """Create a PostgreSQL database connection."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "smart_irrigation"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
    )


def get_latest_sensor_data(field_id):
    """Fetch the latest sensor reading for a field."""

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        query = """
            SELECT
                sensor_id,
                field_id,
                timestamp,
                soil_moisture
            FROM sensor_data
            WHERE field_id = %s
            ORDER BY timestamp DESC
            LIMIT 1;
        """

        cursor.execute(query, (field_id,))
        row = cursor.fetchone()

        if row is None:
            raise ValueError(
                f"No sensor data found for field '{field_id}'."
            )

        return {
            "sensor_id": row[0],
            "field_id": row[1],
            "timestamp": row[2],
            "soil_moisture": float(row[3]),
        }

    finally:
        cursor.close()
        connection.close()


def get_weather_data_closest_to(field_id, target_time):
    """
    Fetch the weather record closest to the target irrigation time.
    """

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        query = """
            SELECT
                field_id,
                location,
                timestamp,
                temperature,
                humidity,
                rainfall,
                rain_probability
            FROM weather_data
            WHERE field_id = %s
            ORDER BY ABS(EXTRACT(EPOCH FROM (timestamp - %s)))
            LIMIT 1;
        """

        cursor.execute(
            query,
            (field_id, target_time)
        )

        row = cursor.fetchone()

        if row is None:
            raise ValueError(
                f"No weather data found for field '{field_id}'."
            )

        return {
            "field_id": row[0],
            "location": row[1],
            "timestamp": row[2],
            "temperature": float(row[3]),
            "humidity": float(row[4]),
            "rainfall": float(row[5]),
            "rain_probability": float(row[6]),
        }

    finally:
        cursor.close()
        connection.close()


def get_latest_water_usage(field_id, crop_type=None):
    """
    Fetch the latest actual irrigation water usage.

    If crop_type is provided, the search is restricted to that crop.
    Returns None when no irrigation history exists.
    """

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        if crop_type:
            query = """
                SELECT
                    water_used_liters,
                    irrigation_timestamp,
                    crop_type
                FROM irrigation_history
                WHERE field_id = %s
                  AND LOWER(crop_type) = LOWER(%s)
                ORDER BY irrigation_timestamp DESC
                LIMIT 1;
            """

            cursor.execute(
                query,
                (field_id, crop_type)
            )

        else:
            query = """
                SELECT
                    water_used_liters,
                    irrigation_timestamp,
                    crop_type
                FROM irrigation_history
                WHERE field_id = %s
                ORDER BY irrigation_timestamp DESC
                LIMIT 1;
            """

            cursor.execute(
                query,
                (field_id,)
            )

        row = cursor.fetchone()

        if row is None:
            return None

        return {
            "water_used_liters": float(row[0]),
            "irrigation_timestamp": row[1],
            "crop_type": row[2],
        }

    finally:
        cursor.close()
        connection.close()


def calculate_recommended_time(current_time=None):
    """
    Recommend the next irrigation time.

    Irrigation is scheduled for the next 6:00 AM.
    """

    if current_time is None:
        current_time = datetime.now()

    recommended_time = current_time.replace(
        hour=6,
        minute=0,
        second=0,
        microsecond=0,
    )

    if recommended_time <= current_time:
        recommended_time += timedelta(days=1)

    return recommended_time


def save_irrigation_schedule(
    field_id,
    crop_type,
    growth_stage,
    irrigation_required,
    predicted_water_quantity_liters,
    recommended_water_quantity_liters,
    recommended_time,
    schedule_status,
    reason,
):
    """Save the irrigation result to PostgreSQL."""

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        query = """
            INSERT INTO irrigation_schedule (
                field_id,
                crop_type,
                growth_stage,
                irrigation_required,
                predicted_water_quantity_liters,
                recommended_water_quantity_liters,
                recommended_time,
                schedule_status,
                reason
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING schedule_id;
        """

        cursor.execute(
            query,
            (
                field_id,
                crop_type,
                str(growth_stage),
                irrigation_required,
                predicted_water_quantity_liters,
                recommended_water_quantity_liters,
                recommended_time,
                schedule_status,
                reason,
            ),
        )

        schedule_id = cursor.fetchone()[0]

        connection.commit()

        return schedule_id

    finally:
        cursor.close()
        connection.close()


def create_automatic_irrigation_schedule(
    field_id,
    crop_type,
    growth_stage,
    previous_water_usage_liters=None,
):
    """
    Automatically create an irrigation schedule using:

    1. Latest sensor data
    2. Weather forecast closest to irrigation time
    3. Latest actual irrigation history
    4. Multi-crop ML prediction
    """

    supported_crops = get_supported_crops()

    crop_type_normalized = crop_type.strip().lower()

    if crop_type_normalized not in supported_crops:
        raise ValueError(
            f"Unsupported crop '{crop_type}'. "
            f"Supported crops: {', '.join(supported_crops)}"
        )

    # ---------------------------------------------------------
    # 1. Get latest sensor data
    # ---------------------------------------------------------

    sensor = get_latest_sensor_data(field_id)

    # ---------------------------------------------------------
    # 2. Calculate recommended irrigation time
    # ---------------------------------------------------------

    recommended_time = calculate_recommended_time()

    # ---------------------------------------------------------
    # 3. Get weather closest to irrigation time
    # ---------------------------------------------------------

    weather = get_weather_data_closest_to(
        field_id,
        recommended_time,
    )

    # ---------------------------------------------------------
    # 4. Get latest actual irrigation water usage
    # ---------------------------------------------------------

    latest_history = get_latest_water_usage(
        field_id,
        crop_type_normalized,
    )

    if latest_history is not None:

        previous_water_usage = latest_history["water_used_liters"]

        history_timestamp = latest_history["irrigation_timestamp"]

        print(
            f"Using latest irrigation history: "
            f"{previous_water_usage} L "
            f"from {history_timestamp}"
        )

    else:

        if previous_water_usage_liters is not None:
            previous_water_usage = float(
                previous_water_usage_liters
            )

            print(
                "No irrigation history found. "
                f"Using provided previous water usage: "
                f"{previous_water_usage} L"
            )

        else:
            previous_water_usage = 0.0

            print(
                "No irrigation history found. "
                "Using previous water usage: 0 L"
            )

    # ---------------------------------------------------------
    # 5. Extract timestamp information
    # ---------------------------------------------------------

    sensor_timestamp = sensor["timestamp"]

    hour = sensor_timestamp.hour
    day_of_week = sensor_timestamp.weekday()
    day_of_month = sensor_timestamp.day

    # ---------------------------------------------------------
    # 6. Run multi-crop ML prediction
    # ---------------------------------------------------------

    prediction = predict_irrigation(
        soil_moisture=sensor["soil_moisture"],
        temperature=weather["temperature"],
        humidity=weather["humidity"],
        rainfall=weather["rainfall"],
        rain_probability=weather["rain_probability"],
        crop_type=crop_type_normalized,
        growth_stage=growth_stage,
        hour=hour,
        day_of_week=day_of_week,
        day_of_month=day_of_month,
        previous_water_usage_liters=previous_water_usage,
    )

    irrigation_required = bool(
        prediction["irrigation_required"]
    )

    predicted_water = float(
        prediction["predicted_water_quantity_liters"]
    )

    reason = prediction["reason"]

    # ---------------------------------------------------------
    # 7. No irrigation required
    # ---------------------------------------------------------

    if not irrigation_required:

        schedule_id = save_irrigation_schedule(
            field_id=field_id,
            crop_type=crop_type_normalized,
            growth_stage=growth_stage,
            irrigation_required=False,
            predicted_water_quantity_liters=0,
            recommended_water_quantity_liters=0,
            recommended_time=None,
            schedule_status="not_required",
            reason=reason,
        )

        return {
            "schedule_id": schedule_id,
            "field_id": field_id,
            "crop_type": crop_type_normalized,
            "growth_stage": growth_stage,
            "sensor_timestamp": sensor["timestamp"],
            "soil_moisture": sensor["soil_moisture"],
            "weather_timestamp": weather["timestamp"],
            "temperature": weather["temperature"],
            "humidity": weather["humidity"],
            "rainfall": weather["rainfall"],
            "rain_probability": weather["rain_probability"],
            "previous_water_usage_liters": previous_water_usage,
            "irrigation_required": False,
            "predicted_water_quantity_liters": 0,
            "recommended_water_quantity_liters": 0,
            "recommended_time": None,
            "schedule_status": "not_required",
            "reason": reason,
        }

    # ---------------------------------------------------------
    # 8. Irrigation required
    # ---------------------------------------------------------

    schedule_id = save_irrigation_schedule(
        field_id=field_id,
        crop_type=crop_type_normalized,
        growth_stage=growth_stage,
        irrigation_required=True,
        predicted_water_quantity_liters=predicted_water,
        recommended_water_quantity_liters=predicted_water,
        recommended_time=recommended_time,
        schedule_status="scheduled",
        reason=reason,
    )

    return {
        "schedule_id": schedule_id,
        "field_id": field_id,
        "crop_type": crop_type_normalized,
        "growth_stage": growth_stage,
        "sensor_timestamp": sensor["timestamp"],
        "soil_moisture": sensor["soil_moisture"],
        "weather_timestamp": weather["timestamp"],
        "temperature": weather["temperature"],
        "humidity": weather["humidity"],
        "rainfall": weather["rainfall"],
        "rain_probability": weather["rain_probability"],
        "previous_water_usage_liters": previous_water_usage,
        "irrigation_required": True,
        "predicted_water_quantity_liters": predicted_water,
        "recommended_water_quantity_liters": predicted_water,
        "recommended_time": recommended_time,
        "schedule_status": "scheduled",
        "reason": reason,
    }


if __name__ == "__main__":

    print("=" * 70)
    print("SMART IRRIGATION - AUTOMATIC DATABASE INTEGRATION TEST")
    print("=" * 70)

    FIELD_ID = "FIELD001"
    CROP_TYPE = "rice"
    GROWTH_STAGE = 2

    try:

        result = create_automatic_irrigation_schedule(
            field_id=FIELD_ID,
            crop_type=CROP_TYPE,
            growth_stage=GROWTH_STAGE,
        )

        print("\nAutomatic Scheduler Result:")
        print("-" * 70)

        for key, value in result.items():
            print(f"{key}: {value}")

        print("-" * 70)
        print("Automatic database integration test completed successfully.")

    except Exception as error:

        print("\nERROR:")
        print(error)

        print("\nAutomatic scheduler test failed.")