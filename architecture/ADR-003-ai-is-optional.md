# ADR-003: AI Is Not a Learner Runtime Dependency

**Status:** Superseded by ADR-006 for scope clarity; retained as historical decision.

AI may assist internal authoring and engineering workflows. The production learner application does not call AI models. Gameplay, question selection, explanations, scoring, timers, recommendations and progression use deterministic application logic and approved versioned content. No AI service availability, model API key or token budget is required to operate the learner product. See ADR-006.
