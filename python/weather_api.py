from dotenv import load_dotenv
import os
import requests
import psycopg2
from datetime import datetime, timezone

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

CITY = "Bengaluru"
FIELD_ID = "FIELD001"

CURRENT_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"


def get_current_weather(city):
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    response = requests.get(
        CURRENT_WEATHER_URL,
        params=params,
        timeout=10
    )

    response.raise_for_status()
    return response.json()


def get_weather_forecast(city):
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    response = requests.get(
        FORECAST_URL,
        params=params,
        timeout=10
    )

    response.raise_for_status()
    return response.json()


def store_weather_data(
    field_id,
    location,
    timestamp,
    temperature,
    humidity,
    rainfall,
    rain_probability
):
    conn = None
    cursor = None

    try:
        conn = psycopg2.connect(
            host="localhost",
            database="smart_irrigation",
            user="postgres",
            password=POSTGRES_PASSWORD,
            port="5432"
        )

        cursor = conn.cursor()

        # Prevent duplicate weather records
        cursor.execute(
            """
            SELECT 1
            FROM weather_data
            WHERE field_id = %s
              AND timestamp = %s
            """,
            (field_id, timestamp)
        )

        if cursor.fetchone() is not None:
            return False

        cursor.execute(
            """
            INSERT INTO weather_data
            (
                field_id,
                location,
                timestamp,
                temperature,
                humidity,
                rainfall,
                rain_probability
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                field_id,
                location,
                timestamp,
                temperature,
                humidity,
                rainfall,
                rain_probability
            )
        )

        conn.commit()
        return True

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()


try:
    current = get_current_weather(CITY)
    forecast = get_weather_forecast(CITY)

    print("Weather API connection successful!")
    print("Location:", current["name"])

    # Current weather
    current_temperature = current["main"]["temp"]
    current_humidity = current["main"]["humidity"]
    current_rainfall = current.get("rain", {}).get("1h", 0)

    current_timestamp = datetime.fromtimestamp(
        current["dt"],
        timezone.utc
    ).replace(tzinfo=None)

    stored = store_weather_data(
        FIELD_ID,
        current["name"],
        current_timestamp,
        current_temperature,
        current_humidity,
        current_rainfall,
        0
    )

    print("Current weather stored:", stored)

    print("\nCurrent Weather:")
    print("Temperature:", current_temperature, "°C")
    print("Humidity:", current_humidity, "%")
    print("Rainfall (last 1 hour):", current_rainfall, "mm")

    # Forecast weather
    print("\nWeather Forecast:")

    for item in forecast["list"][:3]:

        forecast_timestamp = datetime.strptime(
            item["dt_txt"],
            "%Y-%m-%d %H:%M:%S"
        )

        temperature = item["main"]["temp"]
        humidity = item["main"]["humidity"]

        rain_probability = item.get("pop", 0) * 100

        rainfall = item.get("rain", {}).get("3h", 0)

        stored = store_weather_data(
            FIELD_ID,
            CITY,
            forecast_timestamp,
            temperature,
            humidity,
            rainfall,
            rain_probability
        )

        print(
            item["dt_txt"],
            "| Temperature:",
            temperature,
            "°C",
            "| Humidity:",
            humidity,
            "%",
            "| Rainfall:",
            rainfall,
            "mm",
            "| Rain Probability:",
            rain_probability,
            "%",
            "| Stored:",
            stored
        )

except requests.exceptions.RequestException as error:
    print("Weather API request failed.")
    print("Error:", error)

except psycopg2.Error as error:
    print("Database error while storing weather data.")
    print("Error:", error)

except (KeyError, TypeError, ValueError) as error:
    print("Invalid weather API response.")
    print("Error:", error)

except Exception as error:
    print("Unexpected error occurred.")
    print("Error:", error)