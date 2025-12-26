# gui/windows/login_window.py
from typing import Optional, Any, Dict
from database.db_manager import Database

class LoginWindow:
    """
    Минимальное окно логина с run() чтобы main.py мог запускать процесс.
    """

    def __init__(self, db_path: str = "database/database.sqlite", user_id: Optional[Any] = None):
        self.db = Database(db_path)
        self.current_user = None
        if user_id is not None:
            try:
                self.current_user = self.db.get_user_by_id(user_id)
            except Exception:
                self.current_user = None

    def authenticate(self, username: str) -> Optional[Dict[str, Any]]:
        if not username:
            return None
        return self.db.get_user_by_username(username)

    def run(self) -> Optional[Dict[str, Any]]:
        """
        Простая последовательность 'run' — возвращает текущего пользователя, либо None.
        (Не GUI loop, только совместимость по сигнатуре для main.py).
        """
        return self.current_user
