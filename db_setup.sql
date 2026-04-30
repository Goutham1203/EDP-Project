-- Blockchain Voting System Database Setup

-- Create Database
CREATE DATABASE IF NOT EXISTS voting_system;
USE voting_system;

-- Drop tables if they exist to start fresh
DROP TABLE IF EXISTS votes;
DROP TABLE IF EXISTS candidates;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS system_state;

-- Table: users (Voters and Admins)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'voter') DEFAULT 'voter',
    has_voted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: candidates
CREATE TABLE candidates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    image_url VARCHAR(255)
);

-- Table: votes (The Blockchain Ledger)
CREATE TABLE votes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    voter_id INT NOT NULL,
    candidate_id INT NOT NULL,
    timestamp DATETIME NOT NULL,
    previous_hash VARCHAR(64) NOT NULL,
    hash VARCHAR(64) NOT NULL,
    FOREIGN KEY (voter_id) REFERENCES users(id),
    FOREIGN KEY (candidate_id) REFERENCES candidates(id)
);

-- Table: system_state (To manage election status)
CREATE TABLE system_state (
    id INT PRIMARY KEY,
    voting_active BOOLEAN DEFAULT FALSE
);

-- Initialize system state
INSERT INTO system_state (id, voting_active) VALUES (1, FALSE);

-- Insert Default Admin
-- Password is 'admin123' (bcrypt hash)
INSERT INTO users (username, password_hash, role) 
VALUES ('admin', '$2b$12$K1R2T2N.5R6/n1f1W4/Vw.hK0nE.gS9A.V9O8xJ9R8oE4E.R9y9vK', 'admin');

-- Insert some sample candidates
INSERT INTO candidates (name, description, image_url) VALUES 
('Alice Smith', 'Experienced leader focusing on technology and education.', 'https://ui-avatars.com/api/?name=Alice+Smith&background=random&size=150'),
('Bob Johnson', 'Advocate for environmental policies and sustainability.', 'https://ui-avatars.com/api/?name=Bob+Johnson&background=random&size=150'),
('Charlie Brown', 'Dedicated to economic reform and healthcare improvements.', 'https://ui-avatars.com/api/?name=Charlie+Brown&background=random&size=150');

-- Insert a Genesis Block into the votes table
-- The genesis block doesn't belong to any real voter/candidate, it just starts the chain.
-- We use a dummy voter_id=0, candidate_id=0 (we need to disable foreign key checks temporarily)
SET FOREIGN_KEY_CHECKS = 0;
INSERT INTO votes (id, voter_id, candidate_id, timestamp, previous_hash, hash) 
VALUES (1, 0, 0, '2024-01-01 00:00:00', '0000000000000000000000000000000000000000000000000000000000000000', 'a4c588f2195f00e998dc71f83b27b9db8d70df8d1a1b490f23d4ee1e1cd7e127');
SET FOREIGN_KEY_CHECKS = 1;

-- Insert Sample Voters (Password: 'voter123')
INSERT INTO users (username, password_hash, role) VALUES 
('voter', '$2b$12$K1R2T2N.5R6/n1f1W4/Vw.hK0nE.gS9A.V9O8xJ9R8oE4E.R9y9vK', 'voter'),
('voter1', '$2b$12$K1R2T2N.5R6/n1f1W4/Vw.hK0nE.gS9A.V9O8xJ9R8oE4E.R9y9vK', 'voter');
