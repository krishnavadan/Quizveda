# Security Threat Model and Privacy

## Assets
Credentials/tokens, profiles, session state, answer keys, unpublished content, publisher credentials, provenance and audit history.

## Threats and controls
- Client tampering: server-authoritative timer, score and state machine.
- Answer leakage: protected answer payload; reveal only after accepted answer; no answer key in public CDN/logs.
- Replay/double submit: idempotency, unique constraints, transaction locking.
- Session takeover/IDOR: ownership checks, high-entropy guest token, short-lived signed tokens and rate limits.
- Admin abuse: RBAC, least privilege, MFA, separation of duties and audit.
- Malicious upload: quarantine, allow-listed type/size, malware scan, schema validation, no executable HTML.
- Supply-chain risk: dependency pinning/scanning, secret scanning, SBOM and signed images where practical.
- Exfiltration: TLS, managed encryption at rest, least privilege and redacted logs.

## Data classes
Public taxonomy and marketing; Internal editorial drafts/config; Confidential email/profile/session history; Restricted passwords, signing/encryption keys and tokens.

## Crypto
TLS 1.2+; managed at-rest encryption; Argon2id password hashing; secrets manager; key rotation and key-version metadata. Use vetted libraries and managed KMS; no custom cryptography.

## Privacy
Guest play; optional profile; minimization; personalization opt-out; export/delete; documented retention. Do not collect/infer sensitive traits or use MVP score for high-stakes decisions.

## Security release checks
SAST/dependency/secret scan; route auth tests; IDOR tests; replay/concurrency tests; answer-key leak scan across API/log/cache/frontend; upload fuzzing; rate-limit tests; backup restore; audit completeness; export/delete test.