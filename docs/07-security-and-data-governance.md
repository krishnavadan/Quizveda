# Security and Data Governance

## Identity
Use secure password hashing (Argon2id recommended) or a trusted identity provider. Short-lived access tokens, refresh-token rotation, MFA for privileged admins. Never store raw bearer tokens.

## Authorization
RBAC with least privilege. Enforce object ownership on every session/profile endpoint. Admin operations require explicit scopes and audit events. Separate author, reviewer and publisher duties.

## Data protection
TLS in transit; managed encryption at rest for DB, backups and object storage; secrets manager; key rotation; restricted service identities. Never commit secrets.

## Answer integrity
Server controls answer key, timer, score, active question and progression. Idempotency and unique constraints prevent replay/double scoring. Protected answer payloads never enter public CDN assets or logs.

## Privacy
Profile optional; guest play; data minimization; personalization opt-out; export/delete workflows; documented retention. Do not collect or infer sensitive personal attributes. Do not use MVP scores for high-stakes decisions.

## Audit
Log privileged content edits, answer-key changes, approvals, publication, rollback, role changes, user data access and deletion. Redact secrets and personal data.

## Incident readiness
Backups, tested restore, credential/key rotation, containment runbooks, severity ownership, evidence preservation and notification decision process.