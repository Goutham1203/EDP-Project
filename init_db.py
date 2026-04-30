import mysql.connector
from mysql.connector import Error

def init_db():
    try:
        # Connect without database first
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Goutham@.123'
        )
        cursor = conn.cursor()

        # Read sql file
        with open('db_setup.sql', 'r') as file:
            sql_script = file.read()
        
        # Execute script
        for statement in sql_script.split(';'):
            if statement.strip():
                cursor.execute(statement)
        
        conn.commit()
        print("Database initialized successfully.")
    except Error as e:
        print(f"Error initializing database: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    init_db()
