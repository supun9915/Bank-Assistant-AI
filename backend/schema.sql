-- =====================================================
-- Smart Banking Assistant - Database Schema
-- MySQL Database Setup
-- =====================================================

-- Create database
CREATE DATABASE IF NOT EXISTS banking_chatbot;
USE banking_chatbot;

-- =====================================================
-- Table: users
-- Stores user account information
-- =====================================================
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- Table: accounts
-- Stores bank account details and balances
-- =====================================================
CREATE TABLE IF NOT EXISTS accounts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    account_number VARCHAR(20) UNIQUE NOT NULL,
    account_type ENUM('savings', 'checking', 'credit') DEFAULT 'savings',
    balance DECIMAL(15, 2) DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'USD',
    status ENUM('active', 'inactive', 'frozen') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- Table: transactions
-- Stores transaction history
-- =====================================================
CREATE TABLE IF NOT EXISTS transactions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    account_id INT NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    type ENUM('debit', 'credit') NOT NULL,
    description VARCHAR(255),
    reference_number VARCHAR(50) UNIQUE,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    balance_after DECIMAL(15, 2),
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
    INDEX idx_account_date (account_id, date),
    INDEX idx_date (date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- Table: knowledge
-- Knowledge base for predefined Q&A
-- =====================================================
CREATE TABLE IF NOT EXISTS knowledge (
    id INT PRIMARY KEY AUTO_INCREMENT,
    question VARCHAR(500) NOT NULL,
    answer TEXT NOT NULL,
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_question (question(100))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- Table: unknown_questions
-- Stores questions that the bot couldn't answer (for learning)
-- =====================================================
CREATE TABLE IF NOT EXISTS unknown_questions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    question TEXT NOT NULL,
    count INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_asked TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    status ENUM('pending', 'answered', 'ignored') DEFAULT 'pending',
    INDEX idx_status (status),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- SAMPLE DATA FOR TESTING
-- =====================================================

-- Insert sample users
INSERT INTO users (name, email) VALUES
('John Doe', 'john.doe@example.com'),
('Jane Smith', 'jane.smith@example.com'),
('Bob Johnson', 'bob.johnson@example.com');

-- Insert sample accounts
INSERT INTO accounts (user_id, account_number, account_type, balance) VALUES
(1, 'ACC1001234567', 'savings', 5250.00),
(1, 'ACC1001234568', 'checking', 1200.50),
(2, 'ACC2001234567', 'savings', 8750.25),
(3, 'ACC3001234567', 'checking', 3420.80);

-- Insert sample transactions
INSERT INTO transactions (account_id, amount, type, description, reference_number, date, balance_after) VALUES
(1, 500.00, 'credit', 'Salary Deposit', 'TXN001', '2026-04-20 09:00:00', 5250.00),
(1, 150.00, 'debit', 'Grocery Shopping at Walmart', 'TXN002', '2026-04-19 14:30:00', 4750.00),
(1, 75.50, 'debit', 'Restaurant - Pizza Hut', 'TXN003', '2026-04-18 19:45:00', 4900.00),
(1, 1000.00, 'credit', 'Freelance Payment', 'TXN004', '2026-04-17 11:20:00', 4975.50),
(1, 200.00, 'debit', 'Electric Bill Payment', 'TXN005', '2026-04-16 08:15:00', 3975.50),
(1, 50.00, 'debit', 'Netflix Subscription', 'TXN006', '2026-04-15 12:00:00', 4175.50),
(1, 300.00, 'credit', 'Refund from Amazon', 'TXN007', '2026-04-14 16:30:00', 4225.50);

-- Insert sample knowledge base entries
INSERT INTO knowledge (question, answer, category) VALUES
('What are your business hours?', 'Our bank is open Monday to Friday from 9:00 AM to 5:00 PM, and Saturday from 9:00 AM to 1:00 PM. We are closed on Sundays and public holidays.', 'general'),
('How do I reset my password?', 'To reset your password, click on "Forgot Password" on the login page, enter your registered email, and follow the instructions sent to your email.', 'account'),
('What is the minimum balance required?', 'The minimum balance requirement is $100 for savings accounts and $50 for checking accounts.', 'account'),
('How can I contact customer support?', 'You can reach our customer support at 1-800-BANKING (1-800-226-5464) or email us at support@smartbanking.com. Our support team is available 24/7.', 'support'),
('What are the ATM withdrawal limits?', 'The daily ATM withdrawal limit is $500 for standard accounts and $1,000 for premium accounts.', 'atm'),
('How do I apply for a credit card?', 'You can apply for a credit card through our mobile app or by visiting any branch. You will need to provide identification and proof of income.', 'cards'),
('What interest rates do you offer?', 'We offer competitive interest rates: 3.5% APY for savings accounts, 0.5% APY for checking accounts, and varying rates for fixed deposits based on tenure.', 'interest'),
('How do I transfer money?', 'You can transfer money through our mobile app, online banking, or by visiting a branch. Instant transfers are available within the same bank.', 'transfer');

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Verify data insertion
SELECT 'Users created:' as Info, COUNT(*) as Count FROM users
UNION ALL
SELECT 'Accounts created:', COUNT(*) FROM accounts
UNION ALL
SELECT 'Transactions created:', COUNT(*) FROM transactions
UNION ALL
SELECT 'Knowledge entries:', COUNT(*) FROM knowledge;

-- Display sample data
SELECT '=== Sample User Account ===' as Info;
SELECT u.name, u.email, a.account_number, a.account_type, a.balance
FROM users u
JOIN accounts a ON u.id = a.user_id
WHERE u.id = 1;

SELECT '=== Sample Transactions ===' as Info;
SELECT amount, type, description, date
FROM transactions
WHERE account_id = 1
ORDER BY date DESC
LIMIT 5;
