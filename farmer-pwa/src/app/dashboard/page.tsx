"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import {
  createField,
  createIrrigationSchedule,
  getFields,
  getIrrigationRecommendation,
  getIrrigationHistory,
  getLatestSensorData,
  getLatestWeather,
  type FieldResponse,
  type IrrigationResponse,
  type ScheduleResponse,
  type SensorResponse,
  type WeatherResponse,
} from "../../api";

import BottomNav from "../../components/BottomNav";

type Field = {
  fieldId: string;
  farmerId: number;
  fieldName: string;
  fieldSize: number;
  crop: string;
  stage: number;
  soilMoisture?: number;
  sensorId?: string;
};

type Language = "English" | "Hindi" | "Kannada";

const translations = {
  English: {
    dashboard: "Farmer Dashboard",
    smartIrrigation: "Smart Irrigation",
    refresh: "↻ Refresh",
    welcome: "Welcome back, Farmer 👋",
    monitor: "Monitor your farm",
    subtitle:
      "Get data-driven irrigation recommendations for your fields.",
    fields: "Your Fields",
    selectField: "Select a field to view live data",
    add: "+ Add",
    selected: "SELECTED",
    stage: "Stage",
    acres: "acres",
    register: "Register New Field",
    addInfo: "Add your field information below.",
    fieldName: "Field Name",
    location: "Location",
    fieldSize: "Field Size (acres)",
    soilMoisture: "Soil Moisture (%)",
    crop: "Crop",
    growthStage: "Growth Stage",
    saveField: "Save Field",
    cancel: "Cancel",
    selectedField: "Selected Field",
    fieldSizeLabel: "Field Size",
    liveConditions: "Live Farm Conditions",
    liveSubtitle:
      "Latest available sensor and weather data",
    soil: "SOIL",
    temp: "TEMP",
    humidity: "HUMIDITY",
    rain: "RAIN",
    low: "Low",
    moderate: "Moderate",
    good: "Good",
    sensorStatus: "Sensor Status",
    sensorId: "Sensor ID",
    lastReading: "Last reading",
    weatherDetails: "Weather Details",
    rainfall: "Rainfall",
    rainProbability: "Rain probability",
    updated: "Updated",
    aiEngine: "AI / ML Engine",
    recommendation: "Irrigation Recommendation",
    recommendationText:
      "Generated using soil, weather, crop and growth-stage information.",
    calculating: "Calculating...",
    irrigationStatus: "Irrigation Status",
    required: "Required",
    notRequired: "Not Required",
    predictedWater: "Predicted Water",
    previousUsage: "Previous usage",
    waiting:
      "Waiting for current sensor and weather data to generate the recommendation.",
    schedulingEngine: "Scheduling Engine",
    todaySchedule: "Today's Irrigation Schedule",
    scheduleText:
      "Generate a field-specific irrigation schedule using the backend scheduling engine.",
    generateSchedule: "Generate Today's Schedule",
    generating: "Generating Schedule...",
    recommendedTime: "Recommended Time",
    waterQuantity: "Water Quantity",
    recommendationReason: "Recommendation Reason",
    farmerTools: "Farmer Tools",
    sensorHistory: "Sensor History",
    viewTrends: "View trends",
    irrigationHistory: "Irrigation History",
    previousRecords: "Previous records",
    farmerProfile: "Farmer Profile",
    manageProfile: "Manage profile",
    language: "Language",
    english: "English",
    hindi: "हिन्दी",
    kannada: "ಕನ್ನಡ",
  },

  Hindi: {
    dashboard: "किसान डैशबोर्ड",
    smartIrrigation: "स्मार्ट सिंचाई",
    refresh: "↻ रिफ्रेश",
    welcome: "वापसी पर स्वागत है, किसान 👋",
    monitor: "अपने खेत की निगरानी करें",
    subtitle:
      "अपने खेत के लिए डेटा आधारित सिंचाई सुझाव प्राप्त करें।",
    fields: "आपके खेत",
    selectField:
      "लाइव डेटा देखने के लिए खेत चुनें",
    add: "+ जोड़ें",
    selected: "चयनित",
    stage: "चरण",
    acres: "एकड़",
    register: "नया खेत पंजीकृत करें",
    addInfo:
      "अपने खेत की जानकारी नीचे दर्ज करें।",
    fieldName: "खेत का नाम",
    location: "स्थान",
    fieldSize: "खेत का आकार (एकड़)",
    soilMoisture: "मिट्टी की नमी (%)",
    crop: "फसल",
    growthStage: "फसल विकास चरण",
    saveField: "खेत सहेजें",
    cancel: "रद्द करें",
    selectedField: "चयनित खेत",
    fieldSizeLabel: "खेत का आकार",
    liveConditions: "खेत की वर्तमान स्थिति",
    liveSubtitle:
      "नवीनतम सेंसर और मौसम डेटा",
    soil: "मिट्टी",
    temp: "तापमान",
    humidity: "नमी",
    rain: "बारिश",
    low: "कम",
    moderate: "मध्यम",
    good: "अच्छा",
    sensorStatus: "सेंसर स्थिति",
    sensorId: "सेंसर आईडी",
    lastReading: "अंतिम रीडिंग",
    weatherDetails: "मौसम विवरण",
    rainfall: "वर्षा",
    rainProbability: "बारिश की संभावना",
    updated: "अपडेट किया गया",
    aiEngine: "AI / ML इंजन",
    recommendation: "सिंचाई सुझाव",
    recommendationText:
      "मिट्टी, मौसम, फसल और विकास चरण के आधार पर बनाया गया।",
    calculating: "गणना हो रही है...",
    irrigationStatus: "सिंचाई स्थिति",
    required: "आवश्यक",
    notRequired: "आवश्यक नहीं",
    predictedWater: "अनुमानित पानी",
    previousUsage: "पिछला उपयोग",
    waiting:
      "सुझाव तैयार करने के लिए वर्तमान सेंसर और मौसम डेटा की प्रतीक्षा है।",
    schedulingEngine: "शेड्यूलिंग इंजन",
    todaySchedule: "आज की सिंचाई योजना",
    scheduleText:
      "बैकएंड शेड्यूलिंग इंजन का उपयोग करके खेत के लिए सिंचाई योजना बनाएं।",
    generateSchedule: "आज की योजना बनाएं",
    generating: "योजना बनाई जा रही है...",
    recommendedTime: "सुझाया गया समय",
    waterQuantity: "पानी की मात्रा",
    recommendationReason: "सुझाव का कारण",
    farmerTools: "किसान उपकरण",
    sensorHistory: "सेंसर इतिहास",
    viewTrends: "रुझान देखें",
    irrigationHistory: "सिंचाई इतिहास",
    previousRecords: "पिछले रिकॉर्ड",
    farmerProfile: "किसान प्रोफ़ाइल",
    manageProfile: "प्रोफ़ाइल प्रबंधित करें",
    language: "भाषा",
    english: "English",
    hindi: "हिन्दी",
    kannada: "ಕನ್ನಡ",
  },

  Kannada: {
    dashboard: "ರೈತರ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",
    smartIrrigation: "ಸ್ಮಾರ್ಟ್ ನೀರಾವರಿ",
    refresh: "↻ ರಿಫ್ರೆಶ್",
    welcome: "ಮತ್ತೆ ಸ್ವಾಗತ, ರೈತರೆ 👋",
    monitor: "ನಿಮ್ಮ ಹೊಲವನ್ನು ಮೇಲ್ವಿಚಾರಣೆ ಮಾಡಿ",
    subtitle:
      "ನಿಮ್ಮ ಹೊಲಕ್ಕೆ ಡೇಟಾ ಆಧಾರಿತ ನೀರಾವರಿ ಸಲಹೆಗಳನ್ನು ಪಡೆಯಿರಿ.",
    fields: "ನಿಮ್ಮ ಹೊಲಗಳು",
    selectField:
      "ಲೈವ್ ಡೇಟಾ ನೋಡಲು ಹೊಲವನ್ನು ಆಯ್ಕೆಮಾಡಿ",
    add: "+ ಸೇರಿಸಿ",
    selected: "ಆಯ್ಕೆಮಾಡಲಾಗಿದೆ",
    stage: "ಹಂತ",
    acres: "ಎಕರೆ",
    register: "ಹೊಸ ಹೊಲವನ್ನು ನೋಂದಾಯಿಸಿ",
    addInfo:
      "ನಿಮ್ಮ ಹೊಲದ ಮಾಹಿತಿಯನ್ನು ಕೆಳಗೆ ನಮೂದಿಸಿ.",
    fieldName: "ಹೊಲದ ಹೆಸರು",
    location: "ಸ್ಥಳ",
    fieldSize: "ಹೊಲದ ಗಾತ್ರ (ಎಕರೆ)",
    soilMoisture: "ಮಣ್ಣಿನ ತೇವಾಂಶ (%)",
    crop: "ಬೆಳೆ",
    growthStage: "ಬೆಳೆ ಬೆಳವಣಿಗೆಯ ಹಂತ",
    saveField: "ಹೊಲವನ್ನು ಉಳಿಸಿ",
    cancel: "ರದ್ದುಮಾಡಿ",
    selectedField: "ಆಯ್ಕೆಮಾಡಿದ ಹೊಲ",
    fieldSizeLabel: "ಹೊಲದ ಗಾತ್ರ",
    liveConditions: "ಹೊಲದ ಪ್ರಸ್ತುತ ಪರಿಸ್ಥಿತಿಗಳು",
    liveSubtitle:
      "ಇತ್ತೀಚಿನ ಸೆನ್ಸರ್ ಮತ್ತು ಹವಾಮಾನ ಡೇಟಾ",
    soil: "ಮಣ್ಣು",
    temp: "ತಾಪಮಾನ",
    humidity: "ತೇವಾಂಶ",
    rain: "ಮಳೆ",
    low: "ಕಡಿಮೆ",
    moderate: "ಮಧ್ಯಮ",
    good: "ಉತ್ತಮ",
    sensorStatus: "ಸೆನ್ಸರ್ ಸ್ಥಿತಿ",
    sensorId: "ಸೆನ್ಸರ್ ಐಡಿ",
    lastReading: "ಕೊನೆಯ ರೀಡಿಂಗ್",
    weatherDetails: "ಹವಾಮಾನ ವಿವರಗಳು",
    rainfall: "ಮಳೆಯ ಪ್ರಮಾಣ",
    rainProbability: "ಮಳೆಯ ಸಾಧ್ಯತೆ",
    updated: "ನವೀಕರಿಸಲಾಗಿದೆ",
    aiEngine: "AI / ML ಎಂಜಿನ್",
    recommendation: "ನೀರಾವರಿ ಸಲಹೆ",
    recommendationText:
      "ಮಣ್ಣು, ಹವಾಮಾನ, ಬೆಳೆ ಮತ್ತು ಬೆಳವಣಿಗೆಯ ಹಂತದ ಆಧಾರದ ಮೇಲೆ ರಚಿಸಲಾಗಿದೆ.",
    calculating: "ಲೆಕ್ಕಾಚಾರ ಮಾಡಲಾಗುತ್ತಿದೆ...",
    irrigationStatus: "ನೀರಾವರಿ ಸ್ಥಿತಿ",
    required: "ಅಗತ್ಯವಿದೆ",
    notRequired: "ಅಗತ್ಯವಿಲ್ಲ",
    predictedWater: "ಅಂದಾಜು ನೀರು",
    previousUsage: "ಹಿಂದಿನ ಬಳಕೆ",
    waiting:
      "ಸಲಹೆಯನ್ನು ರಚಿಸಲು ಪ್ರಸ್ತುತ ಸೆನ್ಸರ್ ಮತ್ತು ಹವಾಮಾನ ಡೇಟಾಕ್ಕಾಗಿ ಕಾಯಲಾಗುತ್ತಿದೆ.",
    schedulingEngine: "ಶೆಡ್ಯೂಲಿಂಗ್ ಎಂಜಿನ್",
    todaySchedule: "ಇಂದಿನ ನೀರಾವರಿ ವೇಳಾಪಟ್ಟಿ",
    scheduleText:
      "ಬ್ಯಾಕೆಂಡ್ ಶೆಡ್ಯೂಲಿಂಗ್ ಎಂಜಿನ್ ಬಳಸಿ ಹೊಲಕ್ಕೆ ನೀರಾವರಿ ವೇಳಾಪಟ್ಟಿಯನ್ನು ರಚಿಸಿ.",
    generateSchedule: "ಇಂದಿನ ವೇಳಾಪಟ್ಟಿ ರಚಿಸಿ",
    generating: "ವೇಳಾಪಟ್ಟಿ ರಚಿಸಲಾಗುತ್ತಿದೆ...",
    recommendedTime: "ಶಿಫಾರಸು ಮಾಡಿದ ಸಮಯ",
    waterQuantity: "ನೀರಿನ ಪ್ರಮಾಣ",
    recommendationReason: "ಸಲಹೆಯ ಕಾರಣ",
    farmerTools: "ರೈತರ ಉಪಕರಣಗಳು",
    sensorHistory: "ಸೆನ್ಸರ್ ಇತಿಹಾಸ",
    viewTrends: "ಪ್ರವೃತ್ತಿಗಳನ್ನು ನೋಡಿ",
    irrigationHistory: "ನೀರಾವರಿ ಇತಿಹಾಸ",
    previousRecords: "ಹಿಂದಿನ ದಾಖಲೆಗಳು",
    farmerProfile: "ರೈತರ ಪ್ರೊಫೈಲ್",
    manageProfile: "ಪ್ರೊಫೈಲ್ ನಿರ್ವಹಿಸಿ",
    language: "ಭಾಷೆ",
    english: "English",
    hindi: "हिन्दी",
    kannada: "ಕನ್ನಡ",
  },
};

