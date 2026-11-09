"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getUserManager } from "@/lib/oidc";

export default function AuthCallbackPage() {
  const router = useRouter();
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    getUserManager().signinRedirectCallback()
      .then((user) => {
        if (!active) return;
        const state = user.state as { returnTo?: string } | undefined;
        const target = state?.returnTo;
        router.replace(target?.startsWith("/") && !target.startsWith("//") ? target : "/admin");
      })
      .catch((err: unknown) => {
        if (active) setError(err instanceof Error ? err.message : "Sign-in callback failed.");
      });
    return () => { active = false; };
  }, [router]);

  return (
    <main className="auth-shell">
      <section className="auth-panel">
        <div className="brand-mark">Q</div>
        <p className="eyebrow">SECURE AUTHENTICATION</p>
        <h1>{error ? "Sign-in could not be completed" : "Verifying your session…"}</h1>
        {error ? <><p className="error-message" role="alert">{error}</p><a className="text-link" href="/login">Return to sign in</a></> : <p className="muted">Please wait while your identity is verified.</p>}
      </section>
    </main>
  );
}
