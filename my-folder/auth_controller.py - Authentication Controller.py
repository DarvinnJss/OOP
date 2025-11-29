import sqlite3
from db import Database
from models import User

class AuthController:
    def __init__(self):
        self.db = Database()

    def login(self, username: str, password: str) -> tuple[bool, User, str]:
        try:
            conn = self.db.get_connection()
            cur = conn.cursor()
            
            cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", 
                    (username, password))
            user_data = cur.fetchone()
            
            if user_data:
                user = User(id=user_data[0], username=user_data[1], password=user_data[2])
                return True, user, "Login successful"
            else:
                return False, None, "Invalid username or password"
                
        except sqlite3.Error as e:
            return False, None, f"Database error: {str(e)}"
        finally:
            conn.close()

    def change_password(self, user_id: int, new_password: str) -> bool:
        try:
            conn = self.db.get_connection()
            cur = conn.cursor()
            
            cur.execute("UPDATE users SET password = ? WHERE id = ?", 
                    (new_password, user_id))
            conn.commit()
            return True
            
        except sqlite3.Error:
            return False
        finally:
            conn.close()