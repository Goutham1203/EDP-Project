from database import db
import bcrypt

def fix_admin():
    try:
        hashed = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        db.execute_query("UPDATE users SET password_hash = %s WHERE username = 'admin'", (hashed,), commit=True)
        print("Successfully updated admin password to admin123.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    fix_admin()
