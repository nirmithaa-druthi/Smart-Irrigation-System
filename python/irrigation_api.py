import os
import sys
from datetime import datetime

import psycopg2

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# =========================================================
# PROJECT ROOT
# =========================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


from ml.predict_irrigation import (
    predict_irrigation,
    get_supported_crops,
)

from ml.irrigation_scheduler import (
    create_automatic_irrigation_schedule,
    get_latest_water_usage,
)


# =========================================================
# DATABASE
# =========================================================

DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")


def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="smart_irrigation",
        user="postgres",
        password=DB_PASSWORD,
        port="5432",
    )


# =========================================================
# FASTAPI
# =========================================================

app = FastAPI(
    title="Smart Irrigation Multi-Crop API",
    description=(
        "AI-powered irrigation prediction "
        "and automatic scheduling API"
    ),
    version="4.0",
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# REQUEST MODELS
# =========================================================


class IrrigationRequest(BaseModel):
    field_id: str

    soil_moisture: float = Field(
        ...,
        ge=0,
        le=100,
    )

    temperature: float

    humidity: float = Field(
        ...,
        ge=0,
        le=100,
    )

    rainfall: float = Field(
        ...,
        ge=0,
    )

    rain_probability: float = Field(
        ...,
        ge=0,
        le=100,
    )

    crop_type: str

    growth_stage: int = Field(
        ...,
        ge=1,
        le=3,
    )

    hour: int = Field(
        default=6,
        ge=0,
        le=23,
    )

    day_of_week: int = Field(
        default=0,
        ge=0,
        le=6,
    )

    day_of_month: int = Field(
        default=1,
        ge=1,
        le=31,
    )

    previous_water_usage_liters: float | None = Field(
        default=None,
        ge=0,
    )


class IrrigationResponse(BaseModel):
    field_id: str
    irrigation_required: bool
    predicted_water_quantity_liters: float
    crop_type: str
    growth_stage: int
    previous_water_usage_liters: float
    reason: str


class FieldRequest(BaseModel):
    field_name: str
    crop_type: str

    growth_stage: int = Field(
        ...,
        ge=1,
        le=3,
    )

    soil_moisture: float = Field(
        ...,
        ge=0,
        le=100,
    )

    field_size: float = Field(
        default=1.0,
        gt=0,
    )


class ScheduleRequest(BaseModel):
    field_id: str
    crop_type: str

    growth_stage: int = Field(
        ...,
        ge=1,
        le=3,
    )

    previous_water_usage_liters: float | None = Field(
        default=None,
        ge=0,
    )


# =========================================================
# ROOT
# =========================================================


@app.get("/")
def root():
    return {
        "message": "Smart Irrigation Multi-Crop API",
        "supported_crop_count": len(
            get_supported_crops()
        ),
        "version": "4.0",
    }


# =========================================================
# SUPPORTED CROPS
# =========================================================


@app.get("/supported-crops")
def supported_crops():

    crops = get_supported_crops()

    return {
        "count": len(crops),
        "crops": crops,
    }


# =========================================================
# HEALTH
# =========================================================


@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "model": "Random Forest Multi-Crop",
        "supported_crops": len(
            get_supported_crops()
        ),
    }


# =========================================================
# GET ALL FIELDS
# =========================================================


