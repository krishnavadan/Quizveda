# Technical Architecture

## Proposed stack
Frontend: React/Next.js PWA. Backend: FastAPI modular monolith. Database: PostgreSQL. Redis: optional cache/rate-limit/ephemeral coordination. Worker: background validation, exports and analytics. Storage: object storage for immutable content packs; CDN for approved public metadata/assets.

## Modules
Identity & Access; Profile; Taxonomy/Catalog; Content Management; Content Delivery; Question Selection; Game Session; Scoring; Lifelines; Progress; Notifications; Analytics; Admin/Audit.

## Boundaries
Keep gameplay and content management as domain modules in one deployable backend initially. Extract services only when scale, team ownership or isolation justifies the operational cost. PostgreSQL is source of truth. Redis is not durable session state.

## Gameplay
Server-authoritative state machine. Pin pack and policy versions at session creation. Deliver one question at a time. Use idempotent transactional answer submissions. Do not expose answer keys or future questions.

## Content delivery
Immutable versioned packs; manifest checksums; public catalog separated from protected answer data. Compress with Brotli/gzip at transport/CDN layer. Use managed encryption at rest and TLS. Avoid custom encryption/compression.

## Scalability
Stateless API instances; DB connection pooling; CDN caching; bounded worker concurrency; partition high-volume events only when needed; measure before adding infrastructure.

## AI
AI may assist drafting, translation or metadata suggestions behind human review. It is not required for question selection, gameplay, scoring or session progression.