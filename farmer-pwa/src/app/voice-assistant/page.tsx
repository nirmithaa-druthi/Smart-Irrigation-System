"use client";

import { useEffect, useState } from "react";
import {
  getFields,
  getIrrigationRecommendation,
  getLatestSensorData,
  getLatestWeather,
  getIrrigationHistory,
  type FieldResponse,
} from "../../api";
import BottomNav from "../../components/BottomNav";

type VoiceLanguage = "English" | "Hindi" | "Kannada";

const languages = {
  English: {
    recognition: "en-US",
    title: "Voice Assistant",
    subtitle: "Ask about your field, irrigation, weather or crop.",
    listen: "🎙️ Start Listening",
    listening: "🎙️ Listening...",
    ready: "Tap the microphone and speak clearly.",
    youSaid: "You said",
    response: "Assistant Response",
    field: "Select Field",
    language: "Language",
    speakAgain: "🔊 Speak Again",
  },
  Hindi: {
    recognition: "hi-IN",
    title: "वॉइस असिस्टेंट",
    subtitle: "अपने खेत, सिंचाई, मौसम या फसल के बारे में पूछें।",
    listen: "🎙️ सुनना शुरू करें",
    listening: "🎙️ सुन रहा है...",
    ready: "माइक्रोफोन दबाकर स्पष्ट रूप से बोलें।",
    youSaid: "आपने कहा",
    response: "असिस्टेंट का जवाब",
    field: "खेत चुनें",
    language: "भाषा",
    speakAgain: "🔊 फिर से सुनें",
  },
  Kannada: {
    recognition: "kn-IN",
    title: "ವಾಯ್ಸ್ ಅಸಿಸ್ಟೆಂಟ್",
    subtitle: "ನಿಮ್ಮ ಹೊಲ, ನೀರಾವರಿ, ಹವಾಮಾನ ಅಥವಾ ಬೆಳೆಯ ಬಗ್ಗೆ ಕೇಳಿ.",
    listen: "🎙️ ಕೇಳಲು ಪ್ರಾರಂಭಿಸಿ",
    listening: "🎙️ ಕೇಳುತ್ತಿದೆ...",
    ready: "ಮೈಕ್ರೋಫೋನ್ ಒತ್ತಿ ಸ್ಪಷ್ಟವಾಗಿ ಮಾತನಾಡಿ.",
    youSaid: "ನೀವು ಹೇಳಿದ್ದು",
    response: "ಅಸಿಸ್ಟೆಂಟ್ ಉತ್ತರ",
    field: "ಹೊಲ ಆಯ್ಕೆಮಾಡಿ",
    language: "ಭಾಷೆ",
    speakAgain: "🔊 ಮತ್ತೆ ಕೇಳಿ",
  },
};

