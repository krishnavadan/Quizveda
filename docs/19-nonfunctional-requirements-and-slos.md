# Non-functional Requirements and SLOs

## Initial performance hypotheses
Catalog API p95 <300 ms; session create p95 <700 ms excluding cold start; answer submit p95 <400 ms; CDN static TTFB target <200 ms in primary regions; interactive LCP <2.5 s on agreed mid-range device/network; API error rate <1% excluding expected 4xx. Load-test and adjust before production commitment.

## Reliability
Initial availability objective 99.5% monthly for core API. Initial RPO 24h and RTO 8h maximum until business criticality review. Automated DB backups/PITR where supported; object versioning for published packs; restore exercise before launch.

## Scalability
Stateless API; PostgreSQL source of truth; pooling; CDN for immutable public assets; worker queue for imports/exports; Redis only for measured cache/rate-limit/ephemeral coordination. Bound worker concurrency.

## Accessibility
Target WCAG 2.2 AA on key journeys: keyboard, visible focus, semantic labels, screen-reader announcements, contrast, reduced motion, text resize and timer accommodations.

## Localization
BCP 47 locale tags such as en-IN, hi-IN, gu-IN. Keep strings separate from code; human-review translations; do not silently mix locales in one question.

## Observability
Measure request latency/errors, active sessions, answer conflicts/timeouts, question pool exhaustion, pack validation/publish duration, queue depth, DB saturation and CDN hit ratio. Logs carry request/correlation IDs and redact personal data.