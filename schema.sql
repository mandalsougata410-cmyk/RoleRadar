-- RoleRadar PostgreSQL + pgvector Schema
-- Extension for vector embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Users table (profile and preferences memory)
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(100),
    skills TEXT[] DEFAULT '{}',
    preferred_locations TEXT[] DEFAULT '{}',
    target_roles TEXT[] DEFAULT '{}',
    min_stipend INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Jobs & Internships table
CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    location VARCHAR(100) NOT NULL,
    is_remote BOOLEAN DEFAULT FALSE,
    stipend INTEGER DEFAULT 0,
    skills_required TEXT[] DEFAULT '{}',
    requirements_text TEXT NOT NULL,
    embedding VECTOR(768), -- Default 768 for gemini text-embedding-004
    posted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Persistent Conversation History
CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(64) REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- 'user', 'assistant', 'model', 'system'
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User Interactions for Personalized Re-ranking (down-ranking dismissed, boosting viewed)
CREATE TABLE IF NOT EXISTS job_interactions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(64) REFERENCES users(id) ON DELETE CASCADE,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    action VARCHAR(20) NOT NULL, -- 'viewed', 'saved', 'dismissed', 'applied'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for blazing fast retrieval
CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs(location);
CREATE INDEX IF NOT EXISTS idx_jobs_remote ON jobs(is_remote);
CREATE INDEX IF NOT EXISTS idx_jobs_stipend ON jobs(stipend);
CREATE INDEX IF NOT EXISTS idx_chat_user ON chat_messages(user_id);
