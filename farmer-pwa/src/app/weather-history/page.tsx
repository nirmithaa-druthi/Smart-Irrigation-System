"use client";

import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";

import {
  getFields,
  getWeatherHistory,
  type FieldResponse,
  type WeatherHistoryItem,
} from "../../api";

import BottomNav from "../../components/BottomNav";

export default function WeatherHistoryPage() {
  const [fields, setFields] = useState<FieldResponse[]>([]);
  const [selectedField, setSelectedField] =
    useState<FieldResponse | null>(null);

  const [weatherHistory, setWeatherHistory] =
    useState<WeatherHistoryItem[]>([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadFields() {
      try {
        setLoading(true);

        const result = await getFields();

        setFields(result);

        if (result.length > 0) {
          const preferred = result.find(
            (field) => field.field_id === "FIELD001"
          );

          setSelectedField(preferred ?? result[0]);
        }
      } catch (err) {
        console.error(err);

        setError(
          err instanceof Error
            ? err.message
            : "Unable to load fields."
        );
      } finally {
        setLoading(false);
      }
    }

    loadFields();
  }, []);

  useEffect(() => {
    async function loadWeatherHistory() {
      if (!selectedField) {
        return;
      }

      try {
        setLoading(true);
        setError("");

        const result = await getWeatherHistory(
          selectedField.field_id
        );

        setWeatherHistory(result.history);
      } catch (err) {
        console.error(err);

        setWeatherHistory([]);

        setError(
          err instanceof Error
            ? err.message
            : "Unable to load weather history."
        );
      } finally {
        setLoading(false);
      }
    }

    loadWeatherHistory();
  }, [selectedField]);

  const chartData = weatherHistory.map((item) => ({
    time: new Date(item.timestamp).toLocaleString(
      "en-IN",
      {
        day: "2-digit",
        month: "short",
        hour: "2-digit",
        minute: "2-digit",
      }
    ),
    temperature: Number(item.temperature.toFixed(1)),
    humidity: Number(item.humidity.toFixed(1)),
    rainfall: Number(item.rainfall.toFixed(2)),
    rainProbability: Number(
      item.rain_probability.toFixed(0)
    ),
  }));

  const totalRainfall = weatherHistory.reduce(
    (total, item) => total + item.rainfall,
    0
  );

  const averageTemperature =
    weatherHistory.length > 0
      ? weatherHistory.reduce(
          (total, item) => total + item.temperature,
          0
        ) / weatherHistory.length
      : 0;

  const averageHumidity =
    weatherHistory.length > 0
      ? weatherHistory.reduce(
          (total, item) => total + item.humidity,
          0
        ) / weatherHistory.length
      : 0;

  return (
    <main className="min-h-screen bg-slate-50 pb-24 text-slate-900">

      {/* HEADER */}

      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-5xl px-4 py-5">

          <p className="text-xs font-semibold uppercase tracking-wider text-emerald-600">
            Smart Irrigation
          </p>

          <h1 className="mt-1 text-2xl font-bold">
            Weather & Rainfall Trends
          </h1>

          <p className="mt-1 text-sm text-slate-500">
            Historical weather conditions for your field
          </p>

        </div>
      </header>

      <div className="mx-auto max-w-5xl px-4 py-6">

        {/* FIELD SELECTOR */}

        <section className="mb-5 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">

          <h2 className="font-bold">
            Select Field
          </h2>

          <select
            value={selectedField?.field_id ?? ""}
            onChange={(event) => {
              const field = fields.find(
                (item) =>
                  item.field_id === event.target.value
              );

              setSelectedField(field ?? null);
            }}
            className="mt-3 w-full rounded-xl border border-slate-300 bg-white px-4 py-3"
          >
            {fields.map((field) => (
              <option
                key={field.field_id}
                value={field.field_id}
              >
                {field.field_name} - {field.field_id}
              </option>
            ))}
          </select>

        </section>

        {/* LOADING */}

        {loading && (
          <div className="mb-5 rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">

            <div className="mx-auto h-8 w-8 animate-spin rounded-full border-4 border-emerald-200 border-t-emerald-600" />

            <p className="mt-3 text-sm text-slate-500">
              Loading weather history...
            </p>

          </div>
        )}

        {/* ERROR */}

        {error && (
          <div className="mb-5 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        )}

        {/* SUMMARY */}

        {!loading && weatherHistory.length > 0 && (
          <>
            <section className="mb-5 grid grid-cols-1 gap-3 sm:grid-cols-3">

              <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  🌡️ Avg Temperature
                </p>

                <p className="mt-2 text-2xl font-bold">
                  {averageTemperature.toFixed(1)}°C
                </p>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  💧 Avg Humidity
                </p>

                <p className="mt-2 text-2xl font-bold">
                  {averageHumidity.toFixed(1)}%
                </p>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  🌧️ Total Rainfall
                </p>

                <p className="mt-2 text-2xl font-bold">
                  {totalRainfall.toFixed(2)} mm
                </p>
              </div>

            </section>

            {/* TEMPERATURE + HUMIDITY */}

            <section className="mb-5 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

              <h2 className="text-lg font-bold">
                Temperature & Humidity Trends
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Historical readings from the weather database
              </p>

              <div className="mt-5 h-80 w-full">

                <ResponsiveContainer width="100%" height="100%">

                  <LineChart data={chartData}>

                    <CartesianGrid strokeDasharray="3 3" />

                    <XAxis
                      dataKey="time"
                      tick={{ fontSize: 10 }}
                      interval="preserveStartEnd"
                    />

                    <YAxis />

                    <Tooltip />

                    <Legend />

                    <Line
                      type="monotone"
                      dataKey="temperature"
                      name="Temperature °C"
                      stroke="#f97316"
                      strokeWidth={2}
                      dot={false}
                    />

                    <Line
                      type="monotone"
                      dataKey="humidity"
                      name="Humidity %"
                      stroke="#2563eb"
                      strokeWidth={2}
                      dot={false}
                    />

                  </LineChart>

                </ResponsiveContainer>

              </div>

            </section>

            {/* RAINFALL */}

            <section className="mb-5 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

              <h2 className="text-lg font-bold">
                Rainfall Trend
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Recorded rainfall over time
              </p>

              <div className="mt-5 h-80 w-full">

                <ResponsiveContainer width="100%" height="100%">

                  <BarChart data={chartData}>

                    <CartesianGrid strokeDasharray="3 3" />

                    <XAxis
                      dataKey="time"
                      tick={{ fontSize: 10 }}
                      interval="preserveStartEnd"
                    />

                    <YAxis />

                    <Tooltip />

                    <Legend />

                    <Bar
                      dataKey="rainfall"
                      name="Rainfall mm"
                      fill="#0ea5e9"
                    />

                  </BarChart>

                </ResponsiveContainer>

              </div>

            </section>

            {/* RAIN PROBABILITY */}

            <section className="mb-5 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

              <h2 className="text-lg font-bold">
                Rain Probability Trend
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Historical probability of rainfall
              </p>

              <div className="mt-5 h-80 w-full">

                <ResponsiveContainer width="100%" height="100%">

                  <LineChart data={chartData}>

                    <CartesianGrid strokeDasharray="3 3" />

                    <XAxis
                      dataKey="time"
                      tick={{ fontSize: 10 }}
                      interval="preserveStartEnd"
                    />

                    <YAxis
                      domain={[0, 100]}
                    />

                    <Tooltip />

                    <Legend />

                    <Line
                      type="monotone"
                      dataKey="rainProbability"
                      name="Rain Probability %"
                      stroke="#7c3aed"
                      strokeWidth={2}
                      dot={false}
                    />

                  </LineChart>

                </ResponsiveContainer>

              </div>

            </section>

            {/* DATA INFO */}

            <section className="rounded-2xl border border-emerald-200 bg-emerald-50 p-5">

              <h2 className="font-bold text-emerald-900">
                Weather Data
              </h2>

              <p className="mt-2 text-sm text-emerald-800">
                {weatherHistory.length} historical weather
                records are available for{" "}
                {selectedField?.field_name}.
              </p>

              <p className="mt-1 text-xs text-emerald-700">
                Data is retrieved from the PostgreSQL
                weather_data table through the FastAPI
                backend.
              </p>

            </section>
          </>
        )}

        {!loading && weatherHistory.length === 0 && !error && (
          <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">

            <p className="text-lg font-semibold">
              No weather history available
            </p>

            <p className="mt-2 text-sm text-slate-500">
              No historical weather records were found
              for this field.
            </p>

          </div>
        )}

      </div>

      <BottomNav />

    </main>
  );
}