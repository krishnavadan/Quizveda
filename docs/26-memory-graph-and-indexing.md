# 26. Governed Memory Graph and Retrieval Index

## Purpose and boundaries
Create a traceable knowledge layer for approved facts, concepts, questions, explanations, objectives, references, content packs and product decisions. This is a retrieval aid, not an answer-evaluation authority or hidden learner dossier.

## Memory classes
1. Knowledge: verified concepts, claims, relationships and references.
2. Content: question revisions, explanations, objectives, perspectives, locale variants and reviews.
3. Product: approved requirements, ADRs, policies and dependencies.
4. Operations: agent/skill versions, validation, publication and incident learnings.
5. Learner preferences: only explicit, purpose-limited preferences and opted-in progress, logically separated from global knowledge.

Never store hidden reasoning traces, credentials, raw session secrets, unnecessary personal data or unverified generated claims as durable memory.

## Graph schema
Node types: Concept, FactClaim, Source, Topic, QuestionRevision, Explanation, LearningObjective, Perspective, Locale, ContentPackVersion, Policy, ADR, Agent, Skill, Evaluation, LearnerPreference.

Edge types: ABOUT_TOPIC, SUPPORTED_BY, CONTRADICTS, DERIVED_FROM, HAS_OBJECTIVE, USES_PERSPECTIVE, TRANSLATION_OF, SUPERSEDES, VALIDATED_BY, GENERATED_BY, USES_SKILL_VERSION, PUBLISHED_IN, REQUIRES, PREFERS_TOPIC.

Edges carry provenance, confidence/verification state, timestamps, validity interval and creator identity.

## Index architecture
Use PostgreSQL as canonical store for entities, permissions, provenance and versioning; full-text search for exact phrases; vector index for semantic candidates; bounded graph traversal for relationships and contradictions. Rerank only after permission and publication filters. Start with relational node/edge tables; add a graph database only when measured needs justify it. Embeddings are derived indexes and must be rebuildable.

## Retrieval sequence
Classify task -> apply tenant/role/locale/age/publication filters -> exact and semantic search -> one or two bounded graph hops -> rank by relevance, authority, freshness and review status -> return compact evidence cards with source ID, claim, version and citation locator. If evidence conflicts or is absent, state uncertainty and request review.

## Index lifecycle
Validate immutable revision -> update canonical graph transactionally -> refresh embedding/search index -> verify parity -> mark index version current. Rollback restores prior approved revision and invalidates cache. Track freshness and failures.

## Learner memory controls
Explicit, editable, exportable and deletable preferences only. Minimal summaries include chosen language, topics and difficulty range. Never infer age, health, disability, religion, ethnicity or income. Guest mode creates no persistent learner memory.
