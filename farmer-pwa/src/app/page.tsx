"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/login");
  }, [router]);

  return (
    <main className="flex min-h-screen items-center justify-center bg-emerald-950 text-white">
      <div className="text-center">
        <div className="mb-3 text-4xl">🌿</div>

        <p className="text-lg font-semibold">
          Smart Irrigation
        </p>

        <p className="mt-1 text-sm text-emerald-200">
          Opening farmer portal...
        </p>
      </div>
    </main>
  );
}