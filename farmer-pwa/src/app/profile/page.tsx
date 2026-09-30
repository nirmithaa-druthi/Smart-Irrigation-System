"use client";

import { useState } from "react";
import Link from "next/link";
import BottomNav from "../../components/BottomNav";

export default function ProfilePage() {
  const [farmerName, setFarmerName] =
    useState("Nirmitha Druthi");

  const [location, setLocation] =
    useState("Bengaluru");

  const [phone, setPhone] =
    useState("+91 XXXXX XXXXX");

  const [pushEnabled, setPushEnabled] =
    useState(true);

  const [smsEnabled, setSmsEnabled] =
    useState(false);

  const [emailEnabled, setEmailEnabled] =
    useState(true);

  const [language, setLanguage] =
    useState("English");

  const [saved, setSaved] =
    useState(false);

  function handleSave() {
    setSaved(true);

    setTimeout(() => {
      setSaved(false);
    }, 2500);
  }

  return (
    <main className="min-h-screen bg-slate-50 pb-24 text-slate-900">

      {/* HEADER */}

      <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/95 backdrop-blur">

        <div className="mx-auto flex max-w-3xl items-center gap-3 px-4 py-4">

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
              Farmer Profile
            </h1>

          </div>

        </div>

      </header>


      <div className="mx-auto max-w-3xl px-4 py-5">


        {/* PROFILE CARD */}

        <section className="mb-5 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">

          <div className="bg-gradient-to-br from-emerald-600 to-green-700 px-5 py-6 text-white">

            <div className="flex items-center gap-4">

              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-white text-3xl shadow-sm">
                👨‍🌾
              </div>

              <div>

                <p className="text-sm text-emerald-100">
                  Farmer
                </p>

                <h2 className="text-2xl font-bold">
                  {farmerName}
                </h2>

                <p className="text-sm text-emerald-100">
                  Smart Irrigation User
                </p>

              </div>

            </div>

          </div>


          <div className="space-y-4 p-5">

            <div>

              <label className="text-sm font-semibold text-slate-700">
                Farmer Name
              </label>

              <input
                value={farmerName}
                onChange={(e) =>
                  setFarmerName(e.target.value)
                }
                className="mt-1 w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-emerald-500"
              />

            </div>


            <div>

              <label className="text-sm font-semibold text-slate-700">
                Location
              </label>

              <input
                value={location}
                onChange={(e) =>
                  setLocation(e.target.value)
                }
                className="mt-1 w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-emerald-500"
              />

            </div>


            <div>

              <label className="text-sm font-semibold text-slate-700">
                Phone Number
              </label>

              <input
                value={phone}
                onChange={(e) =>
                  setPhone(e.target.value)
                }
                className="mt-1 w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-emerald-500"
              />

            </div>

          </div>

        </section>


        {/* LANGUAGE */}

        <section className="mb-5 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

          <div className="mb-4">

            <h2 className="text-lg font-bold">
              🌐 Language
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Choose your preferred farmer interface language.
            </p>

          </div>


          <div className="grid grid-cols-3 gap-2">

            {[
              "English",
              "हिन्दी",
              "ಕನ್ನಡ",
            ].map((item) => (

              <button
                key={item}
                onClick={() =>
                  setLanguage(item)
                }
                className={`rounded-xl border px-3 py-3 text-sm font-semibold transition ${
                  language === item
                    ? "border-emerald-500 bg-emerald-50 text-emerald-700"
                    : "border-slate-200 bg-white text-slate-600"
                }`}
              >
                {item}
              </button>

            ))}

          </div>


          <p className="mt-3 text-xs text-slate-500">

            Selected language:{" "}

            <span className="font-semibold">
              {language}
            </span>

          </p>

        </section>


        {/* NOTIFICATION PREFERENCES */}

        <section className="mb-5 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

          <div className="mb-4">

            <h2 className="text-lg font-bold">
              🔔 Notification Preferences
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Choose how you want to receive irrigation alerts.
            </p>

          </div>


          <div className="space-y-3">


            {/* PUSH */}

            <button
              onClick={() =>
                setPushEnabled(!pushEnabled)
              }
              className="flex w-full items-center justify-between rounded-xl border border-slate-200 p-4 text-left"
            >

              <div>

                <p className="font-semibold">
                  📱 Web Push
                </p>

                <p className="text-xs text-slate-500">
                  Instant browser notifications
                </p>

              </div>


              <div
                className={`h-6 w-11 rounded-full p-1 transition ${
                  pushEnabled
                    ? "bg-emerald-600"
                    : "bg-slate-300"
                }`}
              >

                <div
                  className={`h-4 w-4 rounded-full bg-white transition ${
                    pushEnabled
                      ? "translate-x-5"
                      : "translate-x-0"
                  }`}
                />

              </div>

            </button>


            {/* SMS */}

            <button
              onClick={() =>
                setSmsEnabled(!smsEnabled)
              }
              className="flex w-full items-center justify-between rounded-xl border border-slate-200 p-4 text-left"
            >

              <div>

                <p className="font-semibold">
                  💬 SMS
                </p>

                <p className="text-xs text-slate-500">
                  Irrigation alerts through SMS
                </p>

              </div>


              <div
                className={`h-6 w-11 rounded-full p-1 transition ${
                  smsEnabled
                    ? "bg-emerald-600"
                    : "bg-slate-300"
                }`}
              >

                <div
                  className={`h-4 w-4 rounded-full bg-white transition ${
                    smsEnabled
                      ? "translate-x-5"
                      : "translate-x-0"
                  }`}
                />

              </div>

            </button>


            {/* EMAIL */}

            <button
              onClick={() =>
                setEmailEnabled(!emailEnabled)
              }
              className="flex w-full items-center justify-between rounded-xl border border-slate-200 p-4 text-left"
            >

              <div>

                <p className="font-semibold">
                  📧 Email
                </p>

                <p className="text-xs text-slate-500">
                  Detailed irrigation reports
                </p>

              </div>


              <div
                className={`h-6 w-11 rounded-full p-1 transition ${
                  emailEnabled
                    ? "bg-emerald-600"
                    : "bg-slate-300"
                }`}
              >

                <div
                  className={`h-4 w-4 rounded-full bg-white transition ${
                    emailEnabled
                      ? "translate-x-5"
                      : "translate-x-0"
                  }`}
                />

              </div>

            </button>

          </div>

        </section>


        {/* SYSTEM INFORMATION */}

        <section className="mb-5 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

          <h2 className="text-lg font-bold">
            🌱 System Information
          </h2>


          <div className="mt-4 space-y-3 text-sm">

            <div className="flex justify-between gap-4">

              <span className="text-slate-500">
                Platform
              </span>

              <span className="font-semibold">
                Farmer PWA
              </span>

            </div>


            <div className="flex justify-between gap-4">

              <span className="text-slate-500">
                AI Engine
              </span>

              <span className="font-semibold">
                ML Irrigation Engine
              </span>

            </div>


            <div className="flex justify-between gap-4">

              <span className="text-slate-500">
                Weather
              </span>

              <span className="font-semibold">
                Weather API
              </span>

            </div>


            <div className="flex justify-between gap-4">

              <span className="text-slate-500">
                Notifications
              </span>

              <span className="font-semibold text-emerald-600">
                Configurable
              </span>

            </div>

          </div>

        </section>


        {/* SAVE */}

        <button
          onClick={handleSave}
          className="w-full rounded-xl bg-emerald-600 px-4 py-3 font-semibold text-white shadow-sm transition hover:bg-emerald-700"
        >

          {saved
            ? "✓ Profile Saved"
            : "Save Profile Settings"}

        </button>


        {saved && (

          <p className="mt-3 text-center text-sm text-emerald-600">
            Your profile preferences have been saved for this session.
          </p>

        )}

      </div>


      <BottomNav />

    </main>
  );
}