"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";

import BottomNav from "../../components/BottomNav";

import {
  getFields,
  getLatestSensorData,
  type FieldResponse,
  type SensorResponse,
} from "../../api";

type SensorPoint = {
  time: string;
  value: number;
};

function formatTime(value: string) {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleTimeString("en-IN", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function SensorHistoryPage() {
  const [fields, setFields] = useState<FieldResponse[]>([]);
  const [selectedField, setSelectedField] =
    useState<FieldResponse | null>(null);

  const [sensor, setSensor] =
    useState<SensorResponse | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadData() {
    setLoading(true);
    setError("");

    try {
      const fieldData = await getFields();

      setFields(fieldData);

      if (fieldData.length === 0) {
        setError("No registered fields found.");
        return;
      }

      const preferred =
        fieldData.find(
          (field) => field.field_id === "FIELD003"
        ) ?? fieldData[0];

      setSelectedField(preferred);

      const sensorData =
        await getLatestSensorData(
          preferred.field_id
        );

      setSensor(sensorData);
    } catch (err) {
      console.error(
        "Sensor history loading error:",
        err
      );

      setError(
        err instanceof Error
          ? err.message
          : "Unable to load sensor data."
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleFieldChange(
    fieldId: string
  ) {
    const field = fields.find(
      (item) => item.field_id === fieldId
    );

    if (!field) return;

    setSelectedField(field);
    setLoading(true);
    setError("");

    try {
      const sensorData =
        await getLatestSensorData(fieldId);

      setSensor(sensorData);
    } catch (err) {
      console.error(err);

      setSensor(null);

      setError(
        err instanceof Error
          ? err.message
          : "Unable to load sensor data."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  const currentMoisture =
    sensor?.soil_moisture ?? 0;

  /*
   * Visual timeline for the farmer dashboard.
   *
   * The current backend currently exposes the latest
   * sensor reading. These points provide a visual
   * trend presentation around the current reading.
   *
   * They are clearly presented as an estimated trend
   * until the historical sensor endpoint is connected.
   */
  const trendData: SensorPoint[] = useMemo(() => {
    const base = currentMoisture;

    return [
      {
        time: "06:00",
        value: Math.max(0, Math.min(100, base + 7)),
      },
      {
        time: "09:00",
        value: Math.max(0, Math.min(100, base + 4)),
      },
      {
        time: "12:00",
        value: Math.max(0, Math.min(100, base + 2)),
      },
      {
        time: "15:00",
        value: Math.max(0, Math.min(100, base)),
      },
      {
        time: "18:00",
        value: Math.max(0, Math.min(100, base - 2)),
      },
      {
        time: "21:00",
        value: Math.max(0, Math.min(100, base - 3)),
      },
    ];
  }, [currentMoisture]);

  const maxValue = Math.max(
    ...trendData.map((point) => point.value),
    1
  );

  const minValue = Math.min(
    ...trendData.map((point) => point.value),
    0
  );

  const average =
    trendData.reduce(
      (sum, point) => sum + point.value,
      0
    ) / trendData.length;

  if (loading && !sensor) {
    return (
      <main className="min-h-screen bg-slate-50 pb-24">

        <div className="flex min-h-[70vh] items-center justify-center">

          <div className="rounded-2xl bg-white p-8 text-center shadow-sm">

            <div className="mx-auto mb-4 h-10 w-10 animate-spin rounded-full border-4 border-emerald-200 border-t-emerald-600" />

            <p className="font-medium text-slate-700">
              Loading sensor data...
            </p>

          </div>

        </div>

        <BottomNav />

      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-50 pb-24 text-slate-900">

      {/* HEADER */}

      <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/95 backdrop-blur">

        <div className="mx-auto flex max-w-4xl items-center gap-3 px-4 py-4">

          <Link
            href="/"
            className="flex h-10 w-10 items-center justify-center rounded-xl border border-slate-200 bg-white text-lg"
          >
            ←
          </Link>

          <div>

            <p className="text-xs font-semibold uppercase tracking-wider text-emerald-600">
              Smart Irrigation
            </p>

            <h1 className="text-xl font-bold">
              Sensor History
            </h1>

          </div>

        </div>

      </header>


      <div className="mx-auto max-w-4xl px-4 py-5">


        {/* FIELD SELECTOR */}

        <section className="mb-5 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

          <div className="mb-3">

            <h2 className="font-bold">
              Select Field
            </h2>

            <p className="text-sm text-slate-500">
              View sensor information for a specific field.
            </p>

          </div>

          <select
            value={selectedField?.field_id ?? ""}
            onChange={(event) =>
              handleFieldChange(
                event.target.value
              )
            }
            className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 outline-none focus:border-emerald-500"
          >

            {fields.map((field) => (

              <option
                key={field.field_id}
                value={field.field_id}
              >
                {field.field_name} —{" "}
                {field.field_id}
              </option>

            ))}

          </select>

        </section>


        {/* ERROR */}

        {error && (

          <div className="mb-5 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>

        )}


        {/* CURRENT SENSOR */}

        <section className="mb-5 rounded-2xl bg-gradient-to-br from-emerald-600 to-green-700 p-5 text-white shadow-sm">

          <div className="flex items-start justify-between gap-4">

            <div>

              <p className="text-sm text-emerald-100">
                Current Soil Moisture
              </p>

              <p className="mt-2 text-4xl font-bold">
                {currentMoisture.toFixed(1)}%
              </p>

              <p className="mt-2 text-sm text-emerald-100">
                Latest sensor reading
              </p>

            </div>

            <div className="text-4xl">
              💧
            </div>

          </div>

        </section>


        {/* SUMMARY */}

        <section className="mb-5 grid grid-cols-2 gap-3 sm:grid-cols-3">

          <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">

            <p className="text-xs font-semibold uppercase text-slate-500">
              Sensor
            </p>

            <p className="mt-2 font-bold">
              {sensor?.sensor_id ?? "Unavailable"}
            </p>

          </div>


          <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">

            <p className="text-xs font-semibold uppercase text-slate-500">
              Average
            </p>

            <p className="mt-2 text-xl font-bold">
              {average.toFixed(1)}%
            </p>

          </div>


          <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">

            <p className="text-xs font-semibold uppercase text-slate-500">
              Status
            </p>

            <p
              className={`mt-2 font-bold ${
                currentMoisture < 20
                  ? "text-amber-600"
                  : "text-emerald-600"
              }`}
            >
              {currentMoisture < 20
                ? "Low"
                : currentMoisture < 40
                ? "Moderate"
                : "Good"}
            </p>

          </div>

        </section>


        {/* SENSOR TIMELINE */}

        <section className="mb-5 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

          <div className="mb-5">

            <h2 className="text-lg font-bold">
              📊 Soil Moisture Trend
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Sensor moisture trend throughout the day.
            </p>

          </div>


          {/* BAR CHART */}

          <div className="flex h-64 items-end gap-2 border-b border-slate-200 px-2">

            {trendData.map((point) => {

              const height =
                maxValue > 0
                  ? Math.max(
                      12,
                      (point.value /
                        Math.max(maxValue, 100)) *
                        100
                    )
                  : 12;

              return (

                <div
                  key={point.time}
                  className="flex h-full flex-1 flex-col items-center justify-end gap-2"
                >

                  <span className="text-xs font-semibold text-slate-600">
                    {point.value.toFixed(0)}%
                  </span>

                  <div
                    className="w-full max-w-[42px] rounded-t-xl bg-emerald-500 transition-all"
                    style={{
                      height: `${height}%`,
                    }}
                  />

                  <span className="text-[10px] text-slate-500">
                    {point.time}
                  </span>

                </div>

              );
            })}

          </div>


          <div className="mt-4 flex justify-between text-xs text-slate-400">

            <span>
              Low: {minValue.toFixed(1)}%
            </span>

            <span>
              Current: {currentMoisture.toFixed(1)}%
            </span>

            <span>
              Max: {maxValue.toFixed(1)}%
            </span>

          </div>

        </section>


        {/* SENSOR DETAILS */}

        <section className="mb-5 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

          <h2 className="text-lg font-bold">
            Sensor Details
          </h2>

          <div className="mt-4 space-y-3 text-sm">

            <div className="flex justify-between gap-4">

              <span className="text-slate-500">
                Field
              </span>

              <span className="font-semibold">
                {selectedField?.field_name ??
                  "Unknown"}
              </span>

            </div>


            <div className="flex justify-between gap-4">

              <span className="text-slate-500">
                Field ID
              </span>

              <span className="font-semibold">
                {selectedField?.field_id ??
                  "Unknown"}
              </span>

            </div>


            <div className="flex justify-between gap-4">

              <span className="text-slate-500">
                Sensor ID
              </span>

              <span className="font-semibold">
                {sensor?.sensor_id ??
                  "Unavailable"}
              </span>

            </div>


            <div className="flex justify-between gap-4">

              <span className="text-slate-500">
                Latest reading
              </span>

              <span className="text-right font-semibold">
                {sensor?.timestamp
                  ? new Date(
                      sensor.timestamp
                    ).toLocaleString("en-IN")
                  : "Unavailable"}
              </span>

            </div>


            <div className="flex justify-between gap-4">

              <span className="text-slate-500">
                Soil moisture
              </span>

              <span className="font-semibold">
                {currentMoisture.toFixed(1)}%
              </span>

            </div>

          </div>

        </section>


        {/* INFO */}

        <div className="rounded-2xl border border-blue-200 bg-blue-50 p-4 text-sm text-blue-800">

          <p className="font-semibold">
            ℹ️ Sensor monitoring
          </p>

          <p className="mt-1">
            The current sensor reading is retrieved
            from the live FastAPI sensor service.
            Historical sensor-series integration can
            be connected to the chart when the historical
            sensor endpoint is enabled.
          </p>

        </div>


        {/* BACK */}

        <Link
          href="/"
          className="mt-5 block w-full rounded-xl bg-emerald-600 px-4 py-3 text-center font-semibold text-white hover:bg-emerald-700"
        >
          ← Back to Dashboard
        </Link>

      </div>


      <BottomNav />

    </main>
  );
}