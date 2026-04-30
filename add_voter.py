from database import db
import bcrypt

def update_db():
    try:
        hashed = bcrypt.hashpw('voter123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Check if voter exists
        existing = db.execute_fetchone("SELECT id FROM users WHERE username = 'voter'")
        if not existing:
            db.execute_query("INSERT INTO users (username, password_hash, role) VALUES ('voter', %s, 'voter')", (hashed,), commit=True)
            print("Successfully added 'voter'.")
        else:
            db.execute_query("UPDATE users SET password_hash = %s WHERE username = 'voter'", (hashed,), commit=True)
            print("Successfully updated 'voter'.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    update_db()
