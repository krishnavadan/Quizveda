# Deployment, DevOps and Environments

## Environments
Local Docker Compose with synthetic data; development integration; staging production-like; production restricted and monitored. Never use production personal data in dev.

## Topology
Browser/PWA → CDN/WAF → ingress/Nginx → FastAPI → PostgreSQL. Worker/scheduler consumes queue. Object storage holds immutable packs/private uploads. Redis optional; not source of truth.

## CI
Lint/typecheck → unit tests → secret/dependency scans → immutable image build → SBOM/image scan → integration tests → staging deploy → smoke/contract tests → production approval.

## Release
Backward-compatible migrations; deploy additive schema before relying on it; feature flags for risky behavior; rolling/canary where supported; health checks; independent application/content rollback.

## Operations
Environment config validated at startup; separate least-privilege credentials; secrets manager; runbooks for API outage, DB saturation, queue backlog, failed publish, stale CDN, answer-key exposure, account compromise, restore and rollback.