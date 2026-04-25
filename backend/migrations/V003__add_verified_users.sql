-- =====================================================
-- V003: Add verified_users table for chatbot identity
-- =====================================================

USE banking_chatbot;

CREATE TABLE IF NOT EXISTS verified_users (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    email       VARCHAR(150) NOT NULL,
    id_number   VARCHAR(50)  NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_email (email),
    INDEX idx_id_number (id_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
