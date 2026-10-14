const IRRIGATION_API_URL = "http://127.0.0.1:8001";
const SENSOR_API_URL = "http://127.0.0.1:8002";

/* =========================================================
   IRRIGATION PREDICTION
   ========================================================= */

export interface IrrigationRequest {
  field_id: string;
  soil_moisture: number;
  temperature: number;
  humidity: number;
  rainfall: number;
  rain_probability: number;
  crop_type: string;
  growth_stage: number;
  hour: number;
  day_of_week: number;
  day_of_month: number;
  previous_water_usage_liters: number;
}

export interface IrrigationResponse {
  field_id?: string;
  irrigation_required: boolean;
  predicted_water_quantity_liters: number;
  crop_type: string;
  growth_stage: number;
  previous_water_usage_liters: number;
  reason: string;
}

/* =========================================================
   SENSOR
   ========================================================= */

export interface SensorResponse {
  sensor_id: string;
  field_id: string;
  timestamp: string;
  soil_moisture: number;
}

/* =========================================================
   WEATHER
   ========================================================= */

export interface WeatherResponse {
  field_id: string;
  location: string;
  timestamp: string;
  temperature: number;
  humidity: number;
  rainfall: number;
  rain_probability: number;
}

/* =========================================================
   FIELD
   ========================================================= */

export interface FieldResponse {
  field_id: string;
  farmer_id: number;
  field_name: string;
  field_size: number;
  crop_type: string;
  growth_stage: number;
  soil_moisture?: number;
  sensor_id?: string;
}

export interface CreateFieldRequest {
  field_name: string;
  soil_moisture: number;
  location: string;
  field_size: number;
  crop_type: string;
  growth_stage: string;
}

/* =========================================================
   IRRIGATION SCHEDULE
   ========================================================= */

export interface ScheduleRequest {
  field_id: string;
  crop_type: string;
  growth_stage: number;
  previous_water_usage_liters?: number;
}

export interface ScheduleResponse {
  schedule_id: number;
  field_id: string;
  crop_type: string;
  growth_stage: number;
  sensor_timestamp: string;
  soil_moisture: number;
  weather_timestamp: string;
  temperature: number;
  humidity: number;
  rainfall: number;
  rain_probability: number;
  irrigation_required: boolean;
  predicted_water_quantity_liters: number;
  recommended_water_quantity_liters: number;
  recommended_time: string | null;
  schedule_status: string;
  reason: string;
}

/* =========================================================
   IRRIGATION HISTORY
   ========================================================= */

export interface IrrigationHistoryItem {
  history_id: number;
  field_id: string;
  crop_type: string;
  growth_stage: string;
  irrigation_timestamp: string;
  water_used_liters: number;
  source: string;
  notes: string | null;
}

export interface IrrigationHistoryResponse {
  field_id: string;
  count: number;
  history: IrrigationHistoryItem[];
}

/* =========================================================
   WEATHER HISTORY
   ========================================================= */

export interface WeatherHistoryItem {
  field_id: string;
  location: string;
  timestamp: string;
  temperature: number;
  humidity: number;
  rainfall: number;
  rain_probability: number;
}

export interface WeatherHistoryResponse {
  field_id: string;
  count: number;
  history: WeatherHistoryItem[];
}

/* =========================================================
   GET ML IRRIGATION RECOMMENDATION
   ========================================================= */

export async function getIrrigationRecommendation(
  data: IrrigationRequest
): Promise<IrrigationResponse> {
  const response = await fetch(
    `${IRRIGATION_API_URL}/predict-irrigation`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    }
  );

  if (!response.ok) {
    const errorText = await response.text();

    throw new Error(
      `Irrigation API request failed: ${response.status} ${errorText}`
    );
  }

  return response.json();
}

/* =========================================================
   GET LATEST SENSOR DATA
   ========================================================= */

export async function getLatestSensorData(
  fieldId: string
): Promise<SensorResponse> {
  const response = await fetch(
    `${SENSOR_API_URL}/sensor-data/latest/${fieldId}`
  );

  if (!response.ok) {
    const errorText = await response.text();

    throw new Error(
      `Sensor API request failed: ${response.status} ${errorText}`
    );
  }

  return response.json();
}

/* =========================================================
   GET LATEST WEATHER FOR A SPECIFIC FIELD
   ========================================================= */

export async function getLatestWeather(
  fieldId: string
): Promise<WeatherResponse> {
  const response = await fetch(
    `${IRRIGATION_API_URL}/weather/latest/${fieldId}`
  );

  if (!response.ok) {
    const errorText = await response.text();

    throw new Error(
      `Weather API request failed: ${response.status} ${errorText}`
    );
  }

  return response.json();
}

/* =========================================================
   GET ALL FIELDS
   ========================================================= */

export async function getFields(): Promise<FieldResponse[]> {
  const response = await fetch(
    `${IRRIGATION_API_URL}/fields`
  );

  if (!response.ok) {
    const errorText = await response.text();

    throw new Error(
      `Fields API request failed: ${response.status} ${errorText}`
    );
  }

  const data = await response.json();

  return data.fields;
}

/* =========================================================
   CREATE FIELD
   ========================================================= */

export async function createField(
  data: CreateFieldRequest
): Promise<FieldResponse> {
  const response = await fetch(
    `${IRRIGATION_API_URL}/fields`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    }
  );

  if (!response.ok) {
    const errorText = await response.text();

    throw new Error(
      errorText ||
        `Create field request failed: ${response.status}`
    );
  }

  return response.json();
}

/* =========================================================
   CREATE IRRIGATION SCHEDULE
   ========================================================= */

export async function createIrrigationSchedule(
  data: ScheduleRequest
): Promise<ScheduleResponse> {
  const response = await fetch(
    `${IRRIGATION_API_URL}/schedule-irrigation`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    }
  );

  if (!response.ok) {
    const errorText = await response.text();

    throw new Error(
      errorText ||
        `Schedule API request failed: ${response.status}`
    );
  }

  return response.json();
}

/* =========================================================
   GET WEATHER HISTORY
   ========================================================= */

export async function getWeatherHistory(
  fieldId: string
): Promise<WeatherHistoryResponse> {
  const response = await fetch(
    `${IRRIGATION_API_URL}/weather/history/${fieldId}`
  );

  if (!response.ok) {
    const errorText = await response.text();

    throw new Error(
      `Weather history request failed: ${response.status} ${errorText}`
    );
  }

  return response.json();
}

/* =========================================================
   GET IRRIGATION HISTORY
   ========================================================= */

export async function getIrrigationHistory(
  fieldId: string
): Promise<IrrigationHistoryResponse> {
  const response = await fetch(
    `${IRRIGATION_API_URL}/irrigation-history/${fieldId}`
  );

  if (!response.ok) {
    const errorText = await response.text();

    throw new Error(
      `Irrigation history request failed: ${response.status} ${errorText}`
    );
  }

  return response.json();
}