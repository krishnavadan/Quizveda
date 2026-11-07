"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ContentPack, adminRequest, contentPackTitle } from "@/lib/admin-api";
import { getUserManager } from "@/lib/oidc";

type PackResponse = { items?: ContentPack[]; content_packs?: ContentPack[] } | ContentPack[];

export default function AdminDashboardPage() {
  const router = useRouter();
  const [packs, setPacks] = useState<ContentPack[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [identity, setIdentity] = useState("Authorised administrator");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const user = await getUserManager().getUser();
      if (!user || user.expired) {
        router.replace("/login");
        return;
      }
      setIdentity(typeof user.profile.name === "string" ? user.profile.name : typeof user.profile.email === "string" ? user.profile.email : "Authorised administrator");
      const result = await adminRequest<PackResponse>("/content-packs");
      setPacks(Array.isArray(result) ? result : result.items ?? result.content_packs ?? []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load content packs.");
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => { void load(); }, [load]);

  async function signOut() {
    await getUserManager().signoutRedirect();
  }

  return (
    <main className="console-shell">
      <aside className="sidebar">
        <a className="sidebar-brand" href="/admin"><span className="brand-mark small">Q</span><span>QuizVeda<small>ADMIN CONSOLE</small></span></a>
        <nav aria-label="Admin navigation">
          <a className="nav-item active" href="/admin"><span>▦</span> Overview</a>
          <a className="nav-item" href="#content-packs"><span>▤</span> Content packs</a>
          <a className="nav-item" href="#governance"><span>◇</span> Governance</a>\n          <a className="nav-item" href="/admin/audit"><span>≡</span> Audit history</a>
        </nav>
        <div className="sidebar-note"><strong>Content integrity</strong><p>Every release is validated, reviewed, approved and published through controlled roles.</p></div>
      </aside>
      <section className="main-area">
        <header className="topbar"><div><span className="eyebrow">WORKSPACE / OVERVIEW</span><h1>Content operations</h1></div><div className="account"><span className="avatar">{identity.slice(0, 1).toUpperCase()}</span><span className="account-name">{identity}</span><button className="quiet-button" onClick={signOut}>Sign out</button></div></header>
        <div className="content-wrap">
          <section className="welcome-row"><div><h2>Good to see you.</h2><p className="muted">Manage the question library and its controlled release lifecycle.</p></div><button className="secondary-button" onClick={() => void load()} disabled={loading}>Refresh data</button></section>
          <section className="metric-grid" aria-label="Content summary">
            <article className="metric-card"><span className="metric-label">Total content packs</span><strong>{loading ? "—" : packs.length}</strong><span className="metric-foot">Visible to your role</span></article>
            <article className="metric-card"><span className="metric-label">Release workflow</span><strong>3 stages</strong><span className="metric-foot">Validated → Approved → Published</span></article>
            <article className="metric-card"><span className="metric-label">Access model</span><strong>OIDC + RBAC</strong><span className="metric-foot">Backend-enforced permissions</span></article>
          </section>
          <section className="data-section" id="content-packs">
            <div className="section-heading"><div><span className="eyebrow">LIBRARY</span><h2>Content packs</h2><p className="muted">Published and draft pack inventory available to your account.</p></div><span className="count-pill">{packs.length} packs</span></div>
            {loading ? <div className="empty-state">Loading content inventory…</div> : error ? <div className="error-panel" role="alert"><strong>Could not load inventory</strong><p>{error}</p><button className="secondary-button" onClick={() => void load()}>Try again</button></div> : packs.length === 0 ? <div className="empty-state">No content packs are currently visible. Import and validate a content pack using the approved offline workflow.</div> : <div className="table-wrap"><table><thead><tr><th>Pack</th><th>Version</th><th>Locale</th><th>Status</th></tr></thead><tbody>{packs.map((pack, index) => <tr key={pack.id ?? index}><td><a className="pack-link" href={`/admin/content-packs/${encodeURIComponent(pack.id)}`}><strong>{contentPackTitle(pack)}</strong><small>{pack.pack_key ?? pack.id} · Review details →</small></a></td><td>{pack.version ?? "—"}</td><td>{pack.locale ?? "—"}</td><td><span className={`status status-${(pack.lifecycle_status ?? "unknown").toLowerCase()}`}>{pack.lifecycle_status ?? "Unknown"}</span></td></tr>)}</tbody></table></div>}
          </section>
          <section className="governance-panel" id="governance"><div><span className="eyebrow">RELEASE GOVERNANCE</span><h2>Trust is built into the workflow.</h2><p>Content moves through separate validation, approval and publication steps. Reviewer and publisher separation is enforced by the API, with audit events recorded for lifecycle transitions.</p></div><div className="workflow"><span>01 <b>Validated</b></span><i>→</i><span>02 <b>Approved</b></span><i>→</i><span>03 <b>Published</b></span></div></section>
          <footer className="console-footer">QuizVeda Admin · Internal content operations · No learner-facing AI services</footer>
        </div>
      </section>
    </main>
  );
}