@app.get("/fields")
def get_fields():

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            SELECT
                f.field_id,
                f.farmer_id,
                f.location,
                f.field_size,
                c.crop_type,
                c.growth_stage
            FROM field f
            LEFT JOIN crop c
                ON f.field_id = c.field_id
            ORDER BY f.field_id
            """
        )

        rows = cursor.fetchall()

        fields = []

        for row in rows:

            growth_stage = row[5]

            if isinstance(
                growth_stage,
                str
            ):
                if "1" in growth_stage:
                    growth_stage_number = 1
                elif "2" in growth_stage:
                    growth_stage_number = 2
                elif "3" in growth_stage:
                    growth_stage_number = 3
                else:
                    growth_stage_number = 1
            else:
                growth_stage_number = (
                    int(growth_stage)
                    if growth_stage is not None
                    else 1
                )

            fields.append(
                {
                    "field_id": row[0],
                    "farmer_id": row[1],
                    "field_name": row[2],
                    "field_size": float(row[3]),
                    "crop_type": row[4],
                    "growth_stage": growth_stage_number,
                }
            )

        return {
            "count": len(fields),
            "fields": fields,
        }

    finally:

        cursor.close()
        connection.close()

# =========================================================
# WEATHER HISTORY
# =========================================================

@app.get("/weather/history/{field_id}")
def get_weather_history(field_id: str):
    """
    Return historical weather records for a field.
    Used by the Farmer PWA weather and rainfall trends.
    """

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        cursor.execute(
            """
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
            ORDER BY timestamp ASC
            """,
            (field_id,),
        )

        rows = cursor.fetchall()

        history = []

        for row in rows:
            history.append(
                {
                    "field_id": row[0],
                    "location": row[1],
                    "timestamp": (
                        row[2].isoformat()
                        if row[2]
                        else None
                    ),
                    "temperature": float(row[3]),
                    "humidity": float(row[4]),
                    "rainfall": float(row[5]),
                    "rain_probability": float(row[6]),
                }
            )

        return {
            "field_id": field_id,
            "count": len(history),
            "history": history,
        }

    finally:
        cursor.close()
        connection.close()
# =========================================================
# CREATE FIELD
# =========================================================


@app.post("/fields")
def create_field(
    request: FieldRequest
):
    """
    Create a new field and its related
    crop, sensor and initial sensor reading.

    Existing project schema:

    field:
        field_id
        farmer_id
        location
        field_size

    crop:
        crop_id
        field_id
        crop_type
        growth_stage

    sensor:
        sensor_id
        field_id
        sensor_type

    sensor_data:
        sensor_id
        field_id
        timestamp
        soil_moisture
    """

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        # -----------------------------------------------------
        # VALIDATE CROP
        # -----------------------------------------------------

        crop_type = (
            request.crop_type
            .strip()
            .lower()
        )

        supported_crops = [
            crop.lower()
            for crop in get_supported_crops()
        ]

        if crop_type not in supported_crops:

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Unsupported crop: "
                    f"{request.crop_type}. "
                    f"Use one of the supported crops."
                ),
            )

        # -----------------------------------------------------
        # CHECK DUPLICATE LOCATION / FIELD NAME
        # -----------------------------------------------------

        cursor.execute(
            """
            SELECT field_id
            FROM field
            WHERE LOWER(location) = LOWER(%s)
            """,
            (
                request.field_name.strip(),
            ),
        )

        existing_field = cursor.fetchone()

        if existing_field is not None:

            raise HTTPException(
                status_code=409,
                detail=(
                    "A field with this name "
                    "already exists."
                ),
            )

        # -----------------------------------------------------
        # GENERATE NEXT FIELD ID
        # -----------------------------------------------------

        cursor.execute(
            """
            SELECT field_id
            FROM field
            WHERE field_id LIKE 'FIELD%'
            ORDER BY field_id DESC
            LIMIT 1
            """
        )

        row = cursor.fetchone()

        if row is None:

            field_number = 1

        else:

            last_field_id = row[0]

            try:

                field_number = (
                    int(
                        last_field_id.replace(
                            "FIELD",
                            ""
                        )
                    )
                    + 1
                )

            except ValueError:

                field_number = 1

        field_id = (
            f"FIELD{field_number:03d}"
        )

        # -----------------------------------------------------
        # INSERT FIELD
        # -----------------------------------------------------
        # farmer_id 1 = existing Demo Farmer
        #
        # Current project field schema:
        # field_id, farmer_id, location, field_size

        cursor.execute(
            """
            INSERT INTO field
            (
                field_id,
                farmer_id,
                location,
                field_size
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                field_id,
                1,
                request.field_name.strip(),
                request.field_size,
            ),
        )

        # -----------------------------------------------------
        # GENERATE CROP ID
        # -----------------------------------------------------

        cursor.execute(
            """
            SELECT COALESCE(
                MAX(crop_id),
                0
            ) + 1
            FROM crop
            """
        )

        crop_id = cursor.fetchone()[0]

        # -----------------------------------------------------
        # STORE GROWTH STAGE
        # -----------------------------------------------------

        growth_stage_text = (
            f"Stage {request.growth_stage}"
        )

        # -----------------------------------------------------
        # INSERT CROP
        # -----------------------------------------------------
        # Actual schema:
        # crop_id, field_id, crop_type, growth_stage

        cursor.execute(
            """
            INSERT INTO crop
            (
                crop_id,
                field_id,
                crop_type,
                growth_stage
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                crop_id,
                field_id,
                crop_type,
                growth_stage_text,
            ),
        )

        # -----------------------------------------------------
        # GENERATE SENSOR ID
        # -----------------------------------------------------

        cursor.execute(
            """
            SELECT sensor_id
            FROM sensor
            WHERE sensor_id LIKE 'SENSOR%'
            ORDER BY sensor_id DESC
            LIMIT 1
            """
        )

        row = cursor.fetchone()

        if row is None:

            sensor_number = 1

        else:

            last_sensor_id = row[0]

            try:

                sensor_number = (
                    int(
                        last_sensor_id.replace(
                            "SENSOR",
                            ""
                        )
                    )
                    + 1
                )

            except ValueError:

                sensor_number = 1

        sensor_id = (
            f"SENSOR{sensor_number:03d}"
        )

        # -----------------------------------------------------
        # INSERT SENSOR
        # -----------------------------------------------------

        cursor.execute(
            """
            INSERT INTO sensor
            (
                sensor_id,
                field_id,
                sensor_type
            )
            VALUES (%s, %s, %s)
            """,
            (
                sensor_id,
                field_id,
                "Soil Moisture Sensor",
            ),
        )

        # -----------------------------------------------------
        # INSERT INITIAL SENSOR READING
        # -----------------------------------------------------

        cursor.execute(
            """
            INSERT INTO sensor_data
            (
                sensor_id,
                field_id,
                timestamp,
                soil_moisture
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                sensor_id,
                field_id,
                datetime.now(),
                request.soil_moisture,
            ),
        )

        # -----------------------------------------------------
        # COMMIT
        # -----------------------------------------------------

        connection.commit()

        return {
            "message": "Field created successfully.",
            "field_id": field_id,
            "farmer_id": 1,
            "field_name": request.field_name.strip(),
            "field_size": request.field_size,
            "crop_type": crop_type,
            "growth_stage": request.growth_stage,
            "soil_moisture": request.soil_moisture,
            "sensor_id": sensor_id,
        }

    except HTTPException:

        connection.rollback()
        raise

    except Exception as error:

        connection.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to create field: "
                f"{str(error)}"
            ),
        )

    finally:

        cursor.close()
        connection.close()


