"use client";

import { UserManager, WebStorageStateStore } from "oidc-client-ts";

const required = (name: string, value: string | undefined): string => {
  if (!value) throw new Error(`Missing configuration: ${name}`);
  return value;
};

let manager: UserManager | undefined;

export function getUserManager(): UserManager {
  if (typeof window === "undefined") {
    throw new Error("OIDC is available only in the browser");
  }
  if (!manager) {
    const authority = required("NEXT_PUBLIC_OIDC_AUTHORITY", process.env.NEXT_PUBLIC_OIDC_AUTHORITY);
    const clientId = required("NEXT_PUBLIC_OIDC_CLIENT_ID", process.env.NEXT_PUBLIC_OIDC_CLIENT_ID);
    const redirectUri = required("NEXT_PUBLIC_OIDC_REDIRECT_URI", process.env.NEXT_PUBLIC_OIDC_REDIRECT_URI);
    manager = new UserManager({
      authority,
      client_id: clientId,
      redirect_uri: redirectUri,
      post_logout_redirect_uri: window.location.origin + "/login",
      response_type: "code",
      scope: process.env.NEXT_PUBLIC_OIDC_SCOPE || "openid profile email",
      userStore: new WebStorageStateStore({ store: window.sessionStorage }),
      stateStore: new WebStorageStateStore({ store: window.sessionStorage }),
      automaticSilentRenew: false,
      monitorSession: false,
      loadUserInfo: false,
    });
  }
  return manager;
}
