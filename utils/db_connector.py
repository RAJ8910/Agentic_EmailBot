import psycopg2
from psycopg2 import Error
import os
from dotenv import load_dotenv

load_dotenv()

class DBConnector:
    """Handles the connection to the PostgreSQL database."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBConnector, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self.conn = None
        self._initialized = True  
    
    def connect(self):
        if self.conn and not self.conn.closed:
            print("Already connected to the database.")
            return self.conn

        try:
            self.conn=psycopg2.connect(
                host=os.getenv("DB_HOST"),
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                port=os.getenv("DB_PORT")
            )
            print("Connection to the database established successfully.")
            return self.conn
        except Error as e:
            print(f"Error while connecting to PostgreSQL: {e}")
            self.conn = None
            raise 
        
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            print("PostgreSQL connection closed.")

    def execute_query(self, query, params=None, fetch_results=False, fetch_one=False):
        if not self.conn or self.conn.closed:
            print("Database not connected. Attempting to reconnect...")
            try:
                self.connect()
            except ValueError as ve: 
                print(f"Cannot connect: {ve}")
                return None
            if not self.conn or self.conn.closed:
                print("Failed to establish connection for query execution.")
                return None

        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            self.conn.commit()
            if fetch_results:
                if cursor.description:
                    return cursor.fetchall()
                else:
                    return []
            elif fetch_one:
                if cursor.description:
                    return cursor.fetchone()
                else:
                    return None
            else:
                
                return True
        except Error as e:
            print(f"Error while executing query: {e}")
            if self.conn:
                self.conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
