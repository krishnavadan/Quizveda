# ADR-005: Immutable content packs with CDN delivery

- **Status:** Accepted for MVP
- **Date:** 2026-11-08

## Context

Question content changes more frequently than application code. Large catalogs should not require application redeployments or repeated database reads for every browse request.

## Decision

Store authored content as immutable, versioned packs. Validate and publish a pack through an administrative workflow. Deliver public, non-sensitive browse metadata and approved question payloads from object storage behind a CDN where practical. Keep answer keys and other protected gameplay data behind authenticated backend APIs.

## Rules

- Every pack has a stable pack ID and immutable version.
- A manifest declares locale, taxonomy scope, schema version, item counts, checksums and provenance.
- A publication pointer identifies the active version; publication is atomic.
- A live session pins its content version and never silently changes midway through play.
- Rollback changes the active publication pointer; it does not mutate historical pack bytes.
- Compression is transport-level (Brotli or gzip where supported); avoid custom compression until measurements justify it.
- Encrypt storage and transport using managed platform capabilities. Do not invent application-level encryption for public content.
- Never place answer keys in publicly cacheable assets.

## Consequences

- Content publishing can proceed independently of app deployment.
- Historical sessions remain reproducible.
- CDN caching improves throughput and reduces database load.
- The publishing pipeline must enforce schema compatibility and provenance.