export default function VoiceAssistantPage() {
  const [fields, setFields] = useState<FieldResponse[]>([]);
  const [selectedField, setSelectedField] =
    useState<FieldResponse | null>(null);

  const [language, setLanguage] =
    useState<VoiceLanguage>("English");

  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [error, setError] = useState("");

  const t = languages[language];

  /* =========================================================
     LOAD FIELDS
     ========================================================= */

  useEffect(() => {
    async function loadFields() {
      try {
        const result = await getFields();

        setFields(result);

        if (result.length > 0) {
          const preferred = result.find(
            (field) => field.field_id === "FIELD001"
          );

          setSelectedField(preferred ?? result[0]);
        }
      } catch (err) {
        console.error("Field loading error:", err);

        setError(
          err instanceof Error
            ? err.message
            : "Unable to load fields."
        );
      }
    }

    loadFields();
  }, []);

  /* =========================================================
     FIELD NAME
     ========================================================= */

  function getFieldName(fieldName: string) {
    const value = fieldName.toLowerCase().trim();

    if (language === "Hindi") {
      if (value === "east field") return "पूर्व का खेत";
      if (value === "south field") return "दक्षिण का खेत";
      if (value === "bengaluru") return "बेंगलुरु";
      if (value === "mysuru") return "मैसूरु";
      if (value === "mangaluru") return "मंगलुरु";
    }

    if (language === "Kannada") {
      if (value === "east field") return "ಪೂರ್ವದ ಹೊಲ";
      if (value === "south field") return "ದಕ್ಷಿಣದ ಹೊಲ";
      if (value === "bengaluru") return "ಬೆಂಗಳೂರು";
      if (value === "mysuru") return "ಮೈಸೂರು";
      if (value === "mangaluru") return "ಮಂಗಳೂರು";
    }

    return fieldName;
  }

  /* =========================================================
     SARVAM TEXT TO SPEECH
     ========================================================= */

  async function speak(text: string) {
    if (!text.trim()) return;

    try {
      setSpeaking(true);
      setError("");

      const res = await fetch(
        "http://127.0.0.1:8003/speak",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            text,
            language,
          }),
        }
      );

      if (!res.ok) {
        throw new Error(
          "Unable to generate Sarvam voice."
        );
      }

      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);

      audio.onended = () => {
        URL.revokeObjectURL(url);
        setSpeaking(false);
      };

      audio.onerror = () => {
        URL.revokeObjectURL(url);
        setSpeaking(false);
        setError(
          language === "English"
            ? "Unable to play the generated voice."
            : language === "Hindi"
            ? "जनरेट की गई आवाज़ चलाने में समस्या हुई।"
            : "ರಚಿಸಲಾದ ಧ್ವನಿಯನ್ನು ಪ್ಲೇ ಮಾಡಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ."
        );
      };

      await audio.play();
    } catch (err) {
      console.error("Sarvam speech error:", err);
      setSpeaking(false);

      setError(
        err instanceof Error
          ? err.message
          : "Unable to generate voice."
      );
    }
  }

  /* =========================================================
     LIVE ML DATA
     ========================================================= */

  async function getMLRecommendation() {
    if (!selectedField) return null;

    const fieldId = selectedField.field_id;

    const sensor =
      await getLatestSensorData(fieldId);

    const weather =
      await getLatestWeather(fieldId);

    const history =
      await getIrrigationHistory(fieldId);

    let previousWaterUsage = 0;

    if (
      history.history &&
      history.history.length > 0
    ) {
      const sorted = [...history.history].sort(
        (a, b) =>
          new Date(
            b.irrigation_timestamp
          ).getTime() -
          new Date(
            a.irrigation_timestamp
          ).getTime()
      );

      previousWaterUsage =
        Number(
          sorted[0].water_used_liters
        ) || 0;
    }

    const now = new Date();

    return getIrrigationRecommendation({
      field_id: fieldId,
      soil_moisture: Number(
        sensor.soil_moisture
      ),
      temperature: Number(
        weather.temperature
      ),
      humidity: Number(weather.humidity),
      rainfall: Number(weather.rainfall),
      rain_probability: Number(
        weather.rain_probability
      ),
      crop_type: selectedField.crop_type,
      growth_stage: Number(
        selectedField.growth_stage
      ),
      hour: now.getHours(),
      day_of_week: now.getDay(),
      day_of_month: now.getDate(),
      previous_water_usage_liters:
        previousWaterUsage,
    });
  }

  /* =========================================================
     QUESTION ANSWER
     ========================================================= */

  async function answerQuestion(question: string) {
    if (!selectedField) {
      setError(
        language === "English"
          ? "Please select a field first."
          : language === "Hindi"
          ? "कृपया पहले एक खेत चुनें।"
          : "ದಯವಿಟ್ಟು ಮೊದಲು ಒಂದು ಹೊಲವನ್ನು ಆಯ್ಕೆಮಾಡಿ."
      );
      return;
    }

    try {
      setLoading(true);
      setError("");
      setResponse("");

      const q = question.toLowerCase().trim();

      const fieldName = getFieldName(
        selectedField.field_name
      );

      const result =
        await getMLRecommendation();

      if (!result) {
        throw new Error(
          "Unable to get irrigation recommendation."
        );
      }

      let message = "";

      /* ================= ENGLISH ================= */

      if (language === "English") {
        if (
          q.includes("water") ||
          q.includes("litre") ||
          q.includes("liter") ||
          q.includes("quantity") ||
          q.includes("how much")
        ) {
          message =
            `The recommended water quantity for ${fieldName} is ` +
            `${Number(
              result.predicted_water_quantity_liters
            ).toFixed(1)} liters.`;
        } else if (
          q.includes("irrigation") ||
          q.includes("irrigate") ||
          q.includes("watering")
        ) {
          message = result.irrigation_required
            ? `Yes. Irrigation is required for ${fieldName}. ` +
              `The recommended quantity is ` +
              `${Number(
                result.predicted_water_quantity_liters
              ).toFixed(1)} liters.`
            : `No. Irrigation is not required for ${fieldName} right now.`;
        } else if (
          q.includes("soil") ||
          q.includes("moisture")
        ) {
          const sensor =
            await getLatestSensorData(
              selectedField.field_id
            );

          message =
            `The current soil moisture for ${fieldName} is ` +
            `${Number(
              sensor.soil_moisture
            ).toFixed(1)} percent.`;
        } else if (
          q.includes("crop")
        ) {
          message =
            `The selected crop for ${fieldName} is ` +
            `${selectedField.crop_type}.`;
        } else if (
          q.includes("stage") ||
          q.includes("growth")
        ) {
          message =
            `The current growth stage for ${fieldName} is ` +
            `${selectedField.growth_stage}.`;
        } else if (
          q.includes("weather") ||
          q.includes("rain") ||
          q.includes("temperature") ||
          q.includes("humidity")
        ) {
          const weather =
            await getLatestWeather(
              selectedField.field_id
            );

          message =
            `The current weather for ${fieldName} is ` +
            `${Number(weather.temperature).toFixed(1)} degrees Celsius, ` +
            `humidity ${Number(weather.humidity).toFixed(1)} percent, ` +
            `rainfall ${Number(weather.rainfall).toFixed(1)} millimeters, ` +
            `and rain probability ${Number(
              weather.rain_probability
            ).toFixed(1)} percent.`;
        } else if (
          q.includes("hello") ||
          q.includes("hi") ||
          q.includes("hey")
        ) {
          message =
            `Hello! I am your smart irrigation assistant. ` +
            `You can ask me about ${fieldName}, soil moisture, ` +
            `irrigation, water quantity, weather or your crop.`;
        } else {
          message =
            `For ${fieldName}, the current ML recommendation is: ` +
            `${result.irrigation_required
              ? "irrigation is required"
              : "irrigation is not required"
            }. ` +
            `The recommended water quantity is ` +
            `${Number(
              result.predicted_water_quantity_liters
            ).toFixed(1)} liters.`;
        }
      }

      /* ================= HINDI ================= */

      if (language === "Hindi") {
        if (
          q.includes("पानी") ||
          q.includes("कितना") ||
          q.includes("सिंचाई")
        ) {
          message =
            `${fieldName} के लिए अनुशंसित पानी की मात्रा ` +
            `${Number(
              result.predicted_water_quantity_liters
            ).toFixed(1)} लीटर है।`;
        } else if (
          q.includes("मिट्टी") ||
          q.includes("नमी")
        ) {
          const sensor =
            await getLatestSensorData(
              selectedField.field_id
            );

          message =
            `${fieldName} में वर्तमान मिट्टी की नमी ` +
            `${Number(
              sensor.soil_moisture
            ).toFixed(1)} प्रतिशत है।`;
        } else if (
          q.includes("मौसम") ||
          q.includes("बारिश") ||
          q.includes("तापमान")
        ) {
          const weather =
            await getLatestWeather(
              selectedField.field_id
            );

          message =
            `${fieldName} में वर्तमान तापमान ` +
            `${Number(weather.temperature).toFixed(1)} डिग्री सेल्सियस है। ` +
            `नमी ${Number(weather.humidity).toFixed(1)} प्रतिशत और ` +
            `बारिश की संभावना ${Number(
              weather.rain_probability
            ).toFixed(1)} प्रतिशत है।`;
        } else {
          message = result.irrigation_required
            ? `${fieldName} में अभी सिंचाई की आवश्यकता है। ` +
              `अनुशंसित पानी ${Number(
                result.predicted_water_quantity_liters
              ).toFixed(1)} लीटर है।`
            : `${fieldName} में अभी सिंचाई की आवश्यकता नहीं है।`;
        }
      }

      /* ================= KANNADA ================= */

      if (language === "Kannada") {
        if (
          q.includes("ನೀರು") ||
          q.includes("ಎಷ್ಟು") ||
          q.includes("ನೀರಾವರಿ") ||
          q.includes("ಬೇಕಾಗಿದೆ") ||
          q.includes("ಬೇಕಾಗುತ್ತದೆ")
        ) {
          message =
            `${fieldName}ಕ್ಕೆ ಶಿಫಾರಸು ಮಾಡಲಾದ ನೀರಿನ ಪ್ರಮಾಣ ` +
            `${Number(
              result.predicted_water_quantity_liters
            ).toFixed(1)} ಲೀಟರ್.`;
        } else if (
          q.includes("ಮಣ್ಣು") ||
          q.includes("ತೇವಾಂಶ")
        ) {
          const sensor =
            await getLatestSensorData(
              selectedField.field_id
            );

          message =
            `${fieldName}ದ ಪ್ರಸ್ತುತ ಮಣ್ಣಿನ ತೇವಾಂಶ ` +
            `${Number(
              sensor.soil_moisture
            ).toFixed(1)} ಶೇಕಡಾ ಇದೆ.`;
        } else if (
          q.includes("ಹವಾಮಾನ") ||
          q.includes("ಮಳೆ") ||
          q.includes("ತಾಪಮಾನ")
        ) {
          const weather =
            await getLatestWeather(
              selectedField.field_id
            );

          message =
            `${fieldName}ದ ಪ್ರಸ್ತುತ ತಾಪಮಾನ ` +
            `${Number(weather.temperature).toFixed(1)} ಡಿಗ್ರಿ ಸೆಲ್ಸಿಯಸ್. ` +
            `ಆರ್ದ್ರತೆ ${Number(weather.humidity).toFixed(1)} ಶೇಕಡಾ ಮತ್ತು ` +
            `ಮಳೆಯ ಸಾಧ್ಯತೆ ${Number(
              weather.rain_probability
            ).toFixed(1)} ಶೇಕಡಾ.`;
        } else {
          message = result.irrigation_required
            ? `${fieldName}ಗೆ ಈಗ ನೀರಾವರಿ ಅಗತ್ಯವಿದೆ. ` +
              `ಶಿಫಾರಸು ಮಾಡಲಾದ ನೀರಿನ ಪ್ರಮಾಣ ` +
              `${Number(
                result.predicted_water_quantity_liters
              ).toFixed(1)} ಲೀಟರ್.`
            : `${fieldName}ಗೆ ಈಗ ನೀರಾವರಿ ಅಗತ್ಯವಿಲ್ಲ.`;
        }
      }

      setResponse(message);

      await speak(message);
    } catch (err) {
      console.error(
        "Question answering error:",
        err
      );

      setError(
        err instanceof Error
          ? err.message
          : language === "English"
          ? "Unable to answer your question."
          : language === "Hindi"
          ? "आपके सवाल का जवाब नहीं दिया जा सका।"
          : "ನಿಮ್ಮ ಪ್ರಶ್ನೆಗೆ ಉತ್ತರಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ."
      );
    } finally {
      setLoading(false);
    }
  }

  /* =========================================================
     VOICE RECOGNITION
     ========================================================= */

  function startListening() {
    setError("");
    setTranscript("");
    setResponse("");

    const SpeechRecognition =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setError(
        language === "English"
          ? "Voice recognition is not supported. Please use Google Chrome."
          : language === "Hindi"
          ? "वॉइस रिकग्निशन उपलब्ध नहीं है। कृपया Google Chrome का उपयोग करें।"
          : "ವಾಯ್ಸ್ ರೆಕಗ್ನಿಷನ್ ಲಭ್ಯವಿಲ್ಲ. ದಯವಿಟ್ಟು Google Chrome ಬಳಸಿ."
      );
      return;
    }

    const recognition = new SpeechRecognition();

    recognition.lang = t.recognition;
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.maxAlternatives = 5;

    setIsListening(true);

    recognition.onstart = () => {
      console.log(
        "🎤 Recognition started:",
        t.recognition
      );
      setIsListening(true);
    };

    recognition.onaudiostart = () => {
      console.log("🎙️ Microphone audio started");
    };

    recognition.onspeechstart = () => {
      console.log("🗣️ Speech detected");
    };

    recognition.onspeechend = () => {
      console.log("🛑 Speech ended");
    };

    recognition.onresult = (event: any) => {
      const result = event.results?.[0]?.[0];

      if (!result) {
        setIsListening(false);
        return;
      }

      const text = String(
        result.transcript || ""
      ).trim();

      console.log(
        "✅ Recognized:",
        text
      );

      if (!text) {
        setIsListening(false);
        setError(
          language === "English"
            ? "I didn't hear anything. Please try again."
            : language === "Hindi"
            ? "मुझे कुछ सुनाई नहीं दिया। कृपया फिर से बोलें।"
            : "ನನಗೆ ಏನೂ ಕೇಳಿಸಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ."
        );
        return;
      }

      setTranscript(text);
      setIsListening(false);

      void answerQuestion(text);
    };

    recognition.onerror = (event: any) => {
      const errorCode = event?.error;

      console.log(
        "Voice recognition status:",
        errorCode
      );

      /*
       * no-speech is NOT a React/JavaScript crash.
       * Chrome simply did not detect speech.
       */
      if (errorCode === "no-speech") {
        setIsListening(false);

        setError(
          language === "English"
            ? "I didn't hear you. Tap the microphone and speak clearly."
            : language === "Hindi"
            ? "मुझे आपकी आवाज़ सुनाई नहीं दी। माइक्रोफोन दबाकर स्पष्ट रूप से बोलें।"
            : "ನನಗೆ ನಿಮ್ಮ ಧ್ವನಿ ಕೇಳಿಸಲಿಲ್ಲ. ಮೈಕ್ರೋಫೋನ್ ಒತ್ತಿ ಸ್ಪಷ್ಟವಾಗಿ ಮಾತನಾಡಿ."
        );

        return;
      }

      if (
        errorCode === "not-allowed" ||
        errorCode === "service-not-allowed"
      ) {
        setIsListening(false);

        setError(
          language === "English"
            ? "Microphone access is blocked. Allow microphone permission for this site."
            : language === "Hindi"
            ? "माइक्रोफोन की अनुमति बंद है। इस साइट के लिए माइक्रोफोन की अनुमति दें।"
            : "ಮೈಕ್ರೋಫೋನ್ ಅನುಮತಿ ನಿರ್ಬಂಧಿಸಲಾಗಿದೆ. ಈ ಸೈಟ್‌ಗೆ ಮೈಕ್ರೋಫೋನ್ ಅನುಮತಿ ನೀಡಿ."
        );

        return;
      }

      if (errorCode === "network") {
        setIsListening(false);

        setError(
          language === "English"
            ? "Speech recognition needs an internet connection."
            : language === "Hindi"
            ? "वॉइस रिकग्निशन के लिए इंटरनेट कनेक्शन आवश्यक है।"
            : "ವಾಯ್ಸ್ ರೆಕಗ್ನಿಷನ್‌ಗೆ ಇಂಟರ್ನೆಟ್ ಸಂಪರ್ಕ ಅಗತ್ಯವಿದೆ."
        );

        return;
      }

      if (errorCode === "aborted") {
        setIsListening(false);
        return;
      }

      console.error(
        "Voice recognition error:",
        errorCode
      );

      setIsListening(false);

      setError(
        language === "English"
          ? "Voice recognition stopped. Please try again."
          : language === "Hindi"
          ? "वॉइस रिकग्निशन रुक गया। कृपया फिर से प्रयास करें।"
          : "ವಾಯ್ಸ್ ರೆಕಗ್ನಿಷನ್ ನಿಂತಿದೆ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ."
      );
    };

    recognition.onend = () => {
      console.log("🎤 Recognition ended");
      setIsListening(false);
    };

    try {
      recognition.start();
    } catch (err) {
      console.error(
        "Recognition start error:",
        err
      );

      setIsListening(false);

      setError(
        language === "English"
          ? "Unable to start the microphone. Please try again."
          : language === "Hindi"
          ? "माइक्रोफोन शुरू नहीं हो सका। कृपया फिर से प्रयास करें।"
          : "ಮೈಕ್ರೋಫೋನ್ ಪ್ರಾರಂಭಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ."
      );
    }
  }

  /* =========================================================
     LANGUAGE CHANGE
     ========================================================= */

  function changeLanguage(
    value: VoiceLanguage
  ) {
    setLanguage(value);
    setTranscript("");
    setResponse("");
    setError("");
  }

  /* =========================================================
     UI
     ========================================================= */

  return (
    <main className="min-h-screen bg-slate-950 pb-24 text-white">
      <div className="mx-auto max-w-3xl px-4 py-6 sm:px-6">

        {/* HEADER */}
        <section className="mb-6 rounded-3xl border border-emerald-400/20 bg-gradient-to-br from-emerald-900 via-slate-900 to-slate-950 p-6 shadow-xl">
          <p className="mb-2 text-sm font-medium text-emerald-300">
            🌱 Smart Irrigation System
          </p>

          <h1 className="text-3xl font-bold">
            {t.title}
          </h1>

          <p className="mt-2 text-sm text-slate-300">
            {t.subtitle}
          </p>
        </section>

        {/* CONTROLS */}
        <section className="mb-5 rounded-3xl border border-slate-800 bg-slate-900 p-5">

          <div className="grid gap-4 sm:grid-cols-2">

            <div>
              <label className="mb-2 block text-sm font-semibold text-slate-300">
                {t.language}
              </label>

              <select
                value={language}
                onChange={(e) =>
                  changeLanguage(
                    e.target.value as VoiceLanguage
                  )
                }
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none focus:border-emerald-400"
              >
                <option value="English">
                  English
                </option>
                <option value="Hindi">
                  हिन्दी
                </option>
                <option value="Kannada">
                  ಕನ್ನಡ
                </option>
              </select>
            </div>

            <div>
              <label className="mb-2 block text-sm font-semibold text-slate-300">
                {t.field}
              </label>

              <select
                value={
                  selectedField?.field_id || ""
                }
                onChange={(e) => {
                  const field =
                    fields.find(
                      (item) =>
                        item.field_id ===
                        e.target.value
                    );

                  setSelectedField(
                    field ?? null
                  );

                  setTranscript("");
                  setResponse("");
                  setError("");
                }}
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none focus:border-emerald-400"
              >
                {fields.map((field) => (
                  <option
                    key={field.field_id}
                    value={field.field_id}
                  >
                    {field.field_name}
                  </option>
                ))}
              </select>
            </div>

          </div>
        </section>

        {/* MICROPHONE */}
        <section className="mb-5 rounded-3xl border border-emerald-400/20 bg-emerald-950/30 p-6 text-center">

          <div
            className={`mx-auto mb-5 flex h-28 w-28 items-center justify-center rounded-full border-4 transition ${
              isListening
                ? "animate-pulse border-red-400 bg-red-500/20"
                : "border-emerald-400 bg-emerald-500/10"
            }`}
          >
            <span className="text-5xl">
              {isListening ? "🎙️" : "🎤"}
            </span>
          </div>

          <button
            type="button"
            onClick={startListening}
            disabled={isListening || loading}
            className="w-full rounded-2xl bg-emerald-500 px-6 py-4 text-lg font-bold text-slate-950 transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isListening
              ? t.listening
              : t.listen}
          </button>

          <p className="mt-4 text-sm text-slate-400">
            {t.ready}
          </p>

        </section>

        {/* TRANSCRIPT */}
        {transcript && (
          <section className="mb-5 rounded-3xl border border-slate-800 bg-slate-900 p-5">
            <p className="mb-2 text-xs font-bold uppercase tracking-wider text-emerald-400">
              {t.youSaid}
            </p>

            <p className="text-lg text-white">
              {transcript}
            </p>
          </section>
        )}

        {/* LOADING */}
        {loading && (
          <section className="mb-5 rounded-3xl border border-blue-400/20 bg-blue-950/30 p-5 text-center">
            <div className="mb-2 text-3xl">
              🤖
            </div>

            <p className="text-sm text-blue-200">
              Checking live field, sensor,
              weather and ML data...
            </p>
          </section>
        )}

        {/* RESPONSE */}
        {response && !loading && (
          <section className="mb-5 rounded-3xl border border-emerald-400/20 bg-slate-900 p-6">

            <div className="mb-4 flex items-center justify-between gap-3">
              <p className="text-xs font-bold uppercase tracking-wider text-emerald-400">
                {t.response}
              </p>

              <button
                type="button"
                onClick={() =>
                  void speak(response)
                }
                disabled={speaking}
                className="rounded-xl border border-emerald-400/30 bg-emerald-500/10 px-4 py-2 text-sm font-semibold text-emerald-300 disabled:opacity-50"
              >
                {speaking
                  ? "🔊 Speaking..."
                  : t.speakAgain}
              </button>
            </div>

            <p className="text-lg leading-8 text-white">
              {response}
            </p>

          </section>
        )}

        {/* ERROR */}
        {error && (
          <section className="mb-5 rounded-3xl border border-red-400/30 bg-red-950/30 p-5">
            <div className="flex gap-3">
              <span className="text-xl">
                ⚠️
              </span>

              <div>
                <p className="font-semibold text-red-300">
                  Voice Assistant
                </p>

                <p className="mt-1 text-sm leading-6 text-red-200">
                  {error}
                </p>
              </div>
            </div>
          </section>
        )}

        {/* QUICK QUESTIONS */}
        <section className="rounded-3xl border border-slate-800 bg-slate-900 p-5">
          <p className="mb-4 text-sm font-bold text-slate-200">
            Try asking
          </p>

          <div className="grid gap-3 sm:grid-cols-2">
            {[
              "How much water does my field need?",
              "What is my soil moisture?",
              "What is the weather?",
              "Is irrigation required?",
            ].map((question) => (
              <button
                key={question}
                type="button"
                onClick={() =>
                  void answerQuestion(
                    question
                  )
                }
                disabled={loading}
                className="rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-left text-sm text-slate-300 transition hover:border-emerald-400 hover:text-white disabled:opacity-50"
              >
                {question}
              </button>
            ))}
          </div>
        </section>

      </div>

      <BottomNav />
    </main>
  );
}