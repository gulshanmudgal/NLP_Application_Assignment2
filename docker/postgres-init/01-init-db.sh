#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create database extensions
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";
    
    -- Create application schema
    CREATE SCHEMA IF NOT EXISTS nlp_app;
    
    -- Create translation history table
    CREATE TABLE IF NOT EXISTS nlp_app.translation_history (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        source_text TEXT NOT NULL,
        translated_text TEXT NOT NULL,
        source_language VARCHAR(10) NOT NULL,
        target_language VARCHAR(10) NOT NULL,
        model_used VARCHAR(50) NOT NULL,
        confidence_score FLOAT,
        processing_time FLOAT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        user_session VARCHAR(255)
    );
    
    -- Create language pairs table
    CREATE TABLE IF NOT EXISTS nlp_app.language_pairs (
        id SERIAL PRIMARY KEY,
        source_language VARCHAR(10) NOT NULL,
        target_language VARCHAR(10) NOT NULL,
        is_supported BOOLEAN DEFAULT TRUE,
        model_name VARCHAR(50),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        UNIQUE(source_language, target_language)
    );
    
    -- Create translation statistics table
    CREATE TABLE IF NOT EXISTS nlp_app.translation_stats (
        id SERIAL PRIMARY KEY,
        date DATE DEFAULT CURRENT_DATE,
        total_translations INTEGER DEFAULT 0,
        cache_hits INTEGER DEFAULT 0,
        cache_misses INTEGER DEFAULT 0,
        avg_processing_time FLOAT DEFAULT 0,
        language_pair VARCHAR(25),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        UNIQUE(date, language_pair)
    );
    
    -- Insert supported language pairs
    INSERT INTO nlp_app.language_pairs (source_language, target_language, model_name) VALUES
    ('en', 'hi', 'mock_translator'),
    ('hi', 'en', 'mock_translator'),
    ('en', 'ta', 'mock_translator'),
    ('ta', 'en', 'mock_translator'),
    ('en', 'te', 'mock_translator'),
    ('te', 'en', 'mock_translator'),
    ('en', 'bn', 'mock_translator'),
    ('bn', 'en', 'mock_translator'),
    ('en', 'mr', 'mock_translator'),
    ('mr', 'en', 'mock_translator')
    ON CONFLICT (source_language, target_language) DO NOTHING;
    
    -- Create indexes for better performance
    CREATE INDEX IF NOT EXISTS idx_translation_history_languages 
        ON nlp_app.translation_history(source_language, target_language);
    CREATE INDEX IF NOT EXISTS idx_translation_history_created_at 
        ON nlp_app.translation_history(created_at);
    CREATE INDEX IF NOT EXISTS idx_translation_stats_date 
        ON nlp_app.translation_stats(date);
    
    -- Grant permissions
    GRANT ALL PRIVILEGES ON SCHEMA nlp_app TO "$POSTGRES_USER";
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA nlp_app TO "$POSTGRES_USER";
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA nlp_app TO "$POSTGRES_USER";
    
    ECHO 'Database initialization completed successfully!';
EOSQL
