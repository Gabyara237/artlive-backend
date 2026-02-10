CREATE DATABASE artlive;
\c artlive

DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS workshops CASCADE;

DROP TYPE IF EXISTS user_role CASCADE;
DROP TYPE IF EXISTS difficulty_level CASCADE;
DROP TYPE IF EXISTS workshops_art_type CASCADE;

CREATE TYPE user_role AS ENUM ('instructor', 'student');
CREATE TYPE difficulty_level AS ENUM ('beginner', 'intermediate', 'advanced');
CREATE TYPE workshops_art_type AS ENUM (  
    'watercolor_painting',
    'oil_painting',
    'acrylic_painting',
    'charcoal_pastel_drawing',
    'ink_drawing_calligraphy',
    'mixed_media',
    'ceramics_pottery',
    'clay_sculpture',
    'wood_sculpture_carving',
    'mosaic_art'
);


CREATE TABLE users(
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password TEXT NOT NULL,
    full_name VARCHAR(100) ,
    username VARCHAR(50) NOT NULL UNIQUE,
    bio TEXT,
    profile_image TEXT,
    role user_role NOT NULL,
    specialties TEXT[] DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE workshops(
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    user_id INTEGER NOT NULL,
    CONSTRAINT author FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,

    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,

    art_type workshops_art_type NOT NULL,
    level difficulty_level NOT NULL, 

    workshop_date DATE NOT NULL,
    start_time TIME NOT NULL,
    duration_hours INTEGER NOT NULL,

    address VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,

    longitude DECIMAL(9,6),
    latitude DECIMAL(9,6),

    max_capacity INTEGER NOT NULL,
    current_registrations INTEGER NOT NULL DEFAULT 0,

    materials_included TEXT,
    materials_to_bring TEXT,
    image_url VARCHAR(255),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT workshops_capacity_check
    CHECK (max_capacity >= 0 AND current_registrations >= 0 AND current_registrations <= max_capacity)
)