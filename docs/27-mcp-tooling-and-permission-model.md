# 27. MCP Tooling Architecture and Permission Model

## Objective
Use MCP servers as a standard boundary for approved agent tools and resources. MCP is not authorization by itself; the gateway enforces identity, scopes, validation, quotas and audit.

## Logical servers
| Server | Example capabilities | Default access |
|---|---|---|
| quizveda-knowledge | search approved sources, fetch citation, traverse graph | read-only |
| quizveda-content | validate pack, preview draft, compare revisions | draft-scoped |
| quizveda-taxonomy | lookup taxonomy, propose mapping | read/propose |
| quizveda-quality | schema, duplicate, answer and safety checks | execute checks |
| quizveda-analytics | privacy-safe aggregate metrics | aggregate read-only |
| quizveda-dev | inspect repo, run tests, create branch/PR | developer role |
| quizveda-admin | approve, publish and rollback | publisher + confirmation |

## Tool contract
Each tool defines stable name, description, JSON schemas, scope, data classification, idempotency, timeout, rate limit, audit event, error taxonomy and confirmation requirement. Prefer narrow verbs such as search_approved_knowledge, validate_content_pack and preview_publication. Prohibit generic execute_sql, unrestricted shell, arbitrary URL fetch and broad write tools.

## Security
Authenticate clients with workload identity or short-lived scoped credentials. Authorize each call server-side. Enforce tenant/resource scopes. Bound and validate inputs/outputs. Redact secrets and personal data. Apply egress allowlists and SSRF protections. Treat tool output as untrusted data, not instructions. Require human confirmation for publish, rollback, destructive changes, external communication and sensitive exports. Keep immutable audit records.

## Resources, reliability and MVP
Expose versioned read-only resources for approved taxonomy, schemas, published packs, policies and agent/skill manifests. Do not expose raw learner records broadly. Set timeouts, bounded retries, circuit breakers, concurrency caps and response-size limits. Cache immutable resources by content hash. Never retry non-idempotent writes without idempotency keys.

Start with one internal knowledge/content MCP server and read-only/validation tools. Add publication tools only after RBAC, audit, confirmation and rollback tests. MCP is not required for learner gameplay.
