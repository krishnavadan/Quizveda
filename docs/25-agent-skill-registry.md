# 25. Agent Skills Registry and Reusable Procedures

## Skill design
A skill is a narrow, versioned, testable procedure, independent of model vendor. Each skill declares purpose, trigger, inputs, preconditions, steps, output schema, prohibited actions, quality gates, examples, evaluation set, owner and semantic version.

## Initial skill catalogue
| ID | Skill | Consumers |
|---|---|---|
| S01 | Task Classification & Routing | Orchestrator |
| S02 | Evidence Retrieval & Citation | Researcher |
| S03 | Question Blueprinting | Question Architect |
| S04 | MCQ Drafting | Question Architect |
| S05 | Independent Answer Solve | Answer Verifier |
| S06 | Distractor Quality Audit | Answer Verifier |
| S07 | Explanation & Teaching Design | Pedagogy Reviewer |
| S08 | Cognitive-Level Calibration | Taxonomy Curator |
| S09 | Age-Level Reading Adaptation | Age Reviewer |
| S10 | Safety, Bias & Inclusion Audit | Safety/Equity Reviewers |
| S11 | Duplicate & Near-Duplicate Detection | Editor |
| S12 | Localization & Cultural Adaptation | Localization Agent |
| S13 | JSON Schema & Pack Validation | Content pipeline |
| S14 | Content Provenance & Rights Check | Researcher/editor |
| S15 | Learner Recommendation Explanation | Personalization Planner |
| S16 | Memory Graph Read/Write | authorised agents |
| S17 | MCP Tool Selection & Least Privilege | Orchestrator |
| S18 | Token Budget & Context Compression | all agents |
| S19 | Evaluation Dataset Generation | Test Engineer |
| S20 | Regression & Release Gate | Release Auditor |
| S21 | Accessibility Review | UX/QA |
| S22 | Incident Triage & Escalation | security/ops |
| S23 | Privacy Data Lifecycle | privacy reviewer |
| S24 | Content Performance Analysis | Assessment Analyst |

## Composition
Evidence retrieval -> blueprint -> draft -> independent solve + distractor audit + explanation review -> objective calibration -> age/safety/inclusion review -> duplicate check -> schema validation -> provenance check -> human approval.

## Versioning and tests
Pin skill versions in every agent run. Maintain positive, negative, adversarial and edge-case fixtures. Evaluate changes against frozen regression sets. Breaking output changes require schema version bump and migration. Production eligibility requires owner, schema, test set, failure behavior, permissions, budget, observability and rollback.
