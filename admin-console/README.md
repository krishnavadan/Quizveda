# QuizVeda Admin Console

Next.js admin interface for the QuizVeda content operations API.

## Included in this increment

- Responsive admin workspace and content-pack inventory.
- OIDC Authorization Code flow with PKCE through `oidc-client-ts`.
- Browser session storage for OIDC state and user session (not local storage).
- Bearer-token API calls to the backend admin endpoints.
- Explicit loading, empty, unauthorised and error states.
- No client-side approval or publishing shortcuts; lifecycle actions remain server-side and will be added as separately permission-gated workflows.

## Configuration

Copy `.env.example` to `.env.local` and configure the public OIDC authority, client ID, exact callback URI, scope and API base URL. Register the callback URI and post-logout URI with the identity provider. Configure a public browser client with Authorization Code + PKCE and no client secret.

The backend must independently validate the access token's RS256 signature, issuer, audience, expiry and roles using its trusted JWKS configuration. Configure the backend role claim to match the identity provider. The browser UI is not an authorization boundary.

## Run locally

```bash
npm install
npm run dev
```

Open `http://localhost:3000/login`.

## Security notes

- Never add an OIDC client secret to `NEXT_PUBLIC_*` variables or browser code.
- Use HTTPS outside localhost; use a restrictive Content Security Policy and allowlist the identity provider/API origins.
- Keep tokens in session storage and avoid logging tokens or claims.
- Configure the backend CORS allowlist for the exact console origin.
- The backend remains authoritative for all permissions and audit events.
- No learner data, gameplay routes or runtime AI services are part of this console.

## Content review and release workflows

- Select a content pack from the dashboard to inspect its metadata and latest question revisions.
- Question preview includes options, answer key and authored explanation for authorised content reviewers.
- The approval form submits a mandatory approval reference to the backend.
- Publishing submits a release reference; the API enforces reviewer/publisher separation and returns conflict/permission errors for invalid transitions.
- Audit history calls the admin-only endpoint. A user without the administrator role receives a backend 403; hiding a link is never treated as access control.

The UI intentionally does not edit question text or mutate published content. Content import and authoring remain in the validated offline content-pack workflow.
