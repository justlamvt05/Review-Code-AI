-- Database: review_code

-- DROP DATABASE IF EXISTS review_code;

-- CREATE DATABASE review_code
--     WITH
--     OWNER = postgres
--     ENCODING = 'UTF8'
--     LC_COLLATE = 'Vietnamese_Vietnam.utf8'
--     LC_CTYPE = 'Vietnamese_Vietnam.utf8'
--     LOCALE_PROVIDER = 'libc'
--     TABLESPACE = pg_default
--     CONNECTION LIMIT = -1
--     IS_TEMPLATE = False;


-- Hỗ trợ extension tạo UUID (nếu dùng bản PostgreSQL cũ, bản mới >= 13 đã có sẵn gen_random_uuid)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- TẠO ENUM TYPE
-- =====================================================
CREATE TYPE role_enum AS ENUM ('ROLE_ADMIN', 'ROLE_USER');

-- -----------------------------------------------------
-- 1. Table: users
-- -----------------------------------------------------
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role role_enum NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------
-- 2. Table: projects
-- -----------------------------------------------------
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    repository_url VARCHAR(500),
    branch VARCHAR(100) DEFAULT 'main',
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------
-- 3. Table: reviews
-- -----------------------------------------------------
CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    rating INTEGER,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    reviewer_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- TẠO INDEX ĐỂ TỐI ƯU TRUY VẤN
-- =====================================================
CREATE INDEX idx_projects_owner_id ON projects(owner_id);
CREATE INDEX idx_reviews_project_id ON reviews(project_id);
CREATE INDEX idx_reviews_reviewer_id ON reviews(reviewer_id);

-- =====================================================
-- TRIGGER TỰ ĐỘNG CẬP NHẬT updated_at
-- =====================================================
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_modtime
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_projects_modtime
    BEFORE UPDATE ON projects
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_reviews_modtime
    BEFORE UPDATE ON reviews
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

-- =====================================================
-- DỮ LIỆU MẪU
-- =====================================================
INSERT INTO users (email, password_hash, role) VALUES
('admin@example.com', '$argon2id$v=19$m=65536,t=3,p=4$QoWYMwEuL74JLLBYc7Fagg$GP6TbVuXGFaRfuspoTsqxpKgDLW/IVyaCRKtF9f2FLc', 'ROLE_ADMIN'),
('nguyen.vana@example.com', '$2a$12$K8K9L0M1N2O3P4Q5R6S7T.U8V9W0X1Y2Z3A4B5C6D7E8F9G0H1I2', 'ROLE_USER'),
('tran.thib@example.com', '$2a$12$L9M0N1O2P3Q4R5S6T7U8V.W9X0Y1Z2A3B4C5D6E7F8G9H0I1J2K3', 'ROLE_USER'),
('le.vanc@example.com', '$2a$12$M0N1O2P3Q4R5S6T7U8V9W.X0Y1Z2A3B4C5D6E7F8G9H0I1J2K3L4', 'ROLE_USER');




-- =====================================================
-- PHASE 8: COMMENTS TABLE
-- =====================================================
CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    review_id UUID NOT NULL REFERENCES reviews(id) ON DELETE CASCADE,
    author_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES comments(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_comments_review_id ON comments(review_id);
CREATE INDEX idx_comments_author_id ON comments(author_id);
CREATE INDEX idx_comments_parent_id ON comments(parent_id);

CREATE TRIGGER update_comments_modtime
    BEFORE UPDATE ON comments
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();


-- =====================================================
-- PHASE 9: NOTIFICATIONS TABLE
-- =====================================================
CREATE TYPE notification_type_enum AS ENUM (
    'COMMENT_ADDED',
    'COMMENT_REPLIED',
    'REVIEW_CREATED',
    'REVIEW_UPDATED'
);

CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipient_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    sender_id UUID REFERENCES users(id) ON DELETE SET NULL,
    type notification_type_enum NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    reference_id UUID,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notifications_recipient_id ON notifications(recipient_id);
CREATE INDEX idx_notifications_is_read ON notifications(recipient_id, is_read);
CREATE INDEX idx_notifications_created_at ON notifications(created_at DESC);

CREATE TRIGGER update_notifications_modtime
    BEFORE UPDATE ON notifications
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();
