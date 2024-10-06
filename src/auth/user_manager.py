import bcrypt
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, Optional, List
from config import config

class UserManager:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD
        )

    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cur.fetchone()
            
            if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                return {"user_id": user['id'], "role": user['role']}
        return None

    def create_user(self, username: str, password: str, email: str, role: str = 'user') -> bool:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (username, password_hash, email, role) VALUES (%s, %s, %s, %s)",
                    (username, hashed_password, email, role)
                )
                self.conn.commit()
            return True
        except psycopg2.Error:
            self.conn.rollback()
            return False

    def get_user_buckets(self, user_id: int) -> List[Dict]:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, name
                FROM buckets
                WHERE owner_id = %s
            """, (user_id,))
            return cur.fetchall()

    def check_bucket_ownership(self, user_id: int, bucket_name: str) -> bool:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id
                FROM buckets
                WHERE name = %s AND owner_id = %s
            """, (bucket_name, user_id))
            return cur.fetchone() is not None

    def __del__(self):
        self.conn.close()

user_manager = UserManager()