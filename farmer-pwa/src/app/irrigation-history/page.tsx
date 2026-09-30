"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  getFields,
  getIrrigationHistory,
  type FieldResponse,
  type IrrigationHistoryItem,
} from "../../api";
import BottomNav from "../../components/BottomNav";

function formatCrop(crop: string) {
  return crop
    .replace(/_/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatDateTime(value: string) {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export default function IrrigationHistoryPage() {
  const router = useRouter();

  const [fields, setFields] = useState<FieldResponse[]>([]);
  const [selectedField, setSelectedField] =
    useState<FieldResponse | null>(null);

  const [history, setHistory] =
    useState<IrrigationHistoryItem[]>([]);

  const [loadingFields, setLoadingFields] = useState(true);
  const [loadingHistory, setLoadingHistory] = useState(false);

  const [error, setError] = useState("");

  // =========================================================
  // LOAD FIELDS
  // =========================================================

  useEffect(() => {
    async function loadFields() {
      try {
        setLoadingFields(true);
        setError("");

        const result = await getFields();

        setFields(result);

        if (result.length > 0) {
          const preferredField = result.find(
            (field) => field.field_id === "FIELD003"
          );

          setSelectedField(
            preferredField ?? result[0]
          );
        }
      } catch (err) {
        console.error("Field loading error:", err);

        setError(
          err instanceof Error
            ? err.message
            : "Unable to load fields."
        );
      } finally {
        setLoadingFields(false);
      }
    }

    loadFields();
  }, []);

  // =========================================================
  // LOAD SELECTED FIELD HISTORY
  // =========================================================

  useEffect(() => {
    if (!selectedField) return;

    const fieldId = selectedField.field_id;

    async function loadHistory() {
      try {
        setLoadingHistory(true);
        setError("");

        const result =
          await getIrrigationHistory(fieldId);

        setHistory(result.history);
      } catch (err) {
        console.error(
          "Irrigation history loading error:",
          err
        );

        setHistory([]);

        setError(
          err instanceof Error
            ? err.message
            : "Unable to load irrigation history."
        );
      } finally {
        setLoadingHistory(false);
      }
    }

    loadHistory();
  }, [selectedField]);

  // =========================================================
  // GO BACK TO DASHBOARD
  // =========================================================

  function goToDashboard() {
    router.replace("/dashboard");
  }

  // =========================================================
  // SUMMARY
  // =========================================================

  const totalWaterUsed = history.reduce(
    (total, record) =>
      total + record.water_used_liters,
    0
  );

  const averageWaterUsed =
    history.length > 0
      ? totalWaterUsed / history.length
      : 0;

  // =========================================================
  // CSV EXPORT
  // =========================================================

  function downloadCSV() {
    if (!selectedField) {
      alert("Please select a field first.");
      return;
    }

    const headers = [
      "History ID",
      "Field ID",
      "Crop",
      "Growth Stage",
      "Irrigation Date",
      "Water Used (Liters)",
      "Source",
      "Notes",
    ];

    const rows = history.map((record) => [
      record.history_id,
      record.field_id,
      formatCrop(record.crop_type),
      `Stage ${record.growth_stage}`,
      formatDateTime(
        record.irrigation_timestamp
      ),
      record.water_used_liters,
      record.source,
      record.notes ?? "",
    ]);

    const csvContent = [headers, ...rows]
      .map((row) =>
        row
          .map((value) => {
            const text = String(value);

            return `"${text.replace(
              /"/g,
              '""'
            )}"`;
          })
          .join(",")
      )
      .join("\r\n");

    const dataUri =
      "data:text/csv;charset=utf-8,\uFEFF" +
      encodeURIComponent(csvContent);

    const link =
      document.createElement("a");

    link.href = dataUri;

    link.download =
      `irrigation-history-${selectedField.field_id}.csv`;

    link.style.display = "none";

    document.body.appendChild(link);

    link.click();

    document.body.removeChild(link);
  }

  // =========================================================
  // PDF EXPORT
  // =========================================================

  async function downloadPDF() {
    if (!selectedField) {
      alert("Please select a field first.");
      return;
    }

    try {
      const { default: jsPDF } =
        await import("jspdf");

      const autoTableModule =
        await import("jspdf-autotable");

      const autoTable =
        autoTableModule.default ||
        autoTableModule.autoTable;

      const doc = new jsPDF();

      doc.setFontSize(18);
      doc.text(
        "Smart Irrigation System",
        14,
        20
      );

      doc.setFontSize(14);
      doc.text(
        "Irrigation History Report",
        14,
        30
      );

      doc.setFontSize(10);

      doc.text(
        `Field: ${selectedField.field_name}`,
        14,
        42
      );

      doc.text(
        `Field ID: ${selectedField.field_id}`,
        14,
        49
      );

      doc.text(
        `Crop: ${formatCrop(
          selectedField.crop_type
        )}`,
        14,
        56
      );

      doc.text(
        `Growth Stage: ${selectedField.growth_stage}`,
        14,
        63
      );

      doc.text(
        `Total Records: ${history.length}`,
        14,
        70
      );

      doc.text(
        `Total Water Used: ${totalWaterUsed.toFixed(
          2
        )} L`,
        14,
        77
      );

      doc.text(
        `Average Water Used: ${averageWaterUsed.toFixed(
          2
        )} L`,
        14,
        84
      );

      if (history.length > 0) {
        autoTable(doc, {
          startY: 94,

          head: [
            [
              "ID",
              "Date",
              "Crop",
              "Stage",
              "Water (L)",
              "Source",
            ],
          ],

          body: history.map((record) => [
            record.history_id,
            formatDateTime(
              record.irrigation_timestamp
            ),
            formatCrop(record.crop_type),
            `Stage ${record.growth_stage}`,
            record.water_used_liters.toFixed(2),
            record.source,
          ]),

          styles: {
            fontSize: 8,
          },

          headStyles: {
            fontStyle: "bold",
          },

          margin: {
            left: 14,
            right: 14,
          },
        });
      } else {
        doc.setFontSize(11);

        doc.text(
          "No irrigation records are available for this field.",
          14,
          100
        );

        doc.setFontSize(9);

        doc.text(
          "Records will appear here after irrigation events are recorded.",
          14,
          108
        );
      }

      doc.save(
        `irrigation-report-${selectedField.field_id}.pdf`
      );
    } catch (err) {
      console.error(
        "PDF generation error:",
        err
      );

      alert(
        "Unable to generate the PDF report. Please try again."
      );
    }
  }

  // =========================================================
  // UI
  // =========================================================

  return (
    <main className="min-h-screen bg-slate-50 pb-24 text-slate-900">

      {/* HEADER */}

      <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/95 backdrop-blur">
        <div className="mx-auto max-w-5xl px-4 py-4">

          <button
            type="button"
            onClick={goToDashboard}
            className="mb-4 flex items-center gap-2 text-sm font-semibold text-emerald-700 transition hover:text-emerald-900"
          >
            <span className="text-lg">
              ←
            </span>

            Back to Dashboard
          </button>

          <p className="text-xs font-semibold uppercase tracking-wider text-emerald-600">
            Smart Irrigation
          </p>

          <h1 className="mt-1 text-xl font-bold">
            Irrigation History
          </h1>

          <p className="mt-1 text-sm text-slate-500">
            View previous irrigation records for your fields.
          </p>

        </div>
      </header>

      <div className="mx-auto max-w-5xl px-4 py-5">

        {/* ERROR */}

        {error && (
          <div className="mb-5 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        )}

        {/* FIELD SELECTOR */}

        <section className="mb-5 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">

          <div className="mb-3">

            <h2 className="font-bold">
              Select Field
            </h2>

            <p className="mt-1 text-xs text-slate-500">
              Choose a field to view its irrigation history.
            </p>

          </div>

          {loadingFields ? (
            <div className="rounded-xl bg-slate-50 p-4 text-sm text-slate-500">
              Loading fields...
            </div>
          ) : fields.length === 0 ? (
            <div className="rounded-xl bg-slate-50 p-4 text-sm text-slate-500">
              No fields registered yet.
            </div>
          ) : (
            <div className="flex gap-3 overflow-x-auto pb-1">

              {fields.map((field) => {
                const selected =
                  selectedField?.field_id ===
                  field.field_id;

                return (
                  <button
                    key={field.field_id}
                    onClick={() =>
                      setSelectedField(field)
                    }
                    className={`min-w-[190px] rounded-2xl border p-4 text-left transition ${
                      selected
                        ? "border-emerald-500 bg-emerald-50 shadow-sm"
                        : "border-slate-200 bg-white hover:border-emerald-300"
                    }`}
                  >

                    <div className="flex items-center justify-between">

                      <span className="text-2xl">
                        🌱
                      </span>

                      {selected && (
                        <span className="rounded-full bg-emerald-600 px-2 py-1 text-[10px] font-bold text-white">
                          SELECTED
                        </span>
                      )}

                    </div>

                    <p className="mt-3 font-semibold">
                      {field.field_name}
                    </p>

                    <p className="mt-1 text-xs text-slate-500">
                      {formatCrop(field.crop_type)}
                    </p>

                    <p className="mt-1 text-xs text-slate-500">
                      Stage {field.growth_stage} •{" "}
                      {field.field_size} acres
                    </p>

                  </button>
                );
              })}

            </div>
          )}

        </section>

        {/* SELECTED FIELD */}

        {selectedField && (
          <section className="mb-5 rounded-2xl bg-gradient-to-br from-emerald-600 to-green-700 p-5 text-white shadow-sm">

            <p className="text-sm text-emerald-100">
              Selected Field
            </p>

            <h2 className="mt-1 text-2xl font-bold">
              {selectedField.field_name}
            </h2>

            <p className="mt-1 text-sm text-emerald-100">
              {formatCrop(
                selectedField.crop_type
              )}{" "}
              • Growth Stage{" "}
              {selectedField.growth_stage}
            </p>

          </section>
        )}

        {/* SUMMARY */}

        <section className="mb-5 grid grid-cols-2 gap-3 sm:grid-cols-3">

          <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">

            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
              Records
            </p>

            <p className="mt-2 text-2xl font-bold">
              {history.length}
            </p>

            <p className="mt-1 text-xs text-slate-500">
              Irrigation events
            </p>

          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">

            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
              Total Water
            </p>

            <p className="mt-2 text-2xl font-bold">
              {totalWaterUsed.toFixed(1)} L
            </p>

            <p className="mt-1 text-xs text-slate-500">
              Across all records
            </p>

          </div>

          <div className="col-span-2 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:col-span-1">

            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
              Average
            </p>

            <p className="mt-2 text-2xl font-bold">
              {averageWaterUsed.toFixed(1)} L
            </p>

            <p className="mt-1 text-xs text-slate-500">
              Per irrigation event
            </p>

          </div>

        </section>

        {/* EXPORT */}

        <section className="mb-5 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 shadow-sm">

          <div className="flex items-start gap-3">

            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-white text-xl shadow-sm">
              📊
            </div>

            <div className="flex-1">

              <h2 className="font-bold text-emerald-900">
                Export Irrigation Report
              </h2>

              <p className="mt-1 text-sm text-emerald-700">
                Download the selected field&apos;s irrigation
                records as CSV or PDF.
              </p>

              <button
                onClick={downloadCSV}
                disabled={!selectedField}
                className="mt-4 w-full rounded-xl bg-emerald-600 px-4 py-3 font-semibold text-white shadow-sm transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                📥 Download CSV Report
              </button>

              <button
                onClick={downloadPDF}
                disabled={!selectedField}
                className="mt-3 w-full rounded-xl bg-red-600 px-4 py-3 font-semibold text-white shadow-sm transition hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                📄 Download PDF Report
              </button>

            </div>

          </div>

        </section>

        {/* HISTORY */}

        <section>

          <div className="mb-3">

            <h2 className="text-lg font-bold">
              Previous Irrigation
            </h2>

            <p className="text-sm text-slate-500">
              Records retrieved from the irrigation database.
            </p>

          </div>

          {loadingHistory ? (

            <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">

              <div className="mx-auto mb-3 h-9 w-9 animate-spin rounded-full border-4 border-emerald-200 border-t-emerald-600" />

              <p className="text-sm text-slate-500">
                Loading irrigation history...
              </p>

            </div>

          ) : history.length === 0 ? (

            <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">

              <div className="text-4xl">
                💧
              </div>

              <h3 className="mt-3 font-bold">
                No irrigation records
              </h3>

              <p className="mt-1 text-sm text-slate-500">
                No previous irrigation records were found
                for this field.
              </p>

            </div>

          ) : (

            <div className="space-y-3">

              {history.map((record) => (

                <div
                  key={record.history_id}
                  className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm"
                >

                  <div className="flex items-start justify-between gap-3">

                    <div className="flex items-start gap-3">

                      <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-xl">
                        💧
                      </div>

                      <div>

                        <h3 className="font-bold">
                          {record.water_used_liters} L
                        </h3>

                        <p className="mt-1 text-sm text-slate-500">
                          {formatDateTime(
                            record.irrigation_timestamp
                          )}
                        </p>

                      </div>

                    </div>

                    <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold capitalize text-slate-600">
                      {record.source}
                    </span>

                  </div>

                  <div className="mt-4 grid grid-cols-2 gap-3">

                    <div className="rounded-xl bg-slate-50 p-3">

                      <p className="text-xs text-slate-500">
                        Crop
                      </p>

                      <p className="mt-1 text-sm font-semibold">
                        {formatCrop(
                          record.crop_type
                        )}
                      </p>

                    </div>

                    <div className="rounded-xl bg-slate-50 p-3">

                      <p className="text-xs text-slate-500">
                        Growth Stage
                      </p>

                      <p className="mt-1 text-sm font-semibold">
                        Stage{" "}
                        {record.growth_stage}
                      </p>

                    </div>

                  </div>

                  {record.notes && (
                    <div className="mt-3 rounded-xl bg-emerald-50 p-3">

                      <p className="text-xs font-semibold text-emerald-700">
                        Notes
                      </p>

                      <p className="mt-1 text-sm text-slate-700">
                        {record.notes}
                      </p>

                    </div>
                  )}

                </div>

              ))}

            </div>

          )}

        </section>

      </div>

      <BottomNav />

    </main>
  );
}