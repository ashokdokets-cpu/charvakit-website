-- ============================================================================
-- Charvak IT Consulting - pgvector for skill embeddings (#42)
-- Migration: 20260920_skill_embeddings.sql
-- Created:   2026-09-20
-- Purpose:   Replace static SKILL_EMBEDDINGS dict with real vector similarity
--            using pgvector + OpenAI text-embedding-3-small (1536 dims).
-- Safety:    All CREATE ... IF NOT EXISTS. Idempotent. Skips gracefully if
--            pgvector extension is not available (local dev / older Postgres).
-- Prereq:    pgvector extension must be enabled on prod
--            (Render Postgres has it available: CREATE EXTENSION vector)
-- Rollback:  DROP TABLE IF EXISTS charvak_skill_embeddings;
-- ============================================================================

-- Try to enable pgvector. If unavailable, skip gracefully.
DO $$
BEGIN
    CREATE EXTENSION IF NOT EXISTS vector;
    RAISE NOTICE 'pgvector extension ready';
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'pgvector unavailable, skipping skill_embeddings migration: %', SQLERRM;
END $$;

-- Only create the table if pgvector is available
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector') THEN
        -- Create table
        EXECUTE '
            CREATE TABLE IF NOT EXISTS charvak_skill_embeddings (
                skill       TEXT PRIMARY KEY,
                category    TEXT,
                embedding   vector(1536),
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ';

        -- Create IVFFlat index for cosine similarity
        EXECUTE '
            CREATE INDEX IF NOT EXISTS idx_skill_embeddings_cosine
                ON charvak_skill_embeddings
                USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 10)
        ';

        -- Category index
        EXECUTE '
            CREATE INDEX IF NOT EXISTS idx_skill_embeddings_category
                ON charvak_skill_embeddings(category)
        ';

        RAISE NOTICE 'charvak_skill_embeddings table created';
    ELSE
        RAISE NOTICE 'pgvector not installed - skipping table creation';
    END IF;
END $$;

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
