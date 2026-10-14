"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

type StoredAccount = {
  username: string;
  password: string;
};

const ACCOUNT_KEY = "farmer_account";
const LOGIN_KEY = "farmer_logged_in";
const PHONE_KEY = "farmer_phone";

export default function LoginPage() {
  const router = useRouter();

  const [mode, setMode] =
    useState<"login" | "create" | "forgot">("login");

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const clearMessages = () => {
    setMessage("");
    setError("");
  };

  // ============================================================
  // LOGIN
  // Any username + any non-empty password is accepted.
  // ============================================================

  const handleLogin = (event: FormEvent) => {
    event.preventDefault();
    clearMessages();

    const cleanUsername = username.trim();

    if (!cleanUsername || !password) {
      setError("Please enter your username and password.");
      return;
    }

    // Store the entered username locally.
    localStorage.setItem(PHONE_KEY, cleanUsername);

    // Mark the user as logged in.
    localStorage.setItem(LOGIN_KEY, "true");

    // Also save the account locally for demo purposes.
    localStorage.setItem(
      ACCOUNT_KEY,
      JSON.stringify({
        username: cleanUsername,
        password,
      })
    );

    // Go directly to dashboard.
    router.replace("/dashboard");
  };

  // ============================================================
  // CREATE ACCOUNT
  // ============================================================

  const handleCreateAccount = (event: FormEvent) => {
    event.preventDefault();
    clearMessages();

    const cleanUsername = username.trim();

    if (!cleanUsername || !password || !confirmPassword) {
      setError("Please fill in all the fields.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    const account: StoredAccount = {
      username: cleanUsername,
      password,
    };

    localStorage.setItem(
      ACCOUNT_KEY,
      JSON.stringify(account)
    );

    localStorage.setItem(LOGIN_KEY, "true");
    localStorage.setItem(PHONE_KEY, cleanUsername);

    router.replace("/dashboard");
  };

  // ============================================================
  // FORGOT PASSWORD
  // ============================================================

  const handleForgotPassword = (event: FormEvent) => {
    event.preventDefault();
    clearMessages();

    const stored = localStorage.getItem(ACCOUNT_KEY);

    if (!stored) {
      setError(
        "No account information is stored on this device."
      );
      return;
    }

    if (!username.trim()) {
      setError("Enter your username first.");
      return;
    }

    try {
      const account: StoredAccount = JSON.parse(stored);

      if (
        username.trim().toLowerCase() !==
        account.username.toLowerCase()
      ) {
        setError("No account was found with that username.");
        return;
      }

      setMessage(
        "For this demo, password recovery is handled locally. Please use the login screen to continue."
      );
    } catch {
      setError("Unable to read the saved account.");
    }
  };

  return (
    <main className="min-h-screen overflow-hidden bg-[#06140f] text-white">
      <div className="relative min-h-screen">

        {/* ======================================================
            BACKGROUND
        ====================================================== */}

        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_15%_20%,rgba(74,222,128,0.22),transparent_30%),radial-gradient(circle_at_85%_80%,rgba(45,212,191,0.18),transparent_32%),linear-gradient(135deg,#071a12_0%,#0b2a1d_48%,#06130f_100%)]" />

          <div className="absolute -left-24 top-20 h-80 w-80 rounded-full bg-emerald-400/10 blur-3xl" />

          <div className="absolute -right-20 bottom-10 h-96 w-96 rounded-full bg-teal-300/10 blur-3xl" />

          <svg
            className="absolute bottom-0 left-0 h-[46%] w-full opacity-30"
            viewBox="0 0 1440 420"
            preserveAspectRatio="none"
            aria-hidden="true"
          >
            <path
              d="M0 280 C180 220 290 270 430 235 C590 195 700 245 850 210 C1010 175 1150 220 1280 180 C1350 160 1400 165 1440 145 L1440 420 L0 420 Z"
              fill="currentColor"
              className="text-emerald-950"
            />

            <path
              d="M0 325 C160 275 300 310 450 275 C620 235 760 285 900 250 C1060 210 1190 260 1440 205 L1440 420 L0 420 Z"
              fill="currentColor"
              className="text-green-950"
            />

            <path
              d="M0 370 C220 330 340 365 530 330 C730 292 900 350 1080 310 C1240 275 1330 310 1440 280 L1440 420 L0 420 Z"
              fill="currentColor"
              className="text-black/50"
            />
          </svg>

          <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-black/50 to-transparent" />
        </div>

        {/* ======================================================
            MAIN CARD
        ====================================================== */}

        <div className="relative z-10 flex min-h-screen items-center justify-center px-5 py-10">
          <section className="grid w-full max-w-5xl overflow-hidden rounded-[32px] border border-white/10 bg-white/[0.07] shadow-2xl shadow-black/40 backdrop-blur-2xl lg:grid-cols-[1.05fr_0.95fr]">

            {/* ==================================================
                BRAND PANEL
            ================================================== */}

            <div className="hidden min-h-[650px] flex-col justify-between p-10 lg:flex">
              <div>

                <div className="mb-8 flex items-center gap-3">
                  <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-400 text-2xl text-[#052e1b] shadow-lg shadow-emerald-900/30">
                    🌱
                  </div>

                  <div>
                    <p className="text-lg font-bold tracking-tight">
                      Smart Irrigation
                    </p>

                    <p className="text-xs uppercase tracking-[0.22em] text-emerald-200/60">
                      Farmer Command Center
                    </p>
                  </div>
                </div>

                <div className="max-w-md">
                  <p className="mb-4 inline-flex rounded-full border border-emerald-300/20 bg-emerald-300/10 px-3 py-1 text-xs font-medium text-emerald-200">
                    AI-powered farm intelligence
                  </p>

                  <h1 className="text-5xl font-semibold leading-[1.08] tracking-tight">
                    Smarter water.
                    <br />
                    <span className="text-emerald-300">
                      Healthier crops.
                    </span>
                  </h1>

                  <p className="mt-6 max-w-sm text-sm leading-7 text-white/60">
                    Monitor field conditions, understand weather
                    patterns and receive irrigation recommendations
                    from one simple farmer dashboard.
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                {[
                  ["AI", "Irrigation"],
                  ["LIVE", "Conditions"],
                  ["PWA", "Mobile ready"],
                ].map(([value, label]) => (
                  <div
                    key={value}
                    className="rounded-2xl border border-white/10 bg-black/10 p-4"
                  >
                    <p className="text-sm font-bold text-emerald-300">
                      {value}
                    </p>

                    <p className="mt-1 text-xs text-white/50">
                      {label}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* ==================================================
                AUTH PANEL
            ================================================== */}

            <div className="flex min-h-[650px] items-center bg-[#f6fbf7] p-6 text-slate-900 sm:p-10">
              <div className="mx-auto w-full max-w-md">

                {/* Mobile brand */}
                <div className="mb-8 lg:hidden">
                  <div className="mb-5 flex items-center gap-3">
                    <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-emerald-600 text-xl">
                      🌱
                    </div>

                    <div>
                      <p className="font-bold">
                        Smart Irrigation
                      </p>

                      <p className="text-[10px] uppercase tracking-widest text-slate-400">
                        Farmer Command Center
                      </p>
                    </div>
                  </div>
                </div>

                {/* Heading */}
                <div className="mb-8">
                  <p className="mb-2 text-sm font-semibold text-emerald-700">
                    Welcome back
                  </p>

                  <h2 className="text-3xl font-bold tracking-tight">
                    {mode === "login"
                      ? "Sign in to your farm"
                      : mode === "create"
                      ? "Create your account"
                      : "Reset your password"}
                  </h2>

                  <p className="mt-2 text-sm text-slate-500">
                    {mode === "login"
                      ? "Access your fields and irrigation insights."
                      : mode === "create"
                      ? "Set up your farmer account on this device."
                      : "Enter your username to begin recovery."}
                  </p>
                </div>

                {/* ==================================================
                    FORM
                ================================================== */}

                <form
                  onSubmit={
                    mode === "login"
                      ? handleLogin
                      : mode === "create"
                      ? handleCreateAccount
                      : handleForgotPassword
                  }
                  className="space-y-5"
                >

                  {/* Username */}
                  <div>
                    <label className="mb-2 block text-sm font-semibold text-slate-700">
                      Username
                    </label>

                    <input
                      value={username}
                      onChange={(e) =>
                        setUsername(e.target.value)
                      }
                      placeholder="Enter your username"
                      autoComplete="username"
                      className="h-12 w-full rounded-xl border border-slate-200 bg-white px-4 text-sm outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10"
                    />
                  </div>

                  {/* Password */}
                  {mode !== "forgot" && (
                    <div>
                      <div className="mb-2 flex items-center justify-between">
                        <label className="text-sm font-semibold text-slate-700">
                          Password
                        </label>

                        {mode === "login" && (
                          <button
                            type="button"
                            onClick={() => {
                              clearMessages();
                              setMode("forgot");
                            }}
                            className="text-xs font-semibold text-emerald-700 hover:text-emerald-900"
                          >
                            Forgot password?
                          </button>
                        )}
                      </div>

                      <input
                        type="password"
                        value={password}
                        onChange={(e) =>
                          setPassword(e.target.value)
                        }
                        placeholder="Enter your password"
                        autoComplete={
                          mode === "create"
                            ? "new-password"
                            : "current-password"
                        }
                        className="h-12 w-full rounded-xl border border-slate-200 bg-white px-4 text-sm outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10"
                      />
                    </div>
                  )}

                  {/* Confirm password */}
                  {mode === "create" && (
                    <div>
                      <label className="mb-2 block text-sm font-semibold text-slate-700">
                        Confirm password
                      </label>

                      <input
                        type="password"
                        value={confirmPassword}
                        onChange={(e) =>
                          setConfirmPassword(e.target.value)
                        }
                        placeholder="Re-enter your password"
                        autoComplete="new-password"
                        className="h-12 w-full rounded-xl border border-slate-200 bg-white px-4 text-sm outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10"
                      />
                    </div>
                  )}

                  {/* Error */}
                  {error && (
                    <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                      {error}
                    </div>
                  )}

                  {/* Message */}
                  {message && (
                    <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
                      {message}
                    </div>
                  )}

                  {/* Submit */}
                  <button
                    type="submit"
                    className="h-12 w-full rounded-xl bg-emerald-600 font-semibold text-white shadow-lg shadow-emerald-600/20 transition hover:bg-emerald-700 active:scale-[0.99]"
                  >
                    {mode === "login"
                      ? "Sign in"
                      : mode === "create"
                      ? "Create account"
                      : "Recover account"}
                  </button>
                </form>

                {/* ==================================================
                    MODE SWITCH
                ================================================== */}

                <div className="mt-7 text-center text-sm text-slate-500">
                  {mode === "login" ? (
                    <>
                      Don't have an account?{" "}
                      <button
                        type="button"
                        onClick={() => {
                          clearMessages();
                          setMode("create");
                          setPassword("");
                        }}
                        className="font-semibold text-emerald-700 hover:text-emerald-900"
                      >
                        Create new account
                      </button>
                    </>
                  ) : (
                    <button
                      type="button"
                      onClick={() => {
                        clearMessages();
                        setMode("login");
                        setPassword("");
                        setConfirmPassword("");
                      }}
                      className="font-semibold text-emerald-700 hover:text-emerald-900"
                    >
                      ← Back to login
                    </button>
                  )}
                </div>

                <p className="mt-8 text-center text-[11px] leading-5 text-slate-400">
                  Demo authentication is stored locally in the
                  browser. Any non-empty username and password can
                  be used to access the farmer dashboard.
                </p>
              </div>
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}