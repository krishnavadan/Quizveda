# Content Editorial Quality Checks

**Status:** advisory implementation; not an approval gate.

## Purpose

Give content editors and reviewers a repeatable first-pass signal for issues that are easy to overlook in a large question pack. The report is deterministic, read-only and derived from the latest revision of each question in a pack.

## Implemented checks

| Check | Signal | Interpretation |
|---|---|---|
| Short stem | Stem has fewer than 20 trimmed characters | Verify the question has enough context |
| Short explanation | Explanation has fewer than 30 trimmed characters | Consider adding learner-facing reasoning |
| Duplicate options | Two options have identical normalized text | Review whether the options are distinguishable |
| Fewer than three options | Less than three options exist | Confirm this is intentional |
| Duplicate stems | Normalized stems match across questions | Review possible duplicate content |

Normalization uses Unicode-aware case folding and non-word character collapsing. It is intentionally conservative and does not attempt semantic similarity, factual verification, answer correctness, bias detection or legal-rights verification.

## API

`GET /api/v1/admin/content-packs/{pack_id}/quality-report`

Requires one of the same content-reading roles as pack preview: `content_editor`, `content_reviewer`, `content_publisher`, or `admin`.

The response includes pack identity, number of latest question revisions checked, advisory count, duplicate stem groups, findings and an explicit disclaimer. Each finding identifies the question key, stable check code, severity (`advisory`) and human-readable explanation.

## Safety and governance

- The endpoint is read-only and does not alter content or lifecycle state.
- Advisories never approve, reject or publish a question or pack.
- No LLM or external AI service is called at runtime.
- A clean report is not proof that content is correct, original, unbiased, accessible or rights-cleared.
- Reviewers must still check subject-matter accuracy, answer-key integrity, provenance, rights, age suitability, language quality and accessibility.
- Existing JSON Schema validation remains the structural import gate; these checks complement rather than replace it.

## Known limitations and next steps

- The first version uses simple heuristics and can produce false positives and false negatives.
- It evaluates only the latest revision of each question.
- The admin preview endpoint currently paginates question data; the quality report checks all latest revisions in the pack.
- Similarity detection beyond exact normalized stems, taxonomy completeness, reading-level estimation and locale parity require separately specified, validated checks.
- Persistent browser-based authoring and revision editing are not part of this batch. The existing offline JSON/JSONL authoring and validated-import workflow remains authoritative until a versioned authoring model is designed.