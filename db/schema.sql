CREATE DATABASE artlive;
\c artlive

DROP TABLE IF EXISTS users CASCADE;

DROP TYPE IF EXISTS user_role CASCADE;

CREATE TYPE user_role AS ENUM ('instructor', 'student');


CREATE TABLE users(
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email VARCHAR(255) ,
    password TEXT NOT NULL,
    full_name VARCHAR(100) ,
    username VARCHAR(50) NOT NULL UNIQUE,
    bio TEXT,
    profile_image TEXT,
    role user_role NOT NULL,
    specialties TEXT[] DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


