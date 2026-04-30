from database import db

def migrate():
    # Add start_time and end_time to system_state
    try:
        db.execute_query("ALTER TABLE system_state ADD COLUMN start_time DATETIME DEFAULT NULL", commit=True)
        print("Added start_time")
    except Exception as e:
        print(e)
        
    try:
        db.execute_query("ALTER TABLE system_state ADD COLUMN end_time DATETIME DEFAULT NULL", commit=True)
        print("Added end_time")
    except Exception as e:
        print(e)

if __name__ == '__main__':
    migrate()
