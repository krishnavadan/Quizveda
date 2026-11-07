# ADR-001: Modular Monolith

**Status:** Accepted. Start with a modular FastAPI monolith. Separate domains by package and interfaces; extract services only when scale, team autonomy or isolation justifies the complexity. PostgreSQL remains system of record.