from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()


class SensorReading(BaseModel):
    sensor_id: str = Field(..., min_length=1)
    field_id: str = Field(..., min_length=1)
    timestamp: datetime
    soil_moisture: float = Field(..., ge=0, le=100)


@app.post("/sensor-data")
def add_sensor_data(reading: SensorReading):

    conn = None
    cursor = None

    try:
        conn = psycopg2.connect(
            host="localhost",
            database="smart_irrigation",
            user="postgres",
            password=os.getenv("POSTGRES_PASSWORD"),
            port="5432"
        )

        cursor = conn.cursor()

        # Check that the sensor is registered for the field
        cursor.execute(
            """
            SELECT 1
            FROM sensor
            WHERE sensor_id = %s
              AND field_id = %s
            """,
            (reading.sensor_id, reading.field_id)
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=400,
                detail="Sensor is not registered for this field."
            )

        # Prevent duplicate sensor readings
        cursor.execute(
            """
            SELECT 1
            FROM sensor_data
            WHERE sensor_id = %s
              AND field_id = %s
              AND timestamp = %s
            """,
            (
                reading.sensor_id,
                reading.field_id,
                reading.timestamp
            )
        )

        if cursor.fetchone() is not None:
            raise HTTPException(
                status_code=409,
                detail="Duplicate sensor reading."
            )

        # Insert valid sensor reading
        cursor.execute(
            """
            INSERT INTO sensor_data
            (sensor_id, field_id, timestamp, soil_moisture)
            VALUES (%s, %s, %s, %s)
            """,
            (
                reading.sensor_id,
                reading.field_id,
                reading.timestamp,
                reading.soil_moisture
            )
        )

        conn.commit()

        return {
            "message": "Sensor data stored successfully",
            "sensor_id": reading.sensor_id,
            "field_id": reading.field_id,
            "soil_moisture": reading.soil_moisture,
            "timestamp": reading.timestamp
        }

    except HTTPException:
        if conn:
            conn.rollback()
        raise

    except psycopg2.Error as error:
        if conn:
            conn.rollback()

        print("DATABASE ERROR:", error)

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    except Exception as error:
        if conn:
            conn.rollback()

        print("UNEXPECTED ERROR:", error)

        raise HTTPException(
            status_code=500,
            detail="Unexpected error occurred."
        )

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()