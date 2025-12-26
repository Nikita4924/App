# gui/windows/base_window.py
from typing import Optional
from database.db_manager import Database

class BaseWindow:
    def __init__(self, db_path: Optional[str] = None, db: Optional[Database] = None):
        if db is not None:
            self.db = db
        else:
            self.db = Database(db_path or "database/database.sqlite")
