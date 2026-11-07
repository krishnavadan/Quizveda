# Glossary and Product Decision Register

## Glossary
Pack: independently versioned content unit. Pack version: immutable snapshot. Question revision: immutable reviewed item. Perspective: lens framing a question. Cognitive objective: intended learning action. Session: server-authoritative game. Lifeline: limited assistance mechanic. Mastery: approximate progress indicator, not validated psychometric score.

## Baseline decisions
Broad audience; optional profile; guest play; Play to Win and Play to Learn; Classic Ladder/Practice/Quick Quiz/Topic Challenge; multi-perspective questions; versioned JSON content; hybrid optional AI; React/Next.js PWA + FastAPI modular monolith + PostgreSQL; Redis only when justified; object storage/CDN for immutable public content; protected answer payloads via API.

## Open decisions before implementation freeze
1. Trademark/domain clearance.
2. Authentication provider and social login scope.
3. Exact scoring curve and timer bonus.
4. Lifeline behavior and limits.
5. Launch locales and editorial capacity.
6. Initial subject catalog and content rights.
7. Hosting, regions, cost envelope and backup strategy.
8. Leaderboard scope and moderation.
9. Monetization/entitlements.
10. Browser/device support matrix.

Resolve in ADR/configuration; do not invent policy silently in code.