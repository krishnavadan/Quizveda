# Admin CMS Foundation: Authentication, Roles and Content Governance

**Status:** implementation slice; requires identity-provider configuration and human review before production use.

## Security architecture

The Admin API verifies signed OIDC access tokens using the provider's JWKS endpoint. Configuration is provider-neutral and supplied only through deployment environment variables:

| Variable | Purpose |
|---|---|
| `OIDC_ISSUER` | Exact expected token issuer |
| `OIDC_AUDIENCE` | API audience expected in the access token |
| `OIDC_JWKS_URL` | Trusted provider JWKS endpoint |
| `OIDC_ROLES_CLAIM` | Claim containing role strings; defaults to `roles` |

The verifier accepts RS256 only, checks signature, issuer, audience, expiry, issued-at and subject, and allows a 30-second clock skew. JWKS responses are cached for five minutes. Admin routes fail closed with HTTP 503 when identity-provider configuration is incomplete. Missing credentials return 401; invalid signatures/claims return 401; insufficient roles return 403.

The IdP must issue access tokens intended for this API and map users into the roles below. Do not accept ID tokens as API bearer tokens. Configure HTTPS, exact issuer/audience values, short access-token lifetimes, MFA for privileged roles, and provider-side role assignment governance. Secrets and signing keys remain with the identity provider; QuizVeda stores no password.

## Role model

| Role | Read pack/question content | Approve | Publish | Read audit |
|---|---:|---:|---:|---:|
| `content_editor` | Yes | No | No | No |
| `content_reviewer` | Yes | Yes | No | No |
| `content_publisher` | Yes | No | Yes | No |
| `admin` | Yes | Yes | Yes | Yes |

An administrator role is an explicit privileged override. The reviewer and publisher should be different subjects: a non-admin publisher cannot publish a pack they approved. The IdP should avoid assigning broad admin privileges as a convenience.

## Content lifecycle

`validated` → `approved` → `published`

1. Offline import validates schemas, provenance fields, hashes and question structure, then creates a `validated` draft. It cannot approve or publish.
2. A reviewer reviews the pack and approves it with a required reference. The API records the token subject and timestamp and marks the included question revisions approved in the same database transaction.
3. A separate publisher publishes the approved pack with a release reference. The API records publication time and an audit event in the same transaction.
4. Gameplay serves only approved revisions in published pack versions.

No API in this slice edits published content. Published versions are immutable; corrections should be imported as a new pack version and pass the complete workflow. Rollback/withdrawal controls are a later release gate and should not be implemented as destructive mutation of historical content.

## Implemented endpoints

All paths are under `/api/v1`.

| Method | Path | Role |
|---|---|---|
| GET | `/admin/content-packs` | editor, reviewer, publisher, admin |
| GET | `/admin/content-packs/{pack_id}` | editor, reviewer, publisher, admin |
| GET | `/admin/content-packs/{pack_id}/questions` | editor, reviewer, publisher, admin |
| POST | `/admin/content-packs/{pack_id}/approve` | reviewer, admin |
| POST | `/admin/content-packs/{pack_id}/publish` | publisher, admin |
| GET | `/admin/audit-events` | admin |

Approval and publish request body:

```json
{
  "approval_reference": "REVIEW-2026-001"
}
```

The reference is an operator-supplied audit identifier, not a substitute for authentication or authorization.

## Audit events

Approval and publication create append-only application audit records in the same transaction as the lifecycle change. Each record captures actor subject, action, resource type/id, reference, metadata and timestamp. The API provides read-only audit access to the admin role. Database administrators remain a trusted infrastructure boundary; production database permissions and backup retention must protect the audit table.

## Operational requirements before production

- Configure and test the real OIDC provider, issuer, audience, JWKS rotation and role claims.
- Require MFA for reviewer, publisher and admin identities.
- Restrict admin API ingress and apply rate limits, request-size limits and security headers at the gateway.
- Alert on repeated 401/403 responses, approval/publish actions and role changes at the IdP.
- Protect audit records with database access controls, backups and retention policy.
- Complete security review, end-to-end tests and operational runbooks.
- Add a frontend admin console only after API authorization and identity configuration are accepted.

## Explicit exclusions

This slice does not include password storage, local admin accounts, user invitations, question editing, bulk import over HTTP, media upload, rollback/withdrawal UI, or learner-facing AI. Internal AI development tools cannot call privileged production admin actions or approve their own content.
