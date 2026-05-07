-- Migration: Add loans, FD, pawning tables + new users, accounts, transactions
-- Created: 2026-04-25

-- =====================================================
-- Table: loans
-- =====================================================
CREATE TABLE IF NOT EXISTS loans (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    user_id         INT NOT NULL,
    account_id      INT NOT NULL,
    loan_type       ENUM('personal', 'home', 'auto', 'education', 'business') NOT NULL,
    principal       DECIMAL(15, 2) NOT NULL,
    interest_rate   DECIMAL(5, 2) NOT NULL COMMENT 'Annual % rate',
    term_months     INT NOT NULL COMMENT 'Loan duration in months',
    monthly_payment DECIMAL(15, 2) NOT NULL,
    outstanding     DECIMAL(15, 2) NOT NULL,
    disbursed_at    DATE NOT NULL,
    due_date        DATE NOT NULL,
    status          ENUM('active', 'closed', 'defaulted', 'pending') DEFAULT 'active',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)    REFERENCES users(id)    ON DELETE CASCADE,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
    INDEX idx_loan_user   (user_id),
    INDEX idx_loan_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- Table: loan_repayments
-- =====================================================
CREATE TABLE IF NOT EXISTS loan_repayments (
    id                INT PRIMARY KEY AUTO_INCREMENT,
    loan_id           INT NOT NULL,
    amount            DECIMAL(15, 2) NOT NULL,
    paid_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reference         VARCHAR(50) UNIQUE,
    outstanding_after DECIMAL(15, 2),
    FOREIGN KEY (loan_id) REFERENCES loans(id) ON DELETE CASCADE,
    INDEX idx_loan_repay (loan_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- Table: fixed_deposits (FD)
-- =====================================================
CREATE TABLE IF NOT EXISTS fixed_deposits (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    user_id         INT NOT NULL,
    account_id      INT NOT NULL,
    fd_number       VARCHAR(30) UNIQUE NOT NULL,
    principal       DECIMAL(15, 2) NOT NULL,
    interest_rate   DECIMAL(5, 2) NOT NULL COMMENT 'Annual % rate',
    term_months     INT NOT NULL,
    maturity_amount DECIMAL(15, 2) NOT NULL,
    start_date      DATE NOT NULL,
    maturity_date   DATE NOT NULL,
    auto_renew      BOOLEAN DEFAULT FALSE,
    status          ENUM('active', 'matured', 'broken', 'renewed') DEFAULT 'active',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)    REFERENCES users(id)    ON DELETE CASCADE,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
    INDEX idx_fd_user   (user_id),
    INDEX idx_fd_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- Table: pawning (pawn loans)
-- =====================================================
CREATE TABLE IF NOT EXISTS pawning (
    id               INT PRIMARY KEY AUTO_INCREMENT,
    user_id          INT NOT NULL,
    account_id       INT NOT NULL,
    ticket_number    VARCHAR(30) UNIQUE NOT NULL,
    item_description TEXT NOT NULL,
    item_category    ENUM('gold', 'silver', 'electronics', 'vehicle', 'jewelry', 'other') DEFAULT 'other',
    appraised_value  DECIMAL(15, 2) NOT NULL,
    loan_amount      DECIMAL(15, 2) NOT NULL,
    interest_rate    DECIMAL(5, 2) NOT NULL COMMENT 'Monthly % rate',
    pledged_at       DATE NOT NULL,
    due_date         DATE NOT NULL,
    outstanding      DECIMAL(15, 2) NOT NULL,
    status           ENUM('active', 'redeemed', 'auctioned', 'extended') DEFAULT 'active',
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)    REFERENCES users(id)    ON DELETE CASCADE,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
    INDEX idx_pawn_user   (user_id),
    INDEX idx_pawn_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- New users (IDs 4 & 5)
-- =====================================================
INSERT IGNORE INTO users (name, email) VALUES
('Alice Brown',   'alice.brown@example.com'),
('Charlie Davis', 'charlie.davis@example.com');

-- =====================================================
-- New accounts
-- Alice  -> savings + credit
-- Charlie -> checking + savings + credit
-- =====================================================
INSERT IGNORE INTO accounts (user_id, account_number, account_type, balance, currency) VALUES
(4, 'ACC4001234567', 'savings',  12000.00, 'USD'),
(4, 'ACC4001234568', 'credit',    3500.00, 'USD'),
(5, 'ACC5001234567', 'checking',  9800.50, 'USD'),
(5, 'ACC5001234568', 'savings',  22500.75, 'USD'),
(5, 'ACC5001234569', 'credit',    5000.00, 'USD');

-- =====================================================
-- Transactions - Alice savings (account_id = 5)
-- 20 transactions
-- =====================================================
INSERT IGNORE INTO transactions (account_id, amount, type, description, reference_number, date, balance_after) VALUES
(5, 3000.00, 'credit', 'Opening Deposit',            'TXN101', '2026-01-01 09:00:00', 3000.00),
(5, 1500.00, 'credit', 'Salary - January',           'TXN102', '2026-01-05 09:00:00', 4500.00),
(5,  200.00, 'debit',  'Utility Bill',               'TXN103', '2026-01-08 11:00:00', 4300.00),
(5,  350.00, 'debit',  'Supermarket Shopping',       'TXN104', '2026-01-12 14:00:00', 3950.00),
(5, 1500.00, 'credit', 'Salary - February',          'TXN105', '2026-02-05 09:00:00', 5450.00),
(5,  120.00, 'debit',  'Internet Subscription',      'TXN106', '2026-02-08 10:30:00', 5330.00),
(5,  400.00, 'debit',  'Clothing Purchase',          'TXN107', '2026-02-15 16:00:00', 4930.00),
(5,  500.00, 'credit', 'Freelance Work',             'TXN108', '2026-02-20 12:00:00', 5430.00),
(5, 1500.00, 'credit', 'Salary - March',             'TXN109', '2026-03-05 09:00:00', 6930.00),
(5,  175.00, 'debit',  'Phone Bill',                 'TXN110', '2026-03-07 09:30:00', 6755.00),
(5,  600.00, 'debit',  'Restaurant & Entertainment', 'TXN111', '2026-03-14 20:00:00', 6155.00),
(5, 1000.00, 'credit', 'Bonus Payment',              'TXN112', '2026-03-25 11:00:00', 7155.00),
(5, 1500.00, 'credit', 'Salary - April',             'TXN113', '2026-04-05 09:00:00', 8655.00),
(5,  300.00, 'debit',  'Gym Membership Annual',      'TXN114', '2026-04-06 10:00:00', 8355.00),
(5,  250.00, 'debit',  'Online Shopping',            'TXN115', '2026-04-10 13:00:00', 8105.00),
(5,  155.00, 'debit',  'Taxi / Ride Share',          'TXN116', '2026-04-14 19:00:00', 7950.00),
(5, 2000.00, 'credit', 'Investment Return',          'TXN117', '2026-04-16 10:00:00', 9950.00),
(5,  800.00, 'debit',  'Hotel Stay',                 'TXN118', '2026-04-18 12:00:00', 9150.00),
(5, 3000.00, 'credit', 'Property Rental Income',    'TXN119', '2026-04-20 09:00:00', 12150.00),
(5,  150.00, 'debit',  'Streaming Services Bundle', 'TXN120', '2026-04-22 08:00:00', 12000.00);

-- =====================================================
-- Transactions - Charlie checking (account_id = 6)
-- 20 transactions
-- =====================================================
INSERT IGNORE INTO transactions (account_id, amount, type, description, reference_number, date, balance_after) VALUES
(6, 5000.00, 'credit', 'Opening Deposit',           'TXN201', '2026-01-01 09:00:00',  5000.00),
(6, 2500.00, 'credit', 'Salary - January',          'TXN202', '2026-01-05 09:00:00',  7500.00),
(6,  450.00, 'debit',  'Rent Payment',              'TXN203', '2026-01-07 10:00:00',  7050.00),
(6,  200.00, 'debit',  'Grocery Store',             'TXN204', '2026-01-10 14:00:00',  6850.00),
(6, 2500.00, 'credit', 'Salary - February',         'TXN205', '2026-02-05 09:00:00',  9350.00),
(6,  450.00, 'debit',  'Rent Payment',              'TXN206', '2026-02-07 10:00:00',  8900.00),
(6,  320.00, 'debit',  'Electronics Purchase',      'TXN207', '2026-02-12 15:00:00',  8580.00),
(6,  800.00, 'credit', 'Side Business Income',      'TXN208', '2026-02-18 11:00:00',  9380.00),
(6, 2500.00, 'credit', 'Salary - March',            'TXN209', '2026-03-05 09:00:00', 11880.00),
(6,  450.00, 'debit',  'Rent Payment',              'TXN210', '2026-03-07 10:00:00', 11430.00),
(6,  190.00, 'debit',  'Insurance Premium',         'TXN211', '2026-03-10 09:00:00', 11240.00),
(6,  500.00, 'debit',  'Flight Tickets',            'TXN212', '2026-03-15 13:00:00', 10740.00),
(6, 2500.00, 'credit', 'Salary - April',            'TXN213', '2026-04-05 09:00:00', 13240.00),
(6,  450.00, 'debit',  'Rent Payment',              'TXN214', '2026-04-07 10:00:00', 12790.00),
(6, 1200.00, 'credit', 'Consulting Fee',            'TXN215', '2026-04-09 11:00:00', 13990.00),
(6,  680.00, 'debit',  'Car Service',               'TXN216', '2026-04-11 14:00:00', 13310.00),
(6,  210.00, 'debit',  'Medical Expenses',          'TXN217', '2026-04-14 10:30:00', 13100.00),
(6, 1500.00, 'credit', 'Project Bonus',             'TXN218', '2026-04-17 09:00:00', 14600.00),
(6, 3000.00, 'credit', 'Freelance Contract',        'TXN219', '2026-04-20 12:00:00', 17600.00),
(6, 7800.00, 'debit',  'Down Payment - FD Opening', 'TXN220', '2026-04-22 10:00:00',  9800.50);

-- =====================================================
-- Loans
-- =====================================================
INSERT IGNORE INTO loans (user_id, account_id, loan_type, principal, interest_rate, term_months, monthly_payment, outstanding, disbursed_at, due_date, status) VALUES
(1, 1, 'home',      150000.00, 6.50, 240, 1118.08, 148200.00, '2025-01-15', '2045-01-15', 'active'),
(2, 3, 'auto',       25000.00, 7.25,  60,  496.76,  22000.00, '2025-06-01', '2030-06-01', 'active'),
(4, 5, 'personal',   10000.00, 9.00,  36,  317.97,   8500.00, '2026-01-10', '2029-01-10', 'active'),
(5, 6, 'education',  30000.00, 5.50,  60,  573.14,  28000.00, '2026-02-01', '2031-02-01', 'active');

-- =====================================================
-- Fixed Deposits
-- =====================================================
INSERT IGNORE INTO fixed_deposits (user_id, account_id, fd_number, principal, interest_rate, term_months, maturity_amount, start_date, maturity_date, auto_renew, status) VALUES
(3, 4, 'FD3001001', 5000.00, 5.00, 12, 5250.00, '2025-04-01', '2026-04-01', TRUE,  'matured'),
(4, 5, 'FD4001001', 8000.00, 5.50, 24, 8907.20, '2026-01-15', '2028-01-15', FALSE, 'active'),
(5, 7, 'FD5001001', 7800.00, 6.00, 36, 9321.40, '2026-04-22', '2029-04-22', TRUE,  'active');

-- =====================================================
-- Pawning
-- =====================================================
INSERT IGNORE INTO pawning (user_id, account_id, ticket_number, item_description, item_category, appraised_value, loan_amount, interest_rate, pledged_at, due_date, outstanding, status) VALUES
(1, 2, 'PWN1001001', '22K Gold Necklace 25g',    'gold',        1200.00,  900.00, 2.50, '2026-03-01', '2026-06-01',  900.00, 'active'),
(2, 3, 'PWN2001001', 'MacBook Pro 14-inch 2024',  'electronics', 2000.00, 1500.00, 3.00, '2026-02-15', '2026-05-15',  750.00, 'active'),
(3, 4, 'PWN3001001', 'Honda Civic 2020',           'vehicle',    15000.00, 8000.00, 2.00, '2026-01-10', '2026-07-10', 8000.00, 'active'),
(4, 5, 'PWN4001001', '18K Gold Ring Set',          'gold',         800.00,  550.00, 2.50, '2026-04-01', '2026-07-01',  550.00, 'active');

