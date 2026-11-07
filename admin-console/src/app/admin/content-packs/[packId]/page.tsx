"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { adminMutation, adminRequest, ContentPack } from "@/lib/admin-api";

type Question = {
  question_id: string;
  question_key: string;
  revision_no: number;
  locale: string;
  stem: string;
  explanation?: string | null;
  difficulty: string;
  estimated_seconds: number;
  approved: boolean;
  answer_key_option_key: string;
  options: { key: string; text: string; display_order: number }[];
};
type QuestionResponse = { items: Question[] };
type ApprovalResponse = ContentPack & { lifecycle_status: string };

export default function ContentPackDetailPage() {
  const { packId } = useParams<{ packId: string }>();
  const router = useRouter();
  const [pack, setPack] = useState<ContentPack | null>(null);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [reference, setReference] = useState("");
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [packResult, questionResult] = await Promise.all([
        adminRequest<ContentPack>(`/content-packs/${encodeURIComponent(packId)}`),
        adminRequest<QuestionResponse>(`/content-packs/${encodeURIComponent(packId)}/questions?limit=100&offset=0`),
      ]);
      setPack(packResult);
      setQuestions(questionResult.items ?? []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load pack details.");
    } finally {
      setLoading(false);
    }
  }, [packId]);

  useEffect(() => { void load(); }, [load]);

  async function transition(action: "approve" | "publish") {
    if (reference.trim().length < 3) {
      setError("Enter a release or approval reference (at least 3 characters).");
      return;
    }
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const updated = await adminMutation<ApprovalResponse>(
        `/content-packs/${encodeURIComponent(packId)}/${action}`,
        { approval_reference: reference.trim() },
      );
      setPack(updated);
      setReference("");
      setNotice(action === "approve" ? "Content pack approved and audit event recorded." : "Content pack published and audit event recorded.");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : `Unable to ${action} this pack.`);
    } finally {
      setBusy(false);
    }
  }

  if (loading) return <main className="content-wrap"><p className="muted">Loading content pack…</p></main>;
  if (error && !pack) return <main className="content-wrap"><div className="error-panel"><strong>Unable to open content pack</strong><p>{error}</p><button className="secondary-button" onClick={() => router.push("/admin")}>Back to inventory</button></div></main>;
  if (!pack) return null;

  const status = pack.lifecycle_status ?? "unknown";
  return (
    <main className="detail-wrap">
      <a className="back-link" href="/admin">← Back to content inventory</a>
      <header className="detail-header">
        <div><span className="eyebrow">CONTENT LIBRARY / PACK DETAIL</span><h1>{pack.title ?? pack.pack_key ?? pack.id}</h1><p className="muted">{pack.pack_key} · Version {pack.version} · {pack.locale}</p></div>
        <span className={`status status-${status}`}>{status}</span>
      </header>
      {error && <div className="error-panel" role="alert">{error}</div>}
      {notice && <div className="success-panel" role="status">{notice}</div>}
      <section className="detail-grid">
        <article className="detail-card"><span className="metric-label">Lifecycle state</span><strong>{status}</strong><small>Controlled release state from the backend</small></article>
        <article className="detail-card"><span className="metric-label">Question count</span><strong>{questions.length}</strong><small>Latest revision per question</small></article>
        <article className="detail-card"><span className="metric-label">Manifest SHA-256</span><strong className="hash-value">{pack.manifest_sha256 ?? "Not available"}</strong><small>Content integrity reference</small></article>
      </section>
      <section className="data-section question-section">
        <div className="section-heading"><div><span className="eyebrow">QUALITY REVIEW</span><h2>Question preview</h2><p className="muted">Review stems, options, answer keys and explanations before approving a pack.</p></div><span className="count-pill">{questions.length} questions</span></div>
        {questions.length === 0 ? <div className="empty-state">No questions are available in this pack.</div> : <div className="question-list">{questions.map((q, index) => <article className="question-card" key={q.question_id}><div className="question-meta"><span>QUESTION {String(index + 1).padStart(2, "0")}</span><span>{q.question_key}</span><span>{q.locale}</span><span>{q.difficulty}</span><span>{q.approved ? "Approved revision" : "Pending revision"}</span></div><h3>{q.stem}</h3><ol className="option-list" type="A">{q.options.sort((a,b)=>a.display_order-b.display_order).map(option => <li key={option.key}><span>{option.text}</span>{option.key === q.answer_key_option_key && <b>Correct answer</b>}</li>)}</ol>{q.explanation && <div className="explanation"><strong>Explanation</strong><p>{q.explanation}</p></div>}</article>)}</div>}
      </section>
      <section className="release-panel">
        <div><span className="eyebrow">CONTROLLED RELEASE</span><h2>Lifecycle action</h2><p>Every action is re-authorised by the API and written to the audit log. A separate reviewer and publisher are required.</p></div>
        <div className="release-controls"><label htmlFor="release-reference">Approval / release reference</label><input id="release-reference" value={reference} onChange={e=>setReference(e.target.value)} placeholder="e.g. CONTENT-REVIEW-2026-014" maxLength={160}/><div className="release-actions">{status === "validated" && <button className="primary-button" disabled={busy} onClick={()=>void transition("approve")}>{busy ? "Processing…" : "Approve pack"}</button>}{status === "approved" && <button className="primary-button" disabled={busy} onClick={()=>void transition("publish")}>{busy ? "Processing…" : "Publish pack"}</button>}{status === "published" && <span className="published-note">This version is published and immutable.</span>}</div></div>
      </section>
    </main>
  );
}