# =========================================================
# LATEST WEATHER
# =========================================================


@app.get("/weather/latest/{field_id}")
def get_latest_weather(field_id: str):
    """
    Return the latest weather record stored in PostgreSQL
    for the requested field.
    """

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
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
            ORDER BY timestamp DESC
            LIMIT 1
            """,
            (field_id,),
        )

        row = cursor.fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail=f"No weather data found for field {field_id}.",
            )

        return {
            "field_id": row[0],
            "location": row[1],
            "timestamp": row[2].isoformat(),
            "temperature": float(row[3]),
            "humidity": float(row[4]),
            "rainfall": float(row[5]),
            "rain_probability": float(row[6]),
        }

    finally:
        cursor.close()
        connection.close()


# =========================================================
# IRRIGATION PREDICTION
# =========================================================


@app.post(
    "/predict-irrigation",
    response_model=IrrigationResponse,
)
def predict_irrigation_endpoint(
    request: IrrigationRequest
):
    """
    Predict irrigation requirement.

    If previous water usage is not supplied,
    latest irrigation history is retrieved
    from PostgreSQL.
    """

    try:

        crop_type_normalized = (
            request.crop_type
            .strip()
            .lower()
        )

        if (
            request.previous_water_usage_liters
            is not None
        ):

            previous_water_usage = float(
                request.previous_water_usage_liters
            )

        else:

            history = get_latest_water_usage(
                field_id="FIELD001",
                crop_type=crop_type_normalized,
            )

            if history is not None:

                previous_water_usage = float(
                    history[
                        "water_used_liters"
                    ]
                )

            else:

                previous_water_usage = 0.0

        result = predict_irrigation(
            soil_moisture=request.soil_moisture,
            temperature=request.temperature,
            humidity=request.humidity,
            rainfall=request.rainfall,
            rain_probability=request.rain_probability,
            crop_type=crop_type_normalized,
            growth_stage=request.growth_stage,
            hour=request.hour,
            day_of_week=request.day_of_week,
            day_of_month=request.day_of_month,
            previous_water_usage_liters=(
                previous_water_usage
            ),
        )

        return {
            "field_id": request.field_id,
            "irrigation_required": bool(
                result[
                    "irrigation_required"
                ]
            ),

            "predicted_water_quantity_liters":
                float(
                    result[
                        "predicted_water_quantity_liters"
                    ]
                ),

            "crop_type":
                result["crop_type"],

            "growth_stage":
                int(
                    result["growth_stage"]
                ),

            "previous_water_usage_liters":
                previous_water_usage,

            "reason":
                result["reason"],
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Prediction failed: "
                f"{str(error)}"
            ),
        )


# =========================================================
# IRRIGATION SCHEDULING
# =========================================================


@app.post("/schedule-irrigation")
def schedule_irrigation(
    request: ScheduleRequest
):
    """
    Automatically generate
    an irrigation schedule.
    """

    try:

        result = (
            create_automatic_irrigation_schedule(
                field_id=request.field_id,
                crop_type=request.crop_type,
                growth_stage=request.growth_stage,
                previous_water_usage_liters=(
                    request.previous_water_usage_liters
                ),
            )
        )

        return result

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Scheduling failed: "
                f"{str(error)}"
            ),
        )
   # =========================================================
# IRRIGATION HISTORY
# =========================================================


@app.get("/irrigation-history/{field_id}")
def get_irrigation_history(field_id: str):
    """
    Return previous irrigation records for a field.
    """

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            SELECT
                history_id,
                field_id,
                crop_type,
                growth_stage,
                irrigation_timestamp,
                water_used_liters,
                source,
                notes
            FROM irrigation_history
            WHERE field_id = %s
            ORDER BY irrigation_timestamp DESC
            """,
            (field_id,),
        )

        rows = cursor.fetchall()

        history = []

        for row in rows:
            history.append(
                {
                    "history_id": row[0],
                    "field_id": row[1],
                    "crop_type": row[2],
                    "growth_stage": row[3],
                    "irrigation_timestamp": (
                        row[4].isoformat()
                        if row[4]
                        else None
                    ),
                    "water_used_liters": float(row[5]),
                    "source": row[6],
                    "notes": row[7],
                }
            )

        return {
            "field_id": field_id,
            "count": len(history),
            "history": history,
        }

    finally:
        cursor.close()
        connection.close()