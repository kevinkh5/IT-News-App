CREATE DATABASE IF NOT EXISTS testDB;
USE testDB;

CREATE TABLE IF NOT EXISTS news_info (
    id SERIAL PRIMARY KEY,
    category VARCHAR(30) NOT NULL,
    title VARCHAR(300) UNIQUE NOT NULL,
    author VARCHAR(30) NOT NULL,
    img_link VARCHAR(255),
    destination_link VARCHAR(255) NOT NULL,
    date TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL,
    INDEX (category),
    INDEX (title)
);

CREATE TABLE IF NOT EXISTS news_content (
    id SERIAL PRIMARY KEY,
    news_info_id INTEGER UNIQUE NOT NULL,
    description TEXT NOT NULL,
    summary TEXT,
    created_at TIMESTAMP NOT NULL,
    CONSTRAINT fk_news_info
        FOREIGN KEY(news_info_id) 
        REFERENCES news_info(id)
        ON DELETE CASCADE,
    INDEX (news_info_id)
);