const supportedCrops = [
  "rice",
  "maize",
  "chickpea",
  "kidneybeans",
  "pigeonpeas",
  "mothbeans",
  "mungbean",
  "blackgram",
  "lentil",
  "pomegranate",
  "banana",
  "mango",
  "grapes",
  "watermelon",
  "muskmelon",
  "apple",
  "orange",
  "papaya",
  "coconut",
  "cotton",
  "jute",
  "coffee",
];

function mapField(field: FieldResponse): Field {
  return {
    fieldId: field.field_id,
    farmerId: field.farmer_id,
    fieldName: field.field_name,
    fieldSize: field.field_size,
    crop: field.crop_type,
    stage: Number(field.growth_stage),
    soilMoisture: field.soil_moisture,
    sensorId: field.sensor_id,
  };
}

function formatCrop(crop: string) {
  return crop
    .replace(/_/g, " ")
    .replace(/\b\w/g, (letter) =>
      letter.toUpperCase()
    );
}

function formatDateTime(
  value: string | null | undefined
) {
  if (!value) return "Not available";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export default function Home() {
  const [language, setLanguage] =
    useState<Language>("English");

  const t = translations[language];

  const [fields, setFields] = useState<Field[]>([]);
  const [selectedField, setSelectedField] =
    useState<Field | null>(null);

  const [sensor, setSensor] =
    useState<SensorResponse | null>(null);

  const [weather, setWeather] =
    useState<WeatherResponse | null>(null);

  const [recommendation, setRecommendation] =
    useState<IrrigationResponse | null>(null);

  const [schedule, setSchedule] =
    useState<ScheduleResponse | null>(null);

  const [loadingFields, setLoadingFields] =
    useState(true);

  const [loadingSensor, setLoadingSensor] =
    useState(false);

  const [loadingWeather, setLoadingWeather] =
    useState(false);

  const [loadingRecommendation, setLoadingRecommendation] =
    useState(false);

  const [scheduleLoading, setScheduleLoading] =
    useState(false);

  const [error, setError] = useState("");
  const [scheduleError, setScheduleError] =
    useState("");

  const [showAddField, setShowAddField] =
    useState(false);

  const [newField, setNewField] = useState({
    field_name: "",
    soil_moisture: "15",
    location: "Bengaluru",
    field_size: "1",
    crop_type: "rice",
    growth_stage: "1",
  });

  async function loadFields() {
    setLoadingFields(true);
    setError("");

    try {
      const response = await getFields();

      const mappedFields =
        response.map(mapField);

      setFields(mappedFields);

      if (mappedFields.length > 0) {
        const preferredField =
          mappedFields.find(
            (field) =>
              field.fieldId === "FIELD003"
          );

        setSelectedField(
          preferredField ?? mappedFields[0]
        );
      }
    } catch (err) {
      console.error(
        "Field loading error:",
        err
      );

      setError(
        err instanceof Error
          ? err.message
          : "Unable to load fields."
      );
    } finally {
      setLoadingFields(false);
    }
  }

  useEffect(() => {
    loadFields();
  }, []);

  async function loadRecommendation(
    field: Field,
    currentSensor: SensorResponse | null,
    currentWeather: WeatherResponse | null
  ) {
    if (!currentSensor || !currentWeather) {
      return;
    }

    setLoadingRecommendation(true);

    try {
      const now = new Date();

      let previousWaterUsage = 0;

      try {
        const history = await getIrrigationHistory(
          field.fieldId
        );

        if (history.history?.length) {
          const sortedHistory = [...history.history].sort(
            (a, b) =>
              new Date(b.irrigation_timestamp).getTime() -
              new Date(a.irrigation_timestamp).getTime()
          );

          previousWaterUsage =
            Number(sortedHistory[0].water_used_liters) || 0;
        }
      } catch (historyError) {
        console.warn(
          "Previous irrigation history unavailable:",
          historyError
        );
      }

      const result =
        await getIrrigationRecommendation({
          field_id: field.fieldId,
          soil_moisture:
            Number(currentSensor.soil_moisture),
          temperature:
            Number(currentWeather.temperature),
          humidity:
            Number(currentWeather.humidity),
          rainfall:
            Number(currentWeather.rainfall),
          rain_probability:
            Number(currentWeather.rain_probability),
          crop_type:
            field.crop.toLowerCase(),
          growth_stage:
            Number(field.stage),
          hour: now.getHours(),
          day_of_week:
            now.getDay(),
          day_of_month:
            now.getDate(),
          previous_water_usage_liters:
            previousWaterUsage,
        });

      setRecommendation(result);
    } catch (err) {
      console.error(
        "Recommendation error:",
        err
      );

      setRecommendation(null);
    } finally {
      setLoadingRecommendation(false);
    }
  }

  async function refreshDashboard(
    field: Field
  ) {
    setError("");
    setSchedule(null);
    setScheduleError("");
    setRecommendation(null);

    try {
      setLoadingSensor(true);

      const sensorResult =
        await getLatestSensorData(
          field.fieldId
        );

      setSensor(sensorResult);
      setLoadingSensor(false);

      setLoadingWeather(true);

      let weatherResult:
        | WeatherResponse
        | null = null;

      try {
        weatherResult =
          await getLatestWeather(field.fieldId);

        setWeather(weatherResult);
      } catch (weatherError) {
        console.error(
          "Weather loading error:",
          weatherError
        );

        setWeather(null);
      } finally {
        setLoadingWeather(false);
      }

      if (weatherResult) {
        await loadRecommendation(
          field,
          sensorResult,
          weatherResult
        );
      }
    } catch (err) {
      console.error(
        "Dashboard refresh error:",
        err
      );

      setSensor(null);

      setError(
        err instanceof Error
          ? err.message
          : "Unable to load field data."
      );

      setLoadingSensor(false);
    }
  }

  useEffect(() => {
    if (!selectedField) return;

    refreshDashboard(selectedField);
  }, [selectedField]);

  async function handleAddField(
    event: React.FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    setError("");

    try {
      const created =
        await createField({
          field_name:
            newField.field_name,
          soil_moisture:
            Number(
              newField.soil_moisture
            ),
          location:
            newField.location,
          field_size:
            Number(
              newField.field_size
            ),
          crop_type:
            newField.crop_type,
          growth_stage:
            newField.growth_stage,
        });

      const mapped =
        mapField(created);

      setFields((previous) => [
        ...previous,
        mapped,
      ]);

      setSelectedField(mapped);

      setNewField({
        field_name: "",
        soil_moisture: "15",
        location: "Bengaluru",
        field_size: "1",
        crop_type: "rice",
        growth_stage: "1",
      });

      setShowAddField(false);
    } catch (err) {
      console.error(
        "Create field error:",
        err
      );

      setError(
        err instanceof Error
          ? err.message
          : "Unable to create field."
      );
    }
  }

  async function handleCreateSchedule() {
    if (!selectedField) return;

    setScheduleLoading(true);
    setScheduleError("");
    setSchedule(null);

    try {
      const result =
        await createIrrigationSchedule({
          field_id:
            selectedField.fieldId,
          crop_type:
            selectedField.crop.toLowerCase(),
          growth_stage:
            selectedField.stage,
          previous_water_usage_liters:
            recommendation?.previous_water_usage_liters ??
            0,
        });

      setSchedule(result);
    } catch (err) {
      console.error(
        "Schedule creation error:",
        err
      );

      setScheduleError(
        err instanceof Error
          ? err.message
          : "Unable to generate the irrigation schedule."
      );
    } finally {
      setScheduleLoading(false);
    }
  }

  const soilMoisture =
    sensor?.soil_moisture ??
    selectedField?.soilMoisture ??
    0;

  const moistureStatus =
    useMemo(() => {
      if (soilMoisture < 20) {
        return {
          label: t.low,
        };
      }

      if (soilMoisture < 40) {
        return {
          label: t.moderate,
        };
      }

      return {
        label: t.good,
      };
    }, [
      soilMoisture,
      t.low,
      t.moderate,
      t.good,
    ]);

  if (loadingFields) {
    return (
      <main className="min-h-screen bg-[#071a12] px-4 py-8">

        <div className="mx-auto flex min-h-[70vh] max-w-5xl items-center justify-center">

          <div className="rounded-3xl border border-white/10 bg-white/[0.08] p-8 text-center text-white shadow-2xl backdrop-blur-xl">

            <div className="mx-auto mb-4 h-10 w-10 animate-spin rounded-full border-4 border-emerald-200 border-t-emerald-600" />

            <p className="font-medium text-white/80">
              Loading your fields...
            </p>

          </div>

        </div>

        <BottomNav />

      </main>
    );
  }

  return (
    <main className="relative min-h-screen overflow-hidden bg-[#edf7ef] text-slate-900">
      <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_8%_8%,rgba(52,211,153,0.18),transparent_26%),radial-gradient(circle_at_92%_18%,rgba(20,184,166,0.14),transparent_25%),linear-gradient(180deg,#f5fbf6_0%,#edf7ef_52%,#e4f1e7_100%)]" />
        <div className="absolute -left-32 top-64 h-80 w-80 rounded-full bg-emerald-300/10 blur-3xl" />
        <div className="absolute -right-32 top-[42rem] h-96 w-96 rounded-full bg-teal-300/10 blur-3xl" />
        <svg className="absolute bottom-0 left-0 h-56 w-full opacity-[0.08]" viewBox="0 0 1440 260" preserveAspectRatio="none" aria-hidden="true">
          <path d="M0 170 C160 115 285 150 430 120 C600 84 710 145 860 105 C1030 60 1170 115 1320 72 C1380 55 1420 58 1440 50 L1440 260 L0 260 Z" fill="currentColor" className="text-emerald-900" />
          <path d="M0 205 C190 150 330 190 510 150 C700 110 820 178 1000 135 C1160 98 1300 150 1440 105 L1440 260 L0 260 Z" fill="currentColor" className="text-green-900" />
        </svg>
      </div>

      {/* HEADER */}

      <header className="sticky top-0 z-40 border-b border-white/70 bg-white/75 shadow-sm backdrop-blur-2xl">

        <div className="mx-auto flex max-w-6xl items-center justify-between gap-3 px-4 py-3 sm:px-6">

          <div className="flex items-center gap-3">

            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-emerald-950 text-xl text-white shadow-lg shadow-emerald-950/15">
              🌿
            </div>

            <div>

              <p className="text-[10px] font-bold uppercase tracking-[0.22em] text-emerald-700">
                {t.smartIrrigation}
              </p>

              <h1 className="text-lg font-black tracking-tight text-emerald-950 sm:text-xl">
                {t.dashboard}
              </h1>

            </div>

          </div>

          <div className="flex items-center gap-2">

            {/* LANGUAGE */}

            <select
              value={language}
              onChange={(event) =>
                setLanguage(
                  event.target.value as Language
                )
              }
              className="rounded-xl border border-slate-200 bg-white px-2 py-2 text-xs font-semibold shadow-sm outline-none"
              aria-label={t.language}
            >

              <option value="English">
                {t.english}
              </option>

              <option value="Hindi">
                {t.hindi}
              </option>

              <option value="Kannada">
                {t.kannada}
              </option>

            </select>

            <button
              onClick={() =>
                selectedField &&
                refreshDashboard(
                  selectedField
                )
              }
              className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-medium shadow-sm transition hover:bg-slate-50"
            >
              {t.refresh}
            </button>

          </div>

        </div>

      </header>

      <div className="mx-auto max-w-6xl px-4 pb-24 pt-5 sm:px-6 sm:py-8">

        {/* ERROR */}

        {error && (
          <div className="mb-5 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        )}

        {/* COMMAND CENTER HERO */}

        <section className="relative mb-6 overflow-hidden rounded-[2rem] bg-emerald-950 p-6 text-white shadow-xl shadow-emerald-950/15 sm:p-8">

          <div className="absolute -right-16 -top-20 h-56 w-56 rounded-full bg-emerald-500/20 blur-2xl" />
          <div className="absolute -bottom-24 left-1/3 h-48 w-48 rounded-full bg-lime-400/10 blur-3xl" />

          <div className="relative grid gap-7 lg:grid-cols-[1fr_auto] lg:items-end">

            <div>

              <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-3 py-1.5 text-[10px] font-bold uppercase tracking-[0.18em] text-emerald-100">
                <span className="h-2 w-2 animate-pulse rounded-full bg-lime-300" />
                Live Farm Command Center
              </div>

              <p className="text-sm text-emerald-200">
                {t.welcome}
              </p>

              <h2 className="mt-1 max-w-2xl text-3xl font-black tracking-tight sm:text-4xl">
                {t.monitor}
              </h2>

              <p className="mt-3 max-w-2xl text-sm leading-6 text-emerald-100/80">
                {t.subtitle}
              </p>

            </div>

            {selectedField && (
              <div className="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur-md lg:min-w-[190px]">

                <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-emerald-200">
                  Monitoring
                </p>

                <p className="mt-1 text-lg font-black">
                  {selectedField.fieldName}
                </p>

                <p className="mt-1 text-xs text-emerald-100/70">
                  {formatCrop(selectedField.crop)} • Stage {selectedField.stage}
                </p>

              </div>
            )}

          </div>

        </section>

        {/* FIELD SELECTOR */}

        <section className="mb-5 rounded-[1.75rem] border border-white/80 bg-white/80 p-4 shadow-lg shadow-emerald-950/5 backdrop-blur-xl">

          <div className="mb-3 flex items-center justify-between gap-3">

            <div>

              <h3 className="font-semibold">
                {t.fields}
              </h3>

              <p className="text-xs text-slate-500">
                {t.selectField}
              </p>

            </div>

            <button
              onClick={() =>
                setShowAddField(
                  (value) => !value
                )
              }
              className="rounded-xl bg-emerald-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-emerald-700"
            >
              {t.add}
            </button>

          </div>

          {fields.length > 0 ? (

            <div className="flex gap-3 overflow-x-auto pb-1">

              {fields.map((field) => {

                const selected =
                  selectedField?.fieldId ===
                  field.fieldId;

                return (
                  <button
                    key={field.fieldId}
                    onClick={() =>
                      setSelectedField(
                        field
                      )
                    }
                    className={`min-w-[190px] rounded-2xl border p-4 text-left transition ${
                      selected
                        ? "border-emerald-500 bg-emerald-50 shadow-sm"
                        : "border-slate-200 bg-white hover:border-emerald-300"
                    }`}
                  >

                    <div className="flex items-start justify-between gap-2">

                      <span className="text-xl">
                        🌱
                      </span>

                      {selected && (
                        <span className="rounded-full bg-emerald-600 px-2 py-1 text-[10px] font-bold text-white">
                          {t.selected}
                        </span>
                      )}

                    </div>

                    <p className="mt-3 font-semibold">
                      {field.fieldName}
                    </p>

                    <p className="mt-1 text-xs text-slate-500">
                      {formatCrop(
                        field.crop
                      )}
                    </p>

                    <p className="mt-1 text-xs text-slate-500">
                      {t.stage}{" "}
                      {field.stage} •{" "}
                      {field.fieldSize}{" "}
                      {t.acres}
                    </p>

                  </button>
                );
              })}

            </div>

          ) : (

            <div className="rounded-xl bg-slate-50 p-5 text-center text-sm text-slate-500">
              No fields registered yet.
            </div>

          )}

        </section>

        {/* ADD FIELD */}

        {showAddField && (

          <section className="mb-5 rounded-[1.75rem] border border-emerald-200/70 bg-white/85 p-5 shadow-lg shadow-emerald-950/5 backdrop-blur-xl">

            <div className="mb-4">

              <h3 className="text-lg font-bold">
                {t.register}
              </h3>

              <p className="text-sm text-slate-500">
                {t.addInfo}
              </p>

            </div>

            <form
              onSubmit={
                handleAddField
              }
              className="grid gap-4 sm:grid-cols-2"
            >

              <label className="text-sm font-medium">
                {t.fieldName}

                <input
                  required
                  value={
                    newField.field_name
                  }
                  onChange={(event) =>
                    setNewField({
                      ...newField,
                      field_name:
                        event.target
                          .value,
                    })
                  }
                  className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-3 outline-none focus:border-emerald-500"
                />

              </label>

              <label className="text-sm font-medium">
                {t.location}

                <input
                  value={
                    newField.location
                  }
                  onChange={(event) =>
                    setNewField({
                      ...newField,
                      location:
                        event.target
                          .value,
                    })
                  }
                  className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-3 outline-none focus:border-emerald-500"
                />

              </label>

              <label className="text-sm font-medium">
                {t.fieldSize}

                <input
                  required
                  type="number"
                  min="0.1"
                  step="0.1"
                  value={
                    newField.field_size
                  }
                  onChange={(event) =>
                    setNewField({
                      ...newField,
                      field_size:
                        event.target
                          .value,
                    })
                  }
                  className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-3 outline-none focus:border-emerald-500"
                />

              </label>

              <label className="text-sm font-medium">
                {t.soilMoisture}

                <input
                  required
                  type="number"
                  min="0"
                  max="100"
                  value={
                    newField.soil_moisture
                  }
                  onChange={(event) =>
                    setNewField({
                      ...newField,
                      soil_moisture:
                        event.target
                          .value,
                    })
                  }
                  className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-3 outline-none focus:border-emerald-500"
                />

              </label>

              <label className="text-sm font-medium">

                {t.crop}

                <select
                  value={
                    newField.crop_type
                  }
                  onChange={(event) =>
                    setNewField({
                      ...newField,
                      crop_type:
                        event.target
                          .value,
                    })
                  }
                  className="mt-1 w-full rounded-xl border border-slate-300 bg-white px-3 py-3 outline-none focus:border-emerald-500"
                >

                  {supportedCrops.map(
                    (crop) => (

                      <option
                        key={crop}
                        value={crop}
                      >
                        {formatCrop(
                          crop
                        )}
                      </option>

                    )
                  )}

                </select>

              </label>

              <label className="text-sm font-medium">

                {t.growthStage}

                <select
                  value={
                    newField.growth_stage
                  }
                  onChange={(event) =>
                    setNewField({
                      ...newField,
                      growth_stage:
                        event.target
                          .value,
                    })
                  }
                  className="mt-1 w-full rounded-xl border border-slate-300 bg-white px-3 py-3 outline-none focus:border-emerald-500"
                >

                  <option value="1">
                    {t.stage} 1
                  </option>

                  <option value="2">
                    {t.stage} 2
                  </option>

                  <option value="3">
                    {t.stage} 3
                  </option>

                </select>

              </label>

              <div className="flex gap-3 sm:col-span-2">

                <button
                  type="submit"
                  className="flex-1 rounded-xl bg-emerald-600 px-4 py-3 font-semibold text-white hover:bg-emerald-700"
                >
                  {t.saveField}
                </button>

                <button
                  type="button"
                  onClick={() =>
                    setShowAddField(
                      false
                    )
                  }
                  className="rounded-xl border border-slate-300 px-4 py-3 font-semibold text-slate-700"
                >
                  {t.cancel}
                </button>

              </div>

            </form>

          </section>

        )}

        {selectedField && (

          <>

            {/* FIELD SUMMARY */}

            <section className="mb-6 overflow-hidden rounded-[2rem] bg-gradient-to-br from-[#064e3b] via-emerald-700 to-[#4d7c0f] p-5 text-white shadow-2xl shadow-emerald-950/20 sm:p-6">

              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">

                <div>

                  <p className="text-sm text-emerald-100">
                    {t.selectedField}
                  </p>

                  <h2 className="mt-1 text-2xl font-bold">
                    {selectedField.fieldName}
                  </h2>

                  <p className="mt-1 text-sm text-emerald-100">
                    {formatCrop(
                      selectedField.crop
                    )}
                    {" • "}
                    {t.stage}{" "}
                    {selectedField.stage}
                  </p>

                </div>

                <div className="rounded-2xl bg-white/15 p-4 backdrop-blur">

                  <p className="text-xs text-emerald-100">
                    {t.fieldSizeLabel}
                  </p>

                  <p className="text-xl font-bold">
                    {
                      selectedField.fieldSize
                    }{" "}
                    {t.acres}
                  </p>

                </div>

              </div>

            </section>

            {/* LIVE CONDITIONS */}

            <section className="mb-6">

              <div className="mb-3 flex items-end justify-between gap-3">

                <div>

                  <h2 className="text-lg font-black tracking-tight">
                  {t.liveConditions}
                </h2>

                  <p className="text-sm text-slate-500">
                    {t.liveSubtitle}
                  </p>

                </div>

                <span className="hidden rounded-full bg-emerald-100 px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-emerald-700 sm:inline-flex">
                  Field telemetry
                </span>

              </div>

              <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">

                <div className="rounded-2xl border border-white/80 bg-white/80 p-4 shadow-lg shadow-slate-900/5 backdrop-blur-xl transition hover:-translate-y-0.5 hover:shadow-xl">

                  <div className="flex items-center justify-between">

                    <span className="text-2xl">
                      💧
                    </span>

                    <span className="text-xs font-semibold text-slate-500">
                      {t.soil}
                    </span>

                  </div>

                  <p className="mt-4 text-2xl font-bold">

                    {loadingSensor
                      ? "..."
                      : `${soilMoisture.toFixed(
                          1
                        )}%`}

                  </p>

                  <p className="mt-1 text-xs font-medium text-slate-500">
                    {
                      moistureStatus.label
                    }
                  </p>

                </div>

                <div className="rounded-2xl border border-white/80 bg-white/80 p-4 shadow-lg shadow-slate-900/5 backdrop-blur-xl transition hover:-translate-y-0.5 hover:shadow-xl">

                  <div className="flex items-center justify-between">

                    <span className="text-2xl">
                      🌡️
                    </span>

                    <span className="text-xs font-semibold text-slate-500">
                      {t.temp}
                    </span>

                  </div>

                  <p className="mt-4 text-2xl font-bold">

                    {loadingWeather
                      ? "..."
                      : weather
                      ? `${weather.temperature.toFixed(
                          1
                        )}°C`
                      : "--"}

                  </p>

                </div>

                <div className="rounded-2xl border border-white/80 bg-white/80 p-4 shadow-lg shadow-slate-900/5 backdrop-blur-xl transition hover:-translate-y-0.5 hover:shadow-xl">

                  <div className="flex items-center justify-between">

                    <span className="text-2xl">
                      💦
                    </span>

                    <span className="text-xs font-semibold text-slate-500">
                      {t.humidity}
                    </span>

                  </div>

                  <p className="mt-4 text-2xl font-bold">

                    {loadingWeather
                      ? "..."
                      : weather
                      ? `${weather.humidity}%`
                      : "--"}

                  </p>

                </div>

                <div className="rounded-2xl border border-white/80 bg-white/80 p-4 shadow-lg shadow-slate-900/5 backdrop-blur-xl transition hover:-translate-y-0.5 hover:shadow-xl">

                  <div className="flex items-center justify-between">

                    <span className="text-2xl">
                      🌧️
                    </span>

                    <span className="text-xs font-semibold text-slate-500">
                      {t.rain}
                    </span>

                  </div>

                  <p className="mt-4 text-2xl font-bold">

                    {loadingWeather
                      ? "..."
                      : weather
                      ? `${weather.rain_probability}%`
                      : "--"}

                  </p>

                </div>

              </div>

            </section>

            {/* SENSOR + WEATHER */}

            <section className="mb-5 grid gap-4 lg:grid-cols-2">

              <div className="rounded-[1.5rem] border border-white/80 bg-white/80 p-5 shadow-lg shadow-slate-900/5 backdrop-blur-xl">

                <h3 className="font-bold">
                  {t.sensorStatus}
                </h3>

                <div className="mt-4 space-y-3 text-sm">

                  <div className="flex justify-between gap-4">

                    <span className="text-slate-500">
                      {t.sensorId}
                    </span>

                    <span className="font-medium">
                      {sensor?.sensor_id ??
                        selectedField.sensorId ??
                        "Not available"}
                    </span>

                  </div>

                  <div className="flex justify-between gap-4">

                    <span className="text-slate-500">
                      {t.lastReading}
                    </span>

                    <span className="text-right font-medium">
                      {formatDateTime(
                        sensor?.timestamp
                      )}
                    </span>

                  </div>

                  <div className="flex justify-between gap-4">

                    <span className="text-slate-500">
                      {t.soilMoisture}
                    </span>

                    <span className="font-medium">
                      {soilMoisture.toFixed(
                        1
                      )}
                      %
                    </span>

                  </div>

                </div>

              </div>

              <div className="rounded-[1.5rem] border border-white/80 bg-white/80 p-5 shadow-lg shadow-slate-900/5 backdrop-blur-xl">

                <h3 className="font-bold">
                  {t.weatherDetails}
                </h3>

                <div className="mt-4 space-y-3 text-sm">

                  <div className="flex justify-between gap-4">

                    <span className="text-slate-500">
                      {t.location}
                    </span>

                    <span className="font-medium">
                      {weather?.location ??
                        "Bengaluru"}
                    </span>

                  </div>

                  <div className="flex justify-between gap-4">

                    <span className="text-slate-500">
                      {t.rainfall}
                    </span>

                    <span className="font-medium">
                      {weather
                        ? `${weather.rainfall} mm`
                        : "--"}
                    </span>

                  </div>

                  <div className="flex justify-between gap-4">

                    <span className="text-slate-500">
                      {t.rainProbability}
                    </span>

                    <span className="font-medium">
                      {weather
                        ? `${weather.rain_probability}%`
                        : "--"}
                    </span>

                  </div>

                  <div className="flex justify-between gap-4">

                    <span className="text-slate-500">
                      {t.updated}
                    </span>

                    <span className="text-right font-medium">
                      {formatDateTime(
                        weather?.timestamp
                      )}
                    </span>

                  </div>

                </div>

              </div>

            </section>

            {/* ML RECOMMENDATION */}

            <section className="mb-6 overflow-hidden rounded-[2rem] border border-emerald-200/70 bg-white/90 p-5 shadow-2xl shadow-emerald-950/10 backdrop-blur-xl sm:p-6">

              <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">

                <div>

                  <p className="text-xs font-bold uppercase tracking-wider text-emerald-600">
                    {t.aiEngine}
                  </p>

                  <h2 className="mt-1 text-xl font-bold">
                    {t.recommendation}
                  </h2>

                  <p className="mt-1 text-sm text-slate-500">
                    {t.recommendationText}
                  </p>

                </div>

                {loadingRecommendation && (

                  <span className="text-sm text-slate-500">
                    {t.calculating}
                  </span>

                )}

              </div>

              {recommendation ? (

                <div className="mt-5 grid gap-4 sm:grid-cols-2">

                  <div className="sm:col-span-2 flex items-center gap-2 rounded-xl bg-slate-950 px-4 py-3 text-xs font-semibold text-white">
                    <span className="h-2 w-2 rounded-full bg-lime-400" />
                    Decision generated from current field conditions
                  </div>

                  <div
                    className={`rounded-2xl p-5 ${
                      recommendation.irrigation_required
                        ? "bg-amber-50"
                        : "bg-emerald-50"
                    }`}
                  >

                    <p className="text-sm font-medium text-slate-500">
                      {t.irrigationStatus}
                    </p>

                    <p className="mt-2 text-2xl font-bold">

                      {recommendation.irrigation_required
                        ? t.required
                        : t.notRequired}

                    </p>

                    <p className="mt-2 text-sm text-slate-600">
                      {recommendation.reason}
                    </p>

                  </div>

                  <div className="rounded-2xl bg-sky-50 p-5">

                    <p className="text-sm font-medium text-slate-500">
                      {t.predictedWater}
                    </p>

                    <p className="mt-2 text-3xl font-bold">

                      {recommendation.predicted_water_quantity_liters.toFixed(
                        2
                      )}

                      <span className="ml-1 text-base font-medium">
                        L
                      </span>

                    </p>

                    <p className="mt-2 text-sm text-slate-600">

                      {t.previousUsage}:{" "}

                      {recommendation.previous_water_usage_liters.toFixed(
                        2
                      )}

                      {" "}L

                    </p>

                  </div>

                </div>

              ) : (

                <div className="mt-5 rounded-2xl bg-slate-50 p-5 text-sm text-slate-500">
                  {t.waiting}
                </div>

              )}

            </section>

            {/* SCHEDULE */}

            <section className="mb-5 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">

              <p className="text-xs font-bold uppercase tracking-wider text-blue-600">
                {t.schedulingEngine}
              </p>

              <h2 className="mt-1 text-xl font-bold">
                {t.todaySchedule}
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                {t.scheduleText}
              </p>

              <button
                onClick={
                  handleCreateSchedule
                }
                disabled={
                  scheduleLoading
                }
                className="mt-5 w-full rounded-xl bg-blue-600 px-4 py-3 font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
              >

                {scheduleLoading
                  ? t.generating
                  : t.generateSchedule}

              </button>

              {scheduleError && (

                <div className="mt-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                  {scheduleError}
                </div>

              )}

              {schedule && (

                <div className="mt-5">

                  <div
                    className={`rounded-2xl p-5 ${
                      schedule.irrigation_required
                        ? "bg-emerald-50"
                        : "bg-slate-50"
                    }`}
                  >

                    <div className="flex items-center justify-between gap-3">

                      <h3 className="font-bold">
                        {schedule.irrigation_required
                          ? t.required
                          : t.notRequired}
                      </h3>

                      <span className="rounded-full bg-white px-3 py-1 text-xs font-semibold capitalize shadow-sm">
                        {schedule.schedule_status}
                      </span>

                    </div>

                    <div className="mt-5 grid grid-cols-2 gap-3">

                      <div className="rounded-xl bg-white p-4">

                        <p className="text-xs text-slate-500">
                          {t.waterQuantity}
                        </p>

                        <p className="mt-1 text-xl font-bold">
                          {schedule.recommended_water_quantity_liters.toFixed(
                            2
                          )}{" "}
                          L
                        </p>

                      </div>

                      <div className="rounded-xl bg-white p-4">

                        <p className="text-xs text-slate-500">
                          {t.recommendedTime}
                        </p>

                        <p className="mt-1 text-sm font-bold">

                          {schedule.recommended_time
                            ? formatDateTime(
                                schedule.recommended_time
                              )
                            : t.notRequired}

                        </p>

                      </div>

                      <div className="rounded-xl bg-white p-4">

                        <p className="text-xs text-slate-500">
                          {t.soilMoisture}
                        </p>

                        <p className="mt-1 text-xl font-bold">
                          {schedule.soil_moisture}%
                        </p>

                      </div>

                      <div className="rounded-xl bg-white p-4">

                        <p className="text-xs text-slate-500">
                          {t.rainProbability}
                        </p>

                        <p className="mt-1 text-xl font-bold">
                          {schedule.rain_probability}%
                        </p>

                      </div>

                    </div>

                    <div className="mt-4 rounded-xl bg-white p-4">

                      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                        {t.recommendationReason}
                      </p>

                      <p className="mt-2 text-sm text-slate-700">
                        {schedule.reason}
                      </p>

                    </div>

                  </div>

                </div>

              )}

            </section>

            {/* FARMER TOOLS */}

            <section className="mb-5">

              <h2 className="mb-3 text-lg font-bold">
                {t.farmerTools}
              </h2>

              <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">

                {/* SENSOR HISTORY */}

                <Link
                  href="/sensor-history"
                  className="block rounded-2xl border border-white/80 bg-white/80 p-4 text-left shadow-lg shadow-slate-900/5 backdrop-blur-xl transition hover:-translate-y-0.5 hover:border-emerald-300 hover:bg-white active:scale-[0.98]"
                >

                  <span className="text-2xl">
                    📊
                  </span>

                  <p className="mt-3 font-semibold">
                    {t.sensorHistory}
                  </p>

                  <p className="mt-1 text-xs text-slate-500">
                    {t.viewTrends}
                  </p>

                </Link>

                {/* IRRIGATION HISTORY */}

                <Link
                  href="/irrigation-history"
                  className="block rounded-2xl border border-white/80 bg-white/80 p-4 text-left shadow-lg shadow-slate-900/5 backdrop-blur-xl transition hover:-translate-y-0.5 hover:border-emerald-300 hover:bg-white active:scale-[0.98]"
                >

                  <span className="text-2xl">
                    💦
                  </span>

                  <p className="mt-3 font-semibold">
                    {t.irrigationHistory}
                  </p>

                  <p className="mt-1 text-xs text-slate-500">
                    {t.previousRecords}
                  </p>

                </Link>

                {/* FARMER PROFILE */}

                <Link
                  href="/profile"
                  className="block rounded-2xl border border-white/80 bg-white/80 p-4 text-left shadow-lg shadow-slate-900/5 backdrop-blur-xl transition hover:-translate-y-0.5 hover:border-emerald-300 hover:bg-white active:scale-[0.98]"
                >

                  <span className="text-2xl">
                    👨‍🌾
                  </span>

                  <p className="mt-3 font-semibold">
                    {t.farmerProfile}
                  </p>

                  <p className="mt-1 text-xs text-slate-500">
                    {t.manageProfile}
                  </p>

                </Link>

                {/* VOICE ASSISTANT */}

                <Link
                  href="/voice-assistant"
                  className="block rounded-2xl border border-purple-200 bg-purple-50 p-4 text-left shadow-sm transition hover:border-purple-400 active:scale-[0.98]"
                >

                  <span className="text-2xl">
                    🎤
                  </span>

                  <p className="mt-3 font-semibold text-purple-900">
                    Voice Assistant
                  </p>

                  <p className="mt-1 text-xs text-purple-700">
                    Ask about irrigation using your voice.
                  </p>

                </Link>

              </div>

            </section>

          </>

        )}

        {/* FOOTER */}

        <footer className="mt-8 rounded-[2rem] border border-white/10 bg-gradient-to-br from-[#052e1b] via-[#064e3b] to-[#14532d] px-5 py-7 text-center text-xs text-emerald-100/70 shadow-2xl shadow-emerald-950/20">

          AI-Powered Smart Irrigation System

          <br />

          Predictive Water Management & Crop
          Optimization

        </footer>

      </div>

      <BottomNav />

    </main>
  );
}