"use client";

import { useEffect, useState } from "react";

import {
  createField,
  getFields,
  type FieldResponse,
} from "../../api";

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

function formatCrop(crop: string) {
  return crop
    .replace(/_/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export default function FieldsPage() {
  const [fields, setFields] = useState<FieldResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    field_name: "",
    soil_moisture: "15",
    location: "Bengaluru",
    field_size: "1",
    crop_type: "rice",
    growth_stage: "1",
  });

  async function loadFields() {
    setLoading(true);
    setError("");

    try {
      const result = await getFields();
      setFields(result);
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

  useEffect(() => {
    loadFields();
  }, []);

  async function handleSubmit(
    event: React.FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();
    setError("");

    try {
      await createField({
        field_name: form.field_name,
        soil_moisture: Number(form.soil_moisture),
        location: form.location,
        field_size: Number(form.field_size),
        crop_type: form.crop_type,
        growth_stage: form.growth_stage,
      });

      setForm({
        field_name: "",
        soil_moisture: "15",
        location: "Bengaluru",
        field_size: "1",
        crop_type: "rice",
        growth_stage: "1",
      });

      setShowForm(false);

      await loadFields();
    } catch (err) {
      console.error(err);

      setError(
        err instanceof Error
          ? err.message
          : "Unable to create field."
      );
    }
  }

  return (
    <main className="min-h-screen bg-slate-50 pb-24 text-slate-900">
      {/* HEADER */}

      <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/95 backdrop-blur">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-emerald-600">
              Smart Irrigation
            </p>

            <h1 className="text-xl font-bold">
              My Fields
            </h1>
          </div>

          <button
            onClick={() => setShowForm(!showForm)}
            className="rounded-xl bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-emerald-700"
          >
            {showForm ? "Close" : "+ Add Field"}
          </button>
        </div>
      </header>

      <div className="mx-auto max-w-5xl px-4 py-5">
        {/* INTRO */}

        <section className="mb-5">
          <h2 className="text-2xl font-bold">
            Manage Your Fields
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            View and register the fields connected to
            your smart irrigation system.
          </p>
        </section>

        {/* ERROR */}

        {error && (
          <div className="mb-5 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        )}

        {/* ADD FIELD FORM */}

        {showForm && (
          <section className="mb-6 rounded-2xl border border-emerald-200 bg-white p-5 shadow-sm">
            <h3 className="text-lg font-bold">
              Register New Field
            </h3>

            <p className="mt-1 text-sm text-slate-500">
              Enter the details of your field.
            </p>

            <form
              onSubmit={handleSubmit}
              className="mt-5 grid gap-4 sm:grid-cols-2"
            >
              <label className="text-sm font-medium">
                Field Name

                <input
                  required
                  value={form.field_name}
                  onChange={(event) =>
                    setForm({
                      ...form,
                      field_name:
                        event.target.value,
                    })
                  }
                  placeholder="Example: North Field"
                  className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-3 outline-none focus:border-emerald-500"
                />
              </label>

              <label className="text-sm font-medium">
                Location

                <input
                  value={form.location}
                  onChange={(event) =>
                    setForm({
                      ...form,
                      location:
                        event.target.value,
                    })
                  }
                  className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-3 outline-none focus:border-emerald-500"
                />
              </label>

              <label className="text-sm font-medium">
                Field Size (acres)

                <input
                  required
                  type="number"
                  min="0.1"
                  step="0.1"
                  value={form.field_size}
                  onChange={(event) =>
                    setForm({
                      ...form,
                      field_size:
                        event.target.value,
                    })
                  }
                  className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-3 outline-none focus:border-emerald-500"
                />
              </label>

              <label className="text-sm font-medium">
                Soil Moisture (%)

                <input
                  required
                  type="number"
                  min="0"
                  max="100"
                  value={form.soil_moisture}
                  onChange={(event) =>
                    setForm({
                      ...form,
                      soil_moisture:
                        event.target.value,
                    })
                  }
                  className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-3 outline-none focus:border-emerald-500"
                />
              </label>

              <label className="text-sm font-medium">
                Crop

                <select
                  value={form.crop_type}
                  onChange={(event) =>
                    setForm({
                      ...form,
                      crop_type:
                        event.target.value,
                    })
                  }
                  className="mt-1 w-full rounded-xl border border-slate-300 bg-white px-3 py-3 outline-none focus:border-emerald-500"
                >
                  {supportedCrops.map((crop) => (
                    <option
                      key={crop}
                      value={crop}
                    >
                      {formatCrop(crop)}
                    </option>
                  ))}
                </select>
              </label>

              <label className="text-sm font-medium">
                Growth Stage

                <select
                  value={form.growth_stage}
                  onChange={(event) =>
                    setForm({
                      ...form,
                      growth_stage:
                        event.target.value,
                    })
                  }
                  className="mt-1 w-full rounded-xl border border-slate-300 bg-white px-3 py-3 outline-none focus:border-emerald-500"
                >
                  <option value="1">
                    Stage 1
                  </option>

                  <option value="2">
                    Stage 2
                  </option>

                  <option value="3">
                    Stage 3
                  </option>
                </select>
              </label>

              <div className="flex gap-3 sm:col-span-2">
                <button
                  type="submit"
                  className="flex-1 rounded-xl bg-emerald-600 px-4 py-3 font-semibold text-white hover:bg-emerald-700"
                >
                  Save Field
                </button>

                <button
                  type="button"
                  onClick={() =>
                    setShowForm(false)
                  }
                  className="rounded-xl border border-slate-300 px-4 py-3 font-semibold text-slate-700"
                >
                  Cancel
                </button>
              </div>
            </form>
          </section>
        )}

        {/* FIELD LIST */}

        <section>
          <div className="mb-3 flex items-center justify-between">
            <h3 className="text-lg font-bold">
              Registered Fields
            </h3>

            <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-700">
              {fields.length}{" "}
              {fields.length === 1
                ? "Field"
                : "Fields"}
            </span>
          </div>

          {loading ? (
            <div className="rounded-2xl bg-white p-8 text-center shadow-sm">
              <div className="mx-auto mb-3 h-8 w-8 animate-spin rounded-full border-4 border-emerald-200 border-t-emerald-600" />

              <p className="text-sm text-slate-500">
                Loading fields...
              </p>
            </div>
          ) : fields.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center">
              <div className="text-4xl">
                🌱
              </div>

              <h3 className="mt-3 font-semibold">
                No fields registered
              </h3>

              <p className="mt-1 text-sm text-slate-500">
                Add your first field to get started.
              </p>
            </div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2">
              {fields.map((field) => (
                <div
                  key={field.field_id}
                  className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-50 text-2xl">
                        🌱
                      </div>

                      <div>
                        <h4 className="font-bold">
                          {field.field_name}
                        </h4>

                        <p className="text-xs text-slate-500">
                          {field.field_id}
                        </p>
                      </div>
                    </div>

                    <span className="rounded-full bg-emerald-50 px-2.5 py-1 text-[10px] font-bold text-emerald-700">
                      ACTIVE
                    </span>
                  </div>

                  <div className="mt-5 grid grid-cols-2 gap-3">
                    <div className="rounded-xl bg-slate-50 p-3">
                      <p className="text-xs text-slate-500">
                        Crop
                      </p>

                      <p className="mt-1 font-semibold">
                        {formatCrop(
                          field.crop_type
                        )}
                      </p>
                    </div>

                    <div className="rounded-xl bg-slate-50 p-3">
                      <p className="text-xs text-slate-500">
                        Growth Stage
                      </p>

                      <p className="mt-1 font-semibold">
                        Stage{" "}
                        {field.growth_stage}
                      </p>
                    </div>

                    <div className="rounded-xl bg-slate-50 p-3">
                      <p className="text-xs text-slate-500">
                        Field Size
                      </p>

                      <p className="mt-1 font-semibold">
                        {field.field_size} acres
                      </p>
                    </div>

                    <div className="rounded-xl bg-slate-50 p-3">
                      <p className="text-xs text-slate-500">
                        Farmer ID
                      </p>

                      <p className="mt-1 font-semibold">
                        {field.farmer_id}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>

      {/* MOBILE NAVIGATION */}

      <div className="sm:hidden">
        {/* Reusing the existing mobile navigation */}
      </div>
    </main>
  );
}