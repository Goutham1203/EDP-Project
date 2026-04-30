<<<<<<< HEAD
# Blockchain-Based Voting System

A secure, transparent, and immutable voting system built with Python, Flask, and MySQL. It simulates a blockchain ledger within a relational database to ensure the integrity of election results.

## Features

- **Role-based Access**: Separate dashboards for Admins and Voters.
- **Blockchain Verification**: Each vote is cryptographically hashed with the previous vote's hash, ensuring immutability.
- **Real-time Integrity Check**: The system verifies the blockchain before displaying results.
- **Premium Aesthetics**: Modern, glassmorphism UI built with pure CSS and HTML.
- **One User, One Vote**: Strict enforcement to prevent double voting.

## Requirements

- Python 3.8+
- MySQL Server

## Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Database**
   - Ensure your local MySQL server is running.
   - If your MySQL user is not `root` or has a password, update the credentials in `database.py` and `init_db.py`.
   - Run the initialization script to set up the schema and sample data:
     ```bash
     python init_db.py
     ```

3. **Run the Application**
   ```bash
   python app.py
   ```
   The application will start on `http://localhost:5000`.

## Test Accounts

The `init_db.py` script automatically creates the following test accounts:

**Admin Account:**
- Username: `admin`
- Password: `admin123`

**Voter Accounts:**
- Username: `voter1`
- Password: `voter123`
- Username: `voter2`
- Password: `voter123`

## Project Structure

- `app.py`: Flask routing and backend logic.
- `database.py`: MySQL connection handler.
- `blockchain.py`: Cryptographic hashing and verification module.
- `db_setup.sql`: Database schema and seed data.
- `templates/`: HTML files for the frontend.
- `static/`: CSS and JS assets.
- `architecture/`: Contains system flowcharts and ER diagrams.
=======
# EDP-Project
>>>>>>> 1ba6b5a7564bb44e7710f16319dcae45cedff04e
