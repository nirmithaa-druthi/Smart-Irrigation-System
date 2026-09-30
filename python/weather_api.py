import os
from datetime import datetime, timezone

import psycopg2
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")

CURRENT_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"


# ---------------------------------------------------------
# DATABASE CONNECTION
# ---------------------------------------------------------

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="smart_irrigation",
        user="postgres",
        password=DB_PASSWORD,
        port="5432",
    )


# ---------------------------------------------------------
# WEATHER API
# ---------------------------------------------------------

def get_current_weather(city):
    response = requests.get(
        CURRENT_WEATHER_URL,
        params={
            "q": city,
            "appid": API_KEY,
            "units": "metric",
        },
        timeout=10,
    )

    response.raise_for_status()
    return response.json()


def get_weather_forecast(city):
    response = requests.get(
        FORECAST_URL,
        params={
            "q": city,
            "appid": API_KEY,
            "units": "metric",
        },
        timeout=10,
    )

    response.raise_for_status()
    return response.json()


# ---------------------------------------------------------
# GET ALL REGISTERED FIELDS
# ---------------------------------------------------------

def get_registered_fields():
    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                field_id,
                location
            FROM field
            ORDER BY field_id
            """
        )

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


# ---------------------------------------------------------
# STORE WEATHER RECORD
# ---------------------------------------------------------

def store_weather_record(
    field_id,
    location,
    timestamp,
    temperature,
    humidity,
    rainfall,
    rain_probability,
):
    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT 1
            FROM weather_data
            WHERE field_id = %s
            AND timestamp = %s
            """,
            (
                field_id,
                timestamp,
            ),
        )

        if cursor.fetchone():
            return False

        cursor.execute(
            """
            INSERT INTO weather_data(
                field_id,
                location,
                timestamp,
                temperature,
                humidity,
                rainfall,
                rain_probability
            )
            VALUES(
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                field_id,
                location,
                timestamp,
                temperature,
                humidity,
                rainfall,
                rain_probability,
            ),
        )

        connection.commit()

        return True

    finally:
        cursor.close()
        connection.close()


# ---------------------------------------------------------
# UPDATE WEATHER FOR ONE FIELD
# ---------------------------------------------------------

def update_field_weather(
    field_id,
    location,
):

    print("\n" + "=" * 60)
    print(
        f"WEATHER UPDATE — {field_id}"
    )
    print("=" * 60)

    print("Field location:", location)

    # -----------------------------------------------------
    # CURRENT WEATHER
    # -----------------------------------------------------

    current = get_current_weather(location)

    actual_location = current["name"]

    current_timestamp = datetime.fromtimestamp(
        current["dt"],
        timezone.utc,
    ).replace(
        tzinfo=None
    )

    current_temperature = (
        current["main"]["temp"]
    )

    current_humidity = (
        current["main"]["humidity"]
    )

    current_rainfall = (
        current
        .get("rain", {})
        .get("1h", 0)
    )

    stored = store_weather_record(
        field_id,
        actual_location,
        current_timestamp,
        current_temperature,
        current_humidity,
        current_rainfall,
        0,
    )

    print(
        "Current weather stored:",
        stored,
    )

    # -----------------------------------------------------
    # FORECAST
    # -----------------------------------------------------

    forecast = get_weather_forecast(
        location
    )

    print(
        "\nSaving complete 5-day forecast..."
    )

    stored_count = 0
    skipped_count = 0

    for item in forecast["list"]:

        timestamp = datetime.strptime(
            item["dt_txt"],
            "%Y-%m-%d %H:%M:%S",
        )

        temperature = (
            item["main"]["temp"]
        )

        humidity = (
            item["main"]["humidity"]
        )

        rainfall = (
            item
            .get("rain", {})
            .get("3h", 0)
        )

        rain_probability = (
            item.get("pop", 0) * 100
        )

        stored = store_weather_record(
            field_id,
            actual_location,
            timestamp,
            temperature,
            humidity,
            rainfall,
            rain_probability,
        )

        if stored:
            stored_count += 1
        else:
            skipped_count += 1

        print(
            timestamp,
            "| Temp:",
            temperature,
            "| Humidity:",
            humidity,
            "| Rain:",
            rainfall,
            "| POP:",
            rain_probability,
            "| Stored:",
            stored,
        )

    print("\n" + "-" * 60)

    print(
        f"Field {field_id} completed."
    )

    print(
        "Forecast records stored:",
        stored_count,
    )

    print(
        "Duplicate records skipped:",
        skipped_count,
    )

    print(
        "Forecast records checked:",
        len(forecast["list"]),
    )


# ---------------------------------------------------------
# UPDATE WEATHER FOR ALL REGISTERED FIELDS
# ---------------------------------------------------------

def update_weather_database():

    fields = get_registered_fields()

    if not fields:
        print(
            "No registered fields found."
        )
        return

    print("=" * 60)
    print("SMART IRRIGATION WEATHER UPDATE")
    print("=" * 60)

    print(
        "Registered fields:",
        len(fields),
    )

    for field_id, location in fields:

        try:

            update_field_weather(
                field_id,
                location,
            )

        except requests.exceptions.RequestException as error:

            print(
                f"\nWeather API error for "
                f"{field_id} ({location}):"
            )

            print(error)

        except Exception as error:

            print(
                f"\nError updating "
                f"{field_id} ({location}):"
            )

            print(error)

    print("\n" + "=" * 60)
    print("ALL FIELD WEATHER UPDATES COMPLETED")
    print("=" * 60)


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

if __name__ == "__main__":

    try:

        update_weather_database()

    except requests.exceptions.RequestException as error:

        print(
            "Weather API Error:",
            error,
        )

    except psycopg2.Error as error:

        print(
            "Database Error:",
            error,
        )

    except Exception as error:

        print(
            "Unexpected Error:",
            error,
        )