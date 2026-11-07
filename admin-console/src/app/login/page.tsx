"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { getUserManager } from "@/lib/oidc";

export default function LoginPage() {
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const router = useRouter();

  async function signIn() {
    setBusy(true);
    setError("");
    try {
      const user = await getUserManager().getUser();
      if (user && !user.expired) {
        router.replace("/admin");
        return;
      }
      await getUserManager().signinRedirect({ state: { returnTo: "/admin" } });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to start secure sign-in.");
      setBusy(false);
    }
  }

  return (
    <main className="auth-shell">
      <section className="auth-panel">
        <div className="brand-mark">Q</div>
        <p className="eyebrow">QUIZVEDA · CONTENT OPERATIONS</p>
        <h1>Admin console</h1>
        <p className="muted">Sign in with your organisation identity provider. Admin access is role-controlled and audited.</p>
        <button className="primary-button full-button" onClick={signIn} disabled={busy}>
          {busy ? "Connecting…" : "Continue with secure sign-in"}
        </button>
        {error && <p className="error-message" role="alert">{error}</p>}
        <p className="footnote">Access is restricted to authorised QuizVeda administrators.</p>
      </section>
    </main>
  );
}
