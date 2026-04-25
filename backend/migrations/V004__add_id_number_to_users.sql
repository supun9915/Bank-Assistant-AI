-- Migration: Add id_number to users table
-- Created: 2026-04-25
-- id_number (NIC / passport) is used to verify identity during OTP send

USE banking_chatbot;

ALTER TABLE users
    ADD COLUMN id_number VARCHAR(50) NULL AFTER email,
    ADD UNIQUE KEY uq_id_number (id_number);

-- Assign sample id numbers to existing seed users
UPDATE users SET id_number = 'NIC1001001' WHERE id = 1; -- John Doe
UPDATE users SET id_number = 'NIC2001001' WHERE id = 2; -- Jane Smith
UPDATE users SET id_number = 'NIC3001001' WHERE id = 3; -- Bob Johnson
UPDATE users SET id_number = 'NIC4001001' WHERE id = 4; -- Alice Brown
UPDATE users SET id_number = 'NIC5001001' WHERE id = 5; -- Charlie Davis

-- Make the column NOT NULL now that all rows have values
ALTER TABLE users
    MODIFY COLUMN id_number VARCHAR(50) NOT NULL;
