-- QuizVeda PostgreSQL starter schema. Review and split into Alembic migrations before production.
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE TABLE users (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 email text UNIQUE,
 password_hash text,
 display_name varchar(80),
 account_status varchar(20) NOT NULL DEFAULT 'active' CHECK (account_status IN ('active','suspended','deletion_pending','deleted')),
 preferred_locale varchar(16) NOT NULL DEFAULT 'en-IN',
 created_at timestamptz NOT NULL DEFAULT now(),
 updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE user_profiles (
 user_id uuid PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
 learning_stage varchar(30), occupation_group varchar(50), experience_band varchar(30),
 learning_goal varchar(40), preferred_language varchar(16) NOT NULL DEFAULT 'en-IN',
 accessibility_preferences jsonb NOT NULL DEFAULT '{}'::jsonb,
 personalization_enabled boolean NOT NULL DEFAULT true,
 updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE taxonomy_nodes (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), node_key varchar(120) NOT NULL UNIQUE,
 parent_id uuid REFERENCES taxonomy_nodes(id) ON DELETE RESTRICT,
 node_type varchar(20) NOT NULL CHECK (node_type IN ('subject','domain','topic','subtopic','skill')),
 label jsonb NOT NULL, description jsonb NOT NULL DEFAULT '{}'::jsonb,
 status varchar(16) NOT NULL DEFAULT 'active' CHECK (status IN ('draft','active','retired')),
 sort_order int NOT NULL DEFAULT 0, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_taxonomy_parent_sort ON taxonomy_nodes(parent_id,sort_order);
CREATE TABLE profile_subject_preferences (
 user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 taxonomy_node_id uuid NOT NULL REFERENCES taxonomy_nodes(id) ON DELETE RESTRICT,
 source varchar(20) NOT NULL CHECK (source IN ('explicit','imported')),
 strength numeric(4,3) NOT NULL DEFAULT 1 CHECK (strength BETWEEN 0 AND 1),
 PRIMARY KEY(user_id,taxonomy_node_id)
);
CREATE TABLE content_packs (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), pack_key varchar(120) NOT NULL UNIQUE,
 title jsonb NOT NULL, description jsonb NOT NULL DEFAULT '{}'::jsonb,
 owner_user_id uuid REFERENCES users(id) ON DELETE SET NULL,
 visibility varchar(16) NOT NULL DEFAULT 'internal' CHECK (visibility IN ('internal','unlisted','public')),
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE content_pack_versions (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 pack_id uuid NOT NULL REFERENCES content_packs(id) ON DELETE RESTRICT,
 version varchar(40) NOT NULL, schema_version varchar(20) NOT NULL, locale varchar(16) NOT NULL,
 object_uri text NOT NULL, sha256 char(64) NOT NULL UNIQUE,
 question_count int NOT NULL DEFAULT 0 CHECK(question_count >= 0),
 lifecycle_status varchar(20) NOT NULL DEFAULT 'uploaded'
 CHECK(lifecycle_status IN ('uploaded','validating','validated','rejected','approved','published','retired')),
 validation_report jsonb NOT NULL DEFAULT '{}'::jsonb,
 created_by uuid REFERENCES users(id) ON DELETE SET NULL, created_at timestamptz NOT NULL DEFAULT now(),
 UNIQUE(pack_id,version)
);
CREATE TABLE questions (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), question_key varchar(160) NOT NULL UNIQUE,
 content_pack_version_id uuid REFERENCES content_pack_versions(id) ON DELETE RESTRICT,
 lifecycle_status varchar(16) NOT NULL DEFAULT 'draft'
 CHECK(lifecycle_status IN ('draft','review','approved','retired')),
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE question_revisions (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 question_id uuid NOT NULL REFERENCES questions(id) ON DELETE RESTRICT,
 revision_no int NOT NULL CHECK(revision_no > 0), stem jsonb NOT NULL,
 explanation jsonb NOT NULL DEFAULT '{}'::jsonb,
 difficulty varchar(16) NOT NULL CHECK(difficulty IN ('beginner','standard','advanced','expert')),
 question_type varchar(24) NOT NULL DEFAULT 'single_choice', locale varchar(16) NOT NULL,
 estimated_seconds int NOT NULL DEFAULT 30 CHECK(estimated_seconds BETWEEN 5 AND 600),
 answer_key_ciphertext bytea NOT NULL, answer_key_key_version varchar(40) NOT NULL,
 provenance jsonb NOT NULL DEFAULT '{}'::jsonb,
 review_state varchar(16) NOT NULL DEFAULT 'draft'
 CHECK(review_state IN ('draft','in_review','approved','rejected')),
 created_at timestamptz NOT NULL DEFAULT now(), UNIQUE(question_id,revision_no)
);
CREATE TABLE question_options (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 question_revision_id uuid NOT NULL REFERENCES question_revisions(id) ON DELETE CASCADE,
 option_key varchar(12) NOT NULL, content jsonb NOT NULL, display_order smallint NOT NULL,
 UNIQUE(question_revision_id,option_key), UNIQUE(question_revision_id,display_order)
);
CREATE TABLE question_taxonomy (
 question_revision_id uuid NOT NULL REFERENCES question_revisions(id) ON DELETE CASCADE,
 taxonomy_node_id uuid NOT NULL REFERENCES taxonomy_nodes(id) ON DELETE RESTRICT,
 relevance_weight numeric(4,3) NOT NULL DEFAULT 1 CHECK(relevance_weight BETWEEN 0 AND 1),
 PRIMARY KEY(question_revision_id,taxonomy_node_id)
);
CREATE TABLE perspectives (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), perspective_key varchar(80) NOT NULL UNIQUE,
 label jsonb NOT NULL, status varchar(16) NOT NULL DEFAULT 'active'
);
CREATE TABLE question_perspectives (
 question_revision_id uuid NOT NULL REFERENCES question_revisions(id) ON DELETE CASCADE,
 perspective_id uuid NOT NULL REFERENCES perspectives(id) ON DELETE RESTRICT,
 weight numeric(4,3) NOT NULL DEFAULT 1 CHECK(weight BETWEEN 0 AND 1),
 PRIMARY KEY(question_revision_id,perspective_id)
);
CREATE TABLE learning_objectives (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), objective_key varchar(80) NOT NULL UNIQUE,
 cognitive_level varchar(20) NOT NULL CHECK(cognitive_level IN ('remember','understand','apply','analyze','evaluate','create')),
 label jsonb NOT NULL
);
CREATE TABLE question_objectives (
 question_revision_id uuid NOT NULL REFERENCES question_revisions(id) ON DELETE CASCADE,
 objective_id uuid NOT NULL REFERENCES learning_objectives(id) ON DELETE RESTRICT,
 PRIMARY KEY(question_revision_id,objective_id)
);
CREATE TABLE game_modes (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), mode_key varchar(60) NOT NULL UNIQUE,
 config jsonb NOT NULL, is_enabled boolean NOT NULL DEFAULT true
);
CREATE TABLE quiz_sessions (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 user_id uuid REFERENCES users(id) ON DELETE SET NULL,
 guest_session_hash char(64),
 mode_id uuid NOT NULL REFERENCES game_modes(id) ON DELETE RESTRICT,
 pack_version_id uuid REFERENCES content_pack_versions(id) ON DELETE RESTRICT,
 selection_policy_version varchar(30) NOT NULL,
 selected_taxonomy jsonb NOT NULL DEFAULT '[]'::jsonb,
 difficulty_policy jsonb NOT NULL,
 status varchar(20) NOT NULL DEFAULT 'created'
 CHECK(status IN ('created','in_progress','completed','abandoned','expired')),
 current_position int NOT NULL DEFAULT 0 CHECK(current_position >= 0),
 score int NOT NULL DEFAULT 0 CHECK(score >= 0),
 started_at timestamptz, completed_at timestamptz, expires_at timestamptz NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now(),
 CHECK(user_id IS NOT NULL OR guest_session_hash IS NOT NULL)
);
CREATE INDEX idx_sessions_user_created ON quiz_sessions(user_id,created_at DESC);
CREATE INDEX idx_sessions_status_expiry ON quiz_sessions(status,expires_at);
CREATE TABLE session_questions (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 session_id uuid NOT NULL REFERENCES quiz_sessions(id) ON DELETE CASCADE,
 question_revision_id uuid NOT NULL REFERENCES question_revisions(id) ON DELETE RESTRICT,
 position int NOT NULL CHECK(position > 0), question_token_hash char(64) NOT NULL,
 issued_at timestamptz NOT NULL, deadline_at timestamptz,
 status varchar(16) NOT NULL DEFAULT 'issued' CHECK(status IN ('issued','answered','timed_out','skipped')),
 score_value int NOT NULL DEFAULT 0 CHECK(score_value >= 0),
 UNIQUE(session_id,position), UNIQUE(session_id,question_revision_id)
);
CREATE TABLE answer_attempts (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 session_question_id uuid NOT NULL UNIQUE REFERENCES session_questions(id) ON DELETE RESTRICT,
 idempotency_key varchar(100) NOT NULL UNIQUE, selected_option_key varchar(12),
 is_correct boolean NOT NULL, response_ms int CHECK(response_ms >= 0),
 awarded_score int NOT NULL DEFAULT 0, submitted_at timestamptz NOT NULL DEFAULT now(),
 outcome_payload jsonb NOT NULL DEFAULT '{}'::jsonb
);
CREATE TABLE lifeline_uses (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), session_id uuid NOT NULL REFERENCES quiz_sessions(id) ON DELETE CASCADE,
 lifeline_key varchar(40) NOT NULL, question_position int NOT NULL,
 result_payload jsonb NOT NULL, used_at timestamptz NOT NULL DEFAULT now(),
 UNIQUE(session_id,lifeline_key)
);
CREATE TABLE session_events (
 id bigserial PRIMARY KEY, session_id uuid NOT NULL REFERENCES quiz_sessions(id) ON DELETE CASCADE,
 event_type varchar(60) NOT NULL, event_version int NOT NULL DEFAULT 1,
 event_payload jsonb NOT NULL DEFAULT '{}'::jsonb, occurred_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_session_events_session_time ON session_events(session_id,occurred_at);
CREATE TABLE user_topic_progress (
 user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 taxonomy_node_id uuid NOT NULL REFERENCES taxonomy_nodes(id) ON DELETE RESTRICT,
 attempts int NOT NULL DEFAULT 0, correct_attempts int NOT NULL DEFAULT 0,
 mastery_score numeric(5,2) NOT NULL DEFAULT 0 CHECK(mastery_score BETWEEN 0 AND 100),
 last_attempt_at timestamptz, updated_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(user_id,taxonomy_node_id), CHECK(correct_attempts <= attempts)
);
CREATE TABLE content_publications (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 pack_id uuid NOT NULL REFERENCES content_packs(id) ON DELETE RESTRICT,
 pack_version_id uuid NOT NULL REFERENCES content_pack_versions(id) ON DELETE RESTRICT,
 environment varchar(16) NOT NULL CHECK(environment IN ('staging','production')),
 published_by uuid REFERENCES users(id) ON DELETE SET NULL,
 published_at timestamptz NOT NULL DEFAULT now(),
 rollback_of uuid REFERENCES content_publications(id)
);
CREATE TABLE admin_audit_events (
 id bigserial PRIMARY KEY, actor_user_id uuid REFERENCES users(id) ON DELETE SET NULL,
 action varchar(80) NOT NULL, target_type varchar(60) NOT NULL, target_id varchar(120) NOT NULL,
 before_state jsonb, after_state jsonb, request_id varchar(100),
 occurred_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_admin_audit_target_time ON admin_audit_events(target_type,target_id,occurred_at DESC);
