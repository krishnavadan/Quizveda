# ADR-002: Content as Immutable Versioned JSON

**Status:** Accepted. Author and distribute content as immutable packs with manifest, schema version and checksums. Store bytes in object storage; metadata and publication pointers in PostgreSQL. Existing sessions pin versions. Rollback updates future publication pointer only. Protect answer keys behind API.