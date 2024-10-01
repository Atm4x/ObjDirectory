from typing import Dict, Optional

# В реальном приложении это должно быть в базе данных
users = {
    "user1": {"password": "password1", "role": "user"},
    "admin": {"password": "admin_password", "role": "admin"}
}

def authenticate_user(username: str, password: str) -> Optional[Dict]:
    user = users.get(username)
    if user and user["password"] == password:
        return {"user_id": username, "role": user["role"]}
    return None