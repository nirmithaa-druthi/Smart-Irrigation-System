"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";

import BottomNav from "../../components/BottomNav";

import {
  getFields,
  getIrrigationRecommendation,
  getLatestSensorData,
  getLatestWeather,
  getIrrigationHistory,
  type FieldResponse,
  type IrrigationResponse,
  type SensorResponse,
  type WeatherResponse,
} from "../../api";

type AlertType =
  | "low-moisture"
  | "rain"
  | "irrigation"
  | "overwatering"
  | "sensor";

type AlertItem = {
  id: string;
  type: AlertType;
  title: string;
  message: string;
  action: string;
  priority: "High" | "Medium" | "Low";
  field: string;
  time: string;
  read: boolean;
};

export default function AlertsPage() {
  const [fields, setFields] = useState<FieldResponse[]>([]);
  const [selectedField, setSelectedField] =
    useState<FieldResponse | null>(null);

  const [sensor, setSensor] =
    useState<SensorResponse | null>(null);

  const [weather, setWeather] =
    useState<WeatherResponse | null>(null);

  const [recommendation, setRecommendation] =
    useState<IrrigationResponse | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [expandedId, setExpandedId] =
    useState<string | null>(null);

  const [readAlerts, setReadAlerts] =
    useState<string[]>([]);

  const [notificationPermission, setNotificationPermission] =
    useState<NotificationPermission | "unsupported">(
      "default"
    );

  const [pushMessage, setPushMessage] = useState("");

  /* =========================================================
     NOTIFICATION STATUS
     ========================================================= */

  useEffect(() => {
    if (typeof window === "undefined") return;

    if (!("Notification" in window)) {
      setNotificationPermission("unsupported");
      return;
    }

    setNotificationPermission(Notification.permission);
  }, []);

  /* =========================================================
     ENABLE WEB PUSH
     ========================================================= */

  async function enableWebPush() {
    setPushMessage("");

    if (!("Notification" in window)) {
      setNotificationPermission("unsupported");

      setPushMessage(
        "This browser does not support notifications."
      );

      return;
    }

    try {
      const permission =
        await Notification.requestPermission();

      setNotificationPermission(permission);

      if (permission === "granted") {
        setPushMessage(
          "Web Push notifications are enabled."
        );

        if ("serviceWorker" in navigator) {
          await navigator.serviceWorker.ready;
        }
      } else if (permission === "denied") {
        setPushMessage(
          "Notifications are blocked. Please allow notifications in your browser settings."
        );
      } else {
        setPushMessage(
          "Notification permission was not granted."
        );
      }
    } catch (err) {
      console.error(
        "Notification permission error:",
        err
      );

      setPushMessage(
        "Unable to enable notifications."
      );
    }
  }

  /* =========================================================
     TEST NOTIFICATION
     ========================================================= */

  async function sendTestNotification() {
    if (
      typeof window === "undefined" ||
      !("Notification" in window)
    ) {
      return;
    }

    if (Notification.permission !== "granted") {
      setPushMessage(
        "Please enable notifications first."
      );

      return;
    }

    try {
      if ("serviceWorker" in navigator) {
        const registration =
          await navigator.serviceWorker.ready;

        await registration.showNotification(
          "Smart Irrigation Alert",
          {
            body: "Web Push notification test successful!",
            icon: "/icons/icon-192.svg",
            badge: "/icons/icon-192.svg",
            tag: "smart-irrigation-test",
          }
        );

        setPushMessage(
          "Test notification sent successfully."
        );
      }
    } catch (err) {
      console.error(
        "Test notification error:",
        err
      );

      setPushMessage(
        "Unable to send test notification."
      );
    }
  }

  /* =========================================================
     GET PREVIOUS WATER USAGE
     ========================================================= */

  async function getPreviousWaterUsage(
    fieldId: string
  ) {
    try {
      const history =
        await getIrrigationHistory(fieldId);

      if (
        !history.history ||
        history.history.length === 0
      ) {
        return 0;
      }

      const sortedHistory = [
        ...history.history,
      ].sort(
        (a, b) =>
          new Date(
            b.irrigation_timestamp
          ).getTime() -
          new Date(
            a.irrigation_timestamp
          ).getTime()
      );

      return (
        Number(
          sortedHistory[0].water_used_liters
        ) || 0
      );
    } catch (err) {
      console.error(
        "Irrigation history error:",
        err
      );

      return 0;
    }
  }

  /* =========================================================
     LOAD ALERT DATA
     ========================================================= */

  async function loadAlerts(
    fieldOverride?: FieldResponse
  ) {
    setLoading(true);
    setError("");

    try {
      let fieldData = fields;

      if (fieldData.length === 0) {
        fieldData = await getFields();
        setFields(fieldData);
      }

      if (fieldData.length === 0) {
        setError("No registered fields found.");
        setLoading(false);
        return;
      }

      const field =
        fieldOverride ??
        selectedField ??
        fieldData.find(
          (item) => item.field_id === "FIELD003"
        ) ??
        fieldData[0];

      setSelectedField(field);

      /* ---------------------------------------------------------
         LIVE SENSOR DATA
         --------------------------------------------------------- */

      let sensorData: SensorResponse | null = null;

      try {
        sensorData =
          await getLatestSensorData(
            field.field_id
          );

        setSensor(sensorData);
      } catch (sensorError) {
        console.error(
          "Sensor alert error:",
          sensorError
        );

        setSensor(null);
      }

      /* ---------------------------------------------------------
         LIVE WEATHER DATA
         --------------------------------------------------------- */

      let weatherData: WeatherResponse | null = null;

      try {
        weatherData =
          await getLatestWeather(
            field.field_id
          );

        setWeather(weatherData);
      } catch (weatherError) {
        console.error(
          "Weather alert error:",
          weatherError
        );

        setWeather(null);
      }

      /* ---------------------------------------------------------
         LIVE ML RECOMMENDATION
         --------------------------------------------------------- */

      if (sensorData && weatherData) {
        try {
          const now = new Date();

          const previousWaterUsage =
            await getPreviousWaterUsage(
              field.field_id
            );

          const mlResult =
            await getIrrigationRecommendation({
              field_id: field.field_id,

              soil_moisture:
                Number(
                  sensorData.soil_moisture
                ),

              temperature:
                Number(
                  weatherData.temperature
                ),

              humidity:
                Number(
                  weatherData.humidity
                ),

              rainfall:
                Number(
                  weatherData.rainfall
                ),

              rain_probability:
                Number(
                  weatherData.rain_probability
                ),

              crop_type:
                field.crop_type,

              growth_stage:
                Number(
                  field.growth_stage
                ),

              hour:
                now.getHours(),

              day_of_week:
                now.getDay(),

              day_of_month:
                now.getDate(),

              previous_water_usage_liters:
                previousWaterUsage,
            });

          setRecommendation(mlResult);
        } catch (mlError) {
          console.error(
            "ML alert error:",
            mlError
          );

          setRecommendation(null);
        }
      } else {
        setRecommendation(null);
      }
    } catch (err) {
      console.error(
        "Alert loading error:",
        err
      );

      setError(
        err instanceof Error
          ? err.message
          : "Unable to load alerts."
      );
    } finally {
      setLoading(false);
    }
  }

  /* =========================================================
     INITIAL LOAD
     ========================================================= */

  useEffect(() => {
    loadAlerts();
  }, []);

  /* =========================================================
     GENERATE ALERTS
     ========================================================= */

  const alerts = useMemo<AlertItem[]>(() => {
    const generated: AlertItem[] = [];

    const fieldName =
      selectedField?.field_name ??
      "Selected Field";

    const moisture =
      sensor?.soil_moisture ?? null;

    const rainProbability =
      weather?.rain_probability ?? null;

    const rainfall =
      weather?.rainfall ?? null;

    /* ---------------------------------------------------------
       LOW SOIL MOISTURE
       --------------------------------------------------------- */

    if (
      moisture !== null &&
      moisture < 20
    ) {
      generated.push({
        id: "low-moisture",
        type: "low-moisture",
        title: "Low Soil Moisture",
        message:
          `Soil moisture is currently ${moisture.toFixed(
            1
          )}%. The field may require irrigation.`,
        action:
          "Check the irrigation recommendation and follow the suggested water quantity.",
        priority: "High",
        field: fieldName,
        time: "Live sensor reading",
        read: readAlerts.includes(
          "low-moisture"
        ),
      });
    }

    /* ---------------------------------------------------------
       HEAVY RAINFALL
       --------------------------------------------------------- */

    if (
      rainProbability !== null &&
      rainProbability >= 70
    ) {
      generated.push({
        id: "heavy-rain",
        type: "rain",
        title: "Heavy Rainfall Warning",
        message:
          `Rain probability is currently ${rainProbability}%. Additional irrigation may not be necessary.`,
        action:
          "Monitor rainfall conditions and avoid unnecessary irrigation.",
        priority: "High",
        field: fieldName,
        time: "Current weather",
        read: readAlerts.includes(
          "heavy-rain"
        ),
      });
    }

    /* ---------------------------------------------------------
       RECENT RAINFALL
       --------------------------------------------------------- */

    if (
      rainfall !== null &&
      rainfall >= 5
    ) {
      generated.push({
        id: "recent-rain",
        type: "rain",
        title: "Recent Rainfall Detected",
        message:
          `${Number(rainfall).toFixed(
            1
          )} mm of rainfall has been recorded in the latest weather data.`,
        action:
          "Check soil moisture before starting additional irrigation.",
        priority: "Medium",
        field: fieldName,
        time: "Current weather",
        read: readAlerts.includes(
          "recent-rain"
        ),
      });
    }

    /* ---------------------------------------------------------
       IRRIGATION REMINDER
       --------------------------------------------------------- */

    if (
      recommendation?.irrigation_required
    ) {
      generated.push({
        id: "irrigation-reminder",
        type: "irrigation",
        title: "Irrigation Reminder",
        message:
          `The ML irrigation engine recommends approximately ${recommendation.predicted_water_quantity_liters.toFixed(
            2
          )} L of water.`,
        action:
          "Review the recommendation and generate today's irrigation schedule from the dashboard.",
        priority: "High",
        field: fieldName,
        time: "ML recommendation",
        read: readAlerts.includes(
          "irrigation-reminder"
        ),
      });
    }

    /* ---------------------------------------------------------
       OVER-WATERING PREVENTION
       --------------------------------------------------------- */

    if (
      moisture !== null &&
      moisture >= 40 &&
      recommendation &&
      !recommendation.irrigation_required
    ) {
      generated.push({
        id: "overwatering",
        type: "overwatering",
        title: "Over-Watering Prevention",
        message:
          `Soil moisture is ${moisture.toFixed(
            1
          )}% and the ML engine does not currently require irrigation.`,
        action:
          "Avoid unnecessary watering and continue monitoring the field.",
        priority: "Medium",
        field: fieldName,
        time: "ML + sensor rule",
        read: readAlerts.includes(
          "overwatering"
        ),
      });
    }

    /* ---------------------------------------------------------
       SENSOR FAILURE
       --------------------------------------------------------- */

    if (!sensor) {
      generated.push({
        id: "sensor-failure",
        type: "sensor",
        title: "Sensor Status Alert",
        message:
          "The latest sensor reading could not be retrieved.",
        action:
          "Check the sensor connection and sensor API service.",
        priority: "High",
        field: fieldName,
        time: "System check",
        read: readAlerts.includes(
          "sensor-failure"
        ),
      });
    }

    /* ---------------------------------------------------------
       NO ALERT
       --------------------------------------------------------- */

    if (generated.length === 0) {
      generated.push({
        id: "system-normal",
        type: "sensor",
        title: "Farm Conditions Normal",
        message:
          "No active irrigation or weather alerts were detected.",
        action:
          "Continue monitoring soil moisture and weather conditions.",
        priority: "Low",
        field: fieldName,
        time: "Live monitoring",
        read: readAlerts.includes(
          "system-normal"
        ),
      });
    }

    return generated;
  }, [
    sensor,
    weather,
    recommendation,
    selectedField,
    readAlerts,
  ]);

  const unreadCount =
    alerts.filter(
      (alert) => !alert.read
    ).length;

  /* =========================================================
     ALERT ACTIONS
     ========================================================= */

  function toggleAlert(id: string) {
    setExpandedId((current) =>
      current === id ? null : id
    );

    if (!readAlerts.includes(id)) {
      setReadAlerts((current) => [
        ...current,
        id,
      ]);
    }
  }

  function markAllRead() {
    setReadAlerts(
      alerts.map((alert) => alert.id)
    );
  }

  /* =========================================================
     ICONS
     ========================================================= */

  function getIcon(type: AlertType) {
    switch (type) {
      case "low-moisture":
        return "💧";

      case "rain":
        return "🌧️";

      case "irrigation":
        return "🚿";

      case "overwatering":
        return "⚠️";

      case "sensor":
        return "📡";

      default:
        return "🔔";
    }
  }

  function getPriorityClass(
    priority: AlertItem["priority"]
  ) {
    if (priority === "High") {
      return "bg-red-100 text-red-700";
    }

    if (priority === "Medium") {
      return "bg-amber-100 text-amber-700";
    }

    return "bg-emerald-100 text-emerald-700";
  }

  /* =========================================================
     UI
     ========================================================= */

  return (
    <main className="min-h-screen bg-slate-50 pb-24 text-slate-900">

      {/* HEADER */}

      <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/95 backdrop-blur">

        <div className="mx-auto flex max-w-4xl items-center justify-between px-4 py-4">

          <div className="flex items-center gap-3">

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
                Alerts
              </h1>

            </div>

          </div>

          {unreadCount > 0 && (
            <div className="rounded-full bg-red-100 px-3 py-1 text-xs font-bold text-red-700">
              {unreadCount} unread
            </div>
          )}

        </div>

      </header>

      <div className="mx-auto max-w-4xl px-4 py-5">

        {/* LIVE STATUS */}

        <section className="mb-5 rounded-2xl bg-gradient-to-br from-emerald-600 to-green-700 p-5 text-white shadow-sm">

          <div className="flex items-start justify-between gap-4">

            <div>

              <p className="text-sm text-emerald-100">
                Live Monitoring
              </p>

              <h2 className="mt-1 text-2xl font-bold">
                Farm Alert Center
              </h2>

              <p className="mt-2 text-sm text-emerald-100">
                Monitoring soil moisture, weather and
                ML irrigation recommendations.
              </p>

            </div>

            <div className="text-4xl">
              🔔
            </div>

          </div>

        </section>

        {/* FIELD */}

        <section className="mb-5 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

          <div className="mb-3">

            <h2 className="font-bold">
              Monitored Field
            </h2>

            <p className="text-sm text-slate-500">
              Alerts are generated using live field data.
            </p>

          </div>

          <select
            value={
              selectedField?.field_id ?? ""
            }
            onChange={async (event) => {

              const field =
                fields.find(
                  (item) =>
                    item.field_id ===
                    event.target.value
                );

              if (!field) return;

              setSelectedField(field);

              await loadAlerts(field);
            }}
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

        {/* ALERT LIST */}

        <section className="mb-5">

          <div className="mb-3 flex items-center justify-between">

            <div>

              <h2 className="text-lg font-bold">
                Active Alerts
              </h2>

              <p className="text-sm text-slate-500">
                Generated from current farm conditions.
              </p>

            </div>

            {unreadCount > 0 && (

              <button
                onClick={markAllRead}
                className="text-xs font-semibold text-emerald-700"
              >
                Mark all read
              </button>

            )}

          </div>

          {loading ? (

            <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">

              <div className="mx-auto mb-4 h-9 w-9 animate-spin rounded-full border-4 border-emerald-200 border-t-emerald-600" />

              <p className="text-sm text-slate-500">
                Checking farm conditions...
              </p>

            </div>

          ) : (

            <div className="space-y-3">

              {alerts.map((alert) => {

                const expanded =
                  expandedId === alert.id;

                return (

                  <button
                    key={alert.id}
                    onClick={() =>
                      toggleAlert(alert.id)
                    }
                    className="w-full rounded-2xl border border-slate-200 bg-white p-4 text-left shadow-sm transition hover:border-emerald-300"
                  >

                    <div className="flex gap-3">

                      <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-xl">
                        {getIcon(alert.type)}
                      </div>

                      <div className="min-w-0 flex-1">

                        <div className="flex items-start justify-between gap-3">

                          <div>

                            <div className="flex items-center gap-2">

                              {!alert.read && (
                                <span className="h-2 w-2 rounded-full bg-red-500" />
                              )}

                              <h3 className="font-bold">
                                {alert.title}
                              </h3>

                            </div>

                            <p className="mt-1 text-sm text-slate-500">
                              {alert.field}
                            </p>

                          </div>

                          <span
                            className={`shrink-0 rounded-full px-2 py-1 text-[10px] font-bold ${getPriorityClass(
                              alert.priority
                            )}`}
                          >
                            {alert.priority}
                          </span>

                        </div>

                        <p className="mt-3 text-sm text-slate-700">
                          {alert.message}
                        </p>

                        <div className="mt-3 flex items-center justify-between">

                          <span className="text-xs text-slate-400">
                            {alert.time}
                          </span>

                          <span className="text-xs font-semibold text-emerald-600">
                            {expanded
                              ? "Hide details ↑"
                              : "View details ↓"}
                          </span>

                        </div>

                        {expanded && (

                          <div className="mt-4 rounded-xl bg-slate-50 p-4">

                            <p className="text-xs font-bold uppercase tracking-wide text-slate-500">
                              Recommended Action
                            </p>

                            <p className="mt-2 text-sm text-slate-700">
                              {alert.action}
                            </p>

                          </div>

                        )}

                      </div>

                    </div>

                  </button>

                );
              })}

            </div>

          )}

        </section>

        {/* CURRENT CONDITIONS */}

        <section className="mb-5 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

          <h2 className="text-lg font-bold">
            Current Conditions
          </h2>

          <div className="mt-4 grid grid-cols-2 gap-3">

            <div className="rounded-xl bg-slate-50 p-4">

              <p className="text-xs text-slate-500">
                Soil Moisture
              </p>

              <p className="mt-1 text-xl font-bold">
                {sensor
                  ? `${Number(
                      sensor.soil_moisture
                    ).toFixed(1)}%`
                  : "--"}
              </p>

            </div>

            <div className="rounded-xl bg-slate-50 p-4">

              <p className="text-xs text-slate-500">
                Temperature
              </p>

              <p className="mt-1 text-xl font-bold">
                {weather
                  ? `${Number(
                      weather.temperature
                    ).toFixed(1)}°C`
                  : "--"}
              </p>

            </div>

            <div className="rounded-xl bg-slate-50 p-4">

              <p className="text-xs text-slate-500">
                Rain Probability
              </p>

              <p className="mt-1 text-xl font-bold">
                {weather
                  ? `${Number(
                      weather.rain_probability
                    ).toFixed(1)}%`
                  : "--"}
              </p>

            </div>

            <div className="rounded-xl bg-slate-50 p-4">

              <p className="text-xs text-slate-500">
                ML Irrigation
              </p>

              <p className="mt-1 text-xl font-bold">

                {recommendation
                  ? recommendation.irrigation_required
                    ? "Required"
                    : "Not Required"
                  : "--"}

              </p>

            </div>

          </div>

        </section>

        {/* NOTIFICATION PREFERENCES */}

        <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

          <h2 className="text-lg font-bold">
            🔔 Notification Preferences
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Delivery channels for future alerts.
          </p>

          {/* WEB PUSH */}

          <div className="mt-4 rounded-xl border border-emerald-200 bg-emerald-50 p-4">

            <div className="flex items-center justify-between gap-3">

              <div>

                <p className="font-semibold">
                  📱 Web Push
                </p>

                <p className="text-xs text-slate-500">
                  Browser notifications
                </p>

              </div>

              <span
                className={`rounded-full px-3 py-1 text-xs font-bold ${
                  notificationPermission === "granted"
                    ? "bg-emerald-100 text-emerald-700"
                    : notificationPermission === "denied"
                    ? "bg-red-100 text-red-700"
                    : "bg-amber-100 text-amber-700"
                }`}
              >
                {notificationPermission ===
                "granted"
                  ? "Enabled"
                  : notificationPermission ===
                    "denied"
                  ? "Blocked"
                  : notificationPermission ===
                    "unsupported"
                  ? "Unsupported"
                  : "Not Enabled"}
              </span>

            </div>

            {notificationPermission !==
              "granted" &&
              notificationPermission !==
                "unsupported" && (

              <button
                onClick={enableWebPush}
                className="mt-4 w-full rounded-xl bg-emerald-600 px-4 py-3 font-semibold text-white shadow-sm transition hover:bg-emerald-700"
              >
                🔔 Enable Web Push Notifications
              </button>

            )}

            {notificationPermission ===
              "granted" && (

              <button
                onClick={sendTestNotification}
                className="mt-4 w-full rounded-xl bg-blue-600 px-4 py-3 font-semibold text-white shadow-sm transition hover:bg-blue-700"
              >
                🔔 Send Test Notification
              </button>

            )}

            {pushMessage && (

              <p className="mt-3 rounded-xl bg-white p-3 text-sm text-slate-700">
                {pushMessage}
              </p>

            )}

          </div>

          {/* SMS */}

          <div className="mt-3 flex items-center justify-between rounded-xl border border-slate-200 p-4">

            <div>

              <p className="font-semibold">
                💬 SMS
              </p>

              <p className="text-xs text-slate-500">
                Twilio integration
              </p>

            </div>

            <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-500">
              Next
            </span>

          </div>

          {/* EMAIL */}

          <div className="mt-3 flex items-center justify-between rounded-xl border border-slate-200 p-4">

            <div>

              <p className="font-semibold">
                📧 Email
              </p>

              <p className="text-xs text-slate-500">
                SendGrid integration
              </p>

            </div>

            <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-500">
              Next
            </span>

          </div>

        </section>

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