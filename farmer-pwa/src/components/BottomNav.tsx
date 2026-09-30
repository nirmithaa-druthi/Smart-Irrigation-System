"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function BottomNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 border-t border-slate-200 bg-white px-2 py-2 shadow-lg">
      <div className="mx-auto grid max-w-md grid-cols-4">

        {/* HOME */}
        <Link
          href="/"
          className={`flex flex-col items-center gap-1 rounded-xl px-2 py-2 ${
            pathname === "/"
              ? "text-emerald-600"
              : "text-slate-500"
          }`}
        >
          <span className="text-xl">🏠</span>
          <span className="text-[10px] font-semibold">
            Home
          </span>
        </Link>

        {/* FIELDS */}
        <Link
          href="/fields"
          className={`flex flex-col items-center gap-1 rounded-xl px-2 py-2 ${
            pathname === "/fields"
              ? "text-emerald-600"
              : "text-slate-500"
          }`}
        >
          <span className="text-xl">🌱</span>
          <span className="text-[10px] font-semibold">
            Fields
          </span>
        </Link>

        {/* ALERTS */}
        <Link
          href="/alerts"
          className={`flex flex-col items-center gap-1 rounded-xl px-2 py-2 ${
            pathname === "/alerts"
              ? "text-emerald-600"
              : "text-slate-500"
          }`}
        >
          <span className="text-xl">🔔</span>
          <span className="text-[10px] font-semibold">
            Alerts
          </span>
        </Link>

        {/* PROFILE */}
        <Link
          href="/profile"
          className={`flex flex-col items-center gap-1 rounded-xl px-2 py-2 ${
            pathname === "/profile"
              ? "text-emerald-600"
              : "text-slate-500"
          }`}
        >
          <span className="text-xl">👤</span>
          <span className="text-[10px] font-semibold">
            Profile
          </span>
        </Link>

      </div>
    </nav>
  );
}