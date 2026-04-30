import mysql.connector
from mysql.connector import Error

class Database:
    def __init__(self, host='localhost', user='root', password='Goutham@.123', database='voting_system'):
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database
        }
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.config)
            return self.connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None

    def execute_query(self, query, params=None, commit=False):
        conn = self.connect()
        if conn is None:
            return None
        
        try:
            cursor = conn.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if commit:
                conn.commit()
                result = cursor.lastrowid
            else:
                result = cursor.fetchall()
            
            cursor.close()
            conn.close()
            return result
        except Error as e:
            print(f"Error executing query: {e}")
            if conn.is_connected():
                conn.close()
            return None

    def execute_fetchone(self, query, params=None):
        conn = self.connect()
        if conn is None:
            return None
        
        try:
            cursor = conn.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result
        except Error as e:
            print(f"Error executing query: {e}")
            if conn.is_connected():
                conn.close()
            return None

db = Database()
