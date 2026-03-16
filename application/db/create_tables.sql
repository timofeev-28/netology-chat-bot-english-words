CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    tg_id BIGINT UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS words (
    id SERIAL PRIMARY KEY,
    word_ru VARCHAR(255) UNIQUE NOT NULL,
    word_en VARCHAR(255) UNIQUE NOT NULL,
    is_common BOOLEAN DEFAULT TRUE NOT NULL,
    CONSTRAINT unique_word_pair UNIQUE (word_ru, word_en)
);

CREATE TABLE IF NOT EXISTS users_words (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    word_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_word
        FOREIGN KEY (word_id)
        REFERENCES words(id)
        ON DELETE CASCADE,
    CONSTRAINT unique_user_word UNIQUE (user_id, word_id)
);
