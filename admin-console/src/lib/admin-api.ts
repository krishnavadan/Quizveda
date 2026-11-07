"use client";

import { getUserManager } from "@/lib/oidc";

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "");

export type ContentPack = {
  id: string;
  pack_key?: string;
  title?: Record<string, string> | string;
  version?: string;
  lifecycle_status?: string;
  locale?: string;
  manifest_sha256?: string | null;
  [key: string]: unknown;
};

export function contentPackTitle(pack: ContentPack): string {
  if (typeof pack.title === "string") return pack.title;
  if (pack.title && typeof pack.title === "object") {
    const localized = pack.title[pack.locale ?? ""] ?? Object.values(pack.title)[0];
    if (localized) return localized;
  }
  return pack.pack_key ?? pack.id;
}

export async function adminRequest<T>(path: string): Promise<T> {
  if (!apiBase) throw new Error("Missing configuration: NEXT_PUBLIC_API_BASE_URL");
  const user = await getUserManager().getUser();
  if (!user || user.expired) throw new Error("Your admin session has expired. Please sign in again.");
  const response = await fetch(`${apiBase}/api/v1/admin${path}`, {
    headers: { Authorization: `Bearer ${user.access_token}`, Accept: "application/json" },
    cache: "no-store",
  });
  if (response.status === 401) throw new Error("Authentication failed. Sign in again.");
  if (response.status === 403) throw new Error("Your account does not have permission for this action.");
  if (!response.ok) throw new Error(`Admin API returned HTTP ${response.status}`);
  return response.json() as Promise<T>;
}

export async function adminMutation<T>(path: string, payload: Record<string, unknown>): Promise<T> {
  if (!apiBase) throw new Error("Missing configuration: NEXT_PUBLIC_API_BASE_URL");
  const user = await getUserManager().getUser();
  if (!user || user.expired) throw new Error("Your admin session has expired. Please sign in again.");
  const response = await fetch(`${apiBase}/api/v1/admin${path}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${user.access_token}`,
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
    cache: "no-store",
  });
  if (response.status === 401) throw new Error("Authentication failed. Sign in again.");
  if (response.status === 403) throw new Error("Your account does not have permission for this action, or the separation-of-duties policy was not met.");
  if (response.status === 409) {
    const body = await response.json().catch(() => ({})) as { detail?: string };
    throw new Error(body.detail ?? "The content lifecycle state changed. Refresh and try again.");
  }
  if (!response.ok) {
    const body = await response.json().catch(() => ({})) as { detail?: string };
    throw new Error(body.detail ?? `Admin API returned HTTP ${response.status}`);
  }
  return response.json() as Promise<T>;
}
