import os
import sys

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Allow imports from project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml.predict_irrigation import predict_irrigation, get_supported_crops
from ml.irrigation_scheduler import (
    create_automatic_irrigation_schedule,
    get_latest_water_usage,
)


app = FastAPI(
    title="Smart Irrigation Multi-Crop API",
    description="AI-powered irrigation prediction and automatic scheduling API",
    version="2.2"
)


class IrrigationRequest(BaseModel):
    soil_moisture: float = Field(..., ge=0, le=100)
    temperature: float
    humidity: float = Field(..., ge=0, le=100)
    rainfall: float = Field(..., ge=0)
    rain_probability: float = Field(..., ge=0, le=100)

    crop_type: str
    growth_stage: int = Field(..., ge=1, le=3)

    hour: int = Field(default=6, ge=0, le=23)
    day_of_week: int = Field(default=0, ge=0, le=6)
    day_of_month: int = Field(default=1, ge=1, le=31)

    previous_water_usage_liters: float | None = Field(
        default=None,
        ge=0
    )


class IrrigationResponse(BaseModel):
    irrigation_required: bool
    predicted_water_quantity_liters: float
    crop_type: str
    growth_stage: int
    previous_water_usage_liters: float
    reason: str


class ScheduleRequest(BaseModel):
    field_id: str
    crop_type: str
    growth_stage: int = Field(..., ge=1, le=3)
    previous_water_usage_liters: float | None = Field(
        default=None,
        ge=0
    )


@app.get("/")
def root():
    """API information."""

    return {
        "message": "Smart Irrigation Multi-Crop API",
        "supported_crop_count": len(get_supported_crops()),
        "version": "2.2"
    }


@app.get("/supported-crops")
def supported_crops():
    """Return all crops supported by the ML model."""

    crops = get_supported_crops()

    return {
        "count": len(crops),
        "crops": crops
    }


@app.get("/health")
def health_check():
    """Check whether the API is healthy."""

    return {
        "status": "healthy",
        "model": "Random Forest Multi-Crop",
        "supported_crops": len(get_supported_crops())
    }


@app.post(
    "/predict-irrigation",
    response_model=IrrigationResponse
)
def predict_irrigation_endpoint(request: IrrigationRequest):
    """
    Predict irrigation requirement.

    If previous water usage is not supplied,
    the latest irrigation history for the crop
    is automatically retrieved from PostgreSQL.
    """

    try:

        crop_type_normalized = request.crop_type.strip().lower()

        # -----------------------------------------------------
        # Determine previous water usage
        # -----------------------------------------------------

        if request.previous_water_usage_liters is not None:

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
                    history["water_used_liters"]
                )

            else:

                previous_water_usage = 0.0

        # -----------------------------------------------------
        # Run ML prediction
        # -----------------------------------------------------

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
            previous_water_usage_liters=previous_water_usage
        )

        return {
            "irrigation_required": bool(
                result["irrigation_required"]
            ),
            "predicted_water_quantity_liters": float(
                result["predicted_water_quantity_liters"]
            ),
            "crop_type": result["crop_type"],
            "growth_stage": int(result["growth_stage"]),
            "previous_water_usage_liters": previous_water_usage,
            "reason": result["reason"]
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(error)}"
        )


@app.post("/schedule-irrigation")
def schedule_irrigation(request: ScheduleRequest):
    """
    Automatically generate an irrigation schedule.

    The scheduler reads the latest sensor data,
    weather forecast and irrigation history
    from PostgreSQL.
    """

    try:

        result = create_automatic_irrigation_schedule(
            field_id=request.field_id,
            crop_type=request.crop_type,
            growth_stage=request.growth_stage,
            previous_water_usage_liters=request.previous_water_usage_liters
        )

        return result

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Scheduling failed: {str(error)}"
        )