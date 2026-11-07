"use client";

import { getUserManager } from "@/lib/oidc";

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "");

export type ContentPack = {
  id: string;
  pack_key?: string;
  title?: string;
  version?: string;
  status?: string;
  locale?: string;
  [key: string]: unknown;
};

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
