from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
from dotenv import load_dotenv
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

app = FastAPI()


class SensorReading(BaseModel):
    sensor_id: str
    field_id: str
    timestamp: str
    soil_moisture: float


@app.get("/")
def home():
    return {"message": "Smart Irrigation Sensor API is running"}


@app.post("/sensor-data")
def add_sensor_data(reading: SensorReading):

    conn = psycopg2.connect(
        host="localhost",
        database="smart_irrigation",
        user="postgres",
        password=os.getenv("POSTGRES_PASSWORD"),
        port="5432"
    )

    cursor = conn.cursor()

    query = """
        INSERT INTO sensor_data
        (sensor_id, field_id, timestamp, soil_moisture)
        VALUES (%s, %s, %s, %s)
    """

    cursor.execute(
        query,
        (
            reading.sensor_id,
            reading.field_id,
            reading.timestamp,
            reading.soil_moisture
        )
    )

    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "Sensor data stored successfully"}