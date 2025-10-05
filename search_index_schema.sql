-- Search Engine Inverted Index Schema
-- Optimized for fast full-text search across NFL player data

-- Documents table: stores all searchable entities
CREATE TABLE IF NOT EXISTS search_documents (
    id SERIAL PRIMARY KEY,
    doc_type VARCHAR(50) NOT NULL,  -- 'player', 'team', 'game'
    entity_id VARCHAR(100) NOT NULL,  -- API ID (player_id, team_id, game_id)
    title VARCHAR(500) NOT NULL,  -- Player name, team name, etc.
    content TEXT NOT NULL,  -- Full searchable text
    metadata JSONB,  -- Additional structured data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(doc_type, entity_id)
);

-- Create index on doc_type for filtering
CREATE INDEX IF NOT EXISTS idx_search_documents_type ON search_documents(doc_type);

-- Create GIN index on metadata for fast JSONB queries
CREATE INDEX IF NOT EXISTS idx_search_documents_metadata ON search_documents USING GIN(metadata);

-- Inverted index: maps terms to document IDs
CREATE TABLE IF NOT EXISTS search_index (
    id SERIAL PRIMARY KEY,
    term VARCHAR(100) NOT NULL,  -- Stemmed search term
    doc_id INTEGER NOT NULL REFERENCES search_documents(id) ON DELETE CASCADE,
    frequency INTEGER DEFAULT 1,  -- How many times term appears in doc
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(term, doc_id)
);

-- Create index on term for fast lookups
CREATE INDEX IF NOT EXISTS idx_search_index_term ON search_index(term);

-- Create index on doc_id for joins
CREATE INDEX IF NOT EXISTS idx_search_index_doc_id ON search_index(doc_id);

-- Composite index for term + doc_id lookups
CREATE INDEX IF NOT EXISTS idx_search_index_term_doc ON search_index(term, doc_id);

-- Search statistics table: track popular searches
CREATE TABLE IF NOT EXISTS search_stats (
    id SERIAL PRIMARY KEY,
    query TEXT NOT NULL,
    result_count INTEGER DEFAULT 0,
    search_count INTEGER DEFAULT 1,
    last_searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(query)
);

-- Create index for popular queries
CREATE INDEX IF NOT EXISTS idx_search_stats_count ON search_stats(search_count DESC);

-- Player-specific search view (optimized for common queries)
CREATE OR REPLACE VIEW player_search_view AS
SELECT
    sd.id as doc_id,
    sd.entity_id as player_id,
    sd.title as player_name,
    sd.metadata->>'team' as team,
    sd.metadata->>'position' as position,
    sd.metadata->>'number' as jersey_number,
    sd.metadata->>'status' as status,
    sd.content as searchable_text,
    sd.updated_at
FROM search_documents sd
WHERE sd.doc_type = 'player';

-- Team-specific search view
CREATE OR REPLACE VIEW team_search_view AS
SELECT
    sd.id as doc_id,
    sd.entity_id as team_id,
    sd.title as team_name,
    sd.metadata->>'city' as city,
    sd.metadata->>'abbreviation' as abbreviation,
    sd.metadata->>'division' as division,
    sd.metadata->>'conference' as conference,
    sd.content as searchable_text,
    sd.updated_at
FROM search_documents sd
WHERE sd.doc_type = 'team';

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_search_document_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update timestamp
DROP TRIGGER IF EXISTS search_document_update_trigger ON search_documents;
CREATE TRIGGER search_document_update_trigger
    BEFORE UPDATE ON search_documents
    FOR EACH ROW
    EXECUTE FUNCTION update_search_document_timestamp();

-- Function to increment search count
CREATE OR REPLACE FUNCTION increment_search_count(search_query TEXT, result_cnt INTEGER)
RETURNS VOID AS $$
BEGIN
    INSERT INTO search_stats (query, result_count, search_count, last_searched_at)
    VALUES (search_query, result_cnt, 1, CURRENT_TIMESTAMP)
    ON CONFLICT (query)
    DO UPDATE SET
        search_count = search_stats.search_count + 1,
        result_count = result_cnt,
        last_searched_at = CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql;

-- Function to perform full-text search with ranking
CREATE OR REPLACE FUNCTION search_documents(
    search_query TEXT,
    doc_type_filter VARCHAR(50) DEFAULT NULL,
    max_results INTEGER DEFAULT 50
)
RETURNS TABLE (
    doc_id INTEGER,
    entity_id VARCHAR(100),
    title VARCHAR(500),
    doc_type VARCHAR(50),
    metadata JSONB,
    relevance_score FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        sd.id,
        sd.entity_id,
        sd.title,
        sd.doc_type,
        sd.metadata,
        SUM(si.frequency)::FLOAT / (1.0 + COUNT(*)::FLOAT) as relevance_score
    FROM search_documents sd
    JOIN search_index si ON sd.id = si.doc_id
    WHERE
        si.term = ANY(string_to_array(lower(search_query), ' '))
        AND (doc_type_filter IS NULL OR sd.doc_type = doc_type_filter)
    GROUP BY sd.id, sd.entity_id, sd.title, sd.doc_type, sd.metadata
    ORDER BY relevance_score DESC
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Function to get autocomplete suggestions
CREATE OR REPLACE FUNCTION search_autocomplete(
    prefix TEXT,
    doc_type_filter VARCHAR(50) DEFAULT NULL,
    max_results INTEGER DEFAULT 10
)
RETURNS TABLE (
    suggestion TEXT,
    entity_id VARCHAR(100),
    doc_type VARCHAR(50)
) AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT
        sd.title,
        sd.entity_id,
        sd.doc_type
    FROM search_documents sd
    WHERE
        LOWER(sd.title) LIKE LOWER(prefix || '%')
        AND (doc_type_filter IS NULL OR sd.doc_type = doc_type_filter)
    ORDER BY sd.title
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions (adjust user as needed)
-- GRANT ALL ON search_documents TO your_db_user;
-- GRANT ALL ON search_index TO your_db_user;
-- GRANT ALL ON search_stats TO your_db_user;

-- Comments for documentation
COMMENT ON TABLE search_documents IS 'Stores all searchable documents (players, teams, games)';
COMMENT ON TABLE search_index IS 'Inverted index mapping terms to documents';
COMMENT ON TABLE search_stats IS 'Tracks search query statistics and popularity';
COMMENT ON FUNCTION search_documents IS 'Full-text search with relevance ranking';
COMMENT ON FUNCTION search_autocomplete IS 'Provides autocomplete suggestions based on prefix';
COMMENT ON FUNCTION increment_search_count IS 'Tracks search query usage for analytics';
