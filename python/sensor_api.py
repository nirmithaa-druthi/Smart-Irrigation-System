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

    try:
        conn = psycopg2.connect(
            host="localhost",
            database="smart_irrigation",
            user="postgres",
            password=os.getenv("POSTGRES_PASSWORD"),
            port="5432"
        )

        cursor = conn.cursor()

        # Check that the sensor is registered
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

        cursor.close()
        conn.close()

        return {
            "message": "Sensor data stored successfully",
            "sensor_id": reading.sensor_id,
            "field_id": reading.field_id,
            "soil_moisture": reading.soil_moisture,
            "timestamp": reading.timestamp
        }

    except HTTPException:
        raise

    except psycopg2.Error as error:
        raise HTTPException(
            status_code=500,
            detail="Database error while storing sensor data."
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Unexpected error occurred."
        )