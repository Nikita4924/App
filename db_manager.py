from typing import Any, Dict, List, Optional, Tuple
import sqlite3
import time
import os

DEFAULT_DB_PATH = os.path.join("database", "database.sqlite")


def safe_int(x: Any, default: int = 0) -> int:
    try:
        if x is None:
            return default
        return int(x)
    except Exception:
        return default


def safe_float(x: Any, default: float = 0.0) -> float:
    try:
        if x is None:
            return default
        return float(x)
    except Exception:
        return default


def safe_str(x: Any, default: str = "") -> str:
    try:
        if x is None:
            return default
        return str(x)
    except Exception:
        return default


class Database:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path if db_path else DEFAULT_DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, timeout=30, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._ensure_schema()

    # ---------- low-level ----------
    def _exec(self, sql: str, params: Tuple = (), commit: bool = False) -> sqlite3.Cursor:
        cur = self.conn.cursor()
        try:
            cur.execute(sql, params)
            if commit:
                self.conn.commit()
        except sqlite3.OperationalError as e:
            # Provide helpful message during development but re-raise for fatal cases
            raise
        return cur

    # ---------- schema & migration ----------
    def _ensure_schema(self) -> None:
        """
        РЎРѕР·РґР°С‘С‚ С‚Р°Р±Р»РёС†С‹, РµСЃР»Рё РёС… РЅРµС‚, Рё РІС‹РїРѕР»РЅСЏРµС‚ РїСЂРѕСЃС‚С‹Рµ РјРёРіСЂР°С†РёРё
        (РґРѕР±Р°РІР»РµРЅРёРµ РєРѕР»РѕРЅРѕРє РїСЂРё РЅРµРѕР±С…РѕРґРёРјРѕСЃС‚Рё).
        """
        # РЎРѕР·РґР°С‘Рј С‚Р°Р±Р»РёС†С‹ РµСЃР»Рё РЅРµ СЃСѓС‰РµСЃС‚РІСѓСЋС‚
        self._exec(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                phone TEXT,
                full_name TEXT,
                role TEXT DEFAULT 'user',
                created_ts INTEGER
            );
            """,
            (),
            commit=True,
        )

        self._exec(
            """
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                price REAL DEFAULT 0.0,
                boss_percent INTEGER DEFAULT 0,
                boss_fixed_amount REAL DEFAULT 0.0
            );
            """,
            (),
            commit=True,
        )

        self._exec(
            """
            CREATE TABLE IF NOT EXISTS daily_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_ts INTEGER,
                service_id INTEGER,
                service_name TEXT,
                orders_count INTEGER DEFAULT 0,
                total_income REAL DEFAULT 0.0,
                total_amount REAL DEFAULT 0.0,
                master_id INTEGER,
                master_income REAL DEFAULT 0.0,
                boss_income REAL DEFAULT 0.0,
                kaspi REAL DEFAULT 0.0,
                description TEXT
            );
            """,
            (),
            commit=True,
        )

        self._exec(
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            );
            """,
            (),
            commit=True,
        )

        # РџСЂРѕСЃС‚Р°СЏ РјРёРіСЂР°С†РёСЏ: СѓР±РµРґРёРјСЃСЏ, С‡С‚Рѕ СЃС‚РѕР»Р±С†С‹ РїСЂРёСЃСѓС‚СЃС‚РІСѓСЋС‚ (РґР»СЏ СЃС‚Р°СЂС‹С… Р‘Р”)
        self._migrate_add_column_if_missing("users", "role", "TEXT DEFAULT 'user'")
        self._migrate_add_column_if_missing("users", "created_ts", "INTEGER")
        self._migrate_add_column_if_missing("services", "boss_percent", "INTEGER DEFAULT 0")
        self._migrate_add_column_if_missing("services", "boss_fixed_amount", "REAL DEFAULT 0.0")
        # daily_records columns already included above; if older DB lacks some, add them
        self._migrate_add_column_if_missing("daily_records", "kaspi", "REAL DEFAULT 0.0")
        self._migrate_add_column_if_missing("daily_records", "description", "TEXT")

        # Ensure there's at least one admin (demo) if table is empty
        if self.get_admin_count() == 0:
            admin_pw = "admin"  # РјРѕР¶РЅРѕ РёР·РјРµРЅРёС‚СЊ
            self.add_user(username="admin", phone="", full_name="Manager", password=admin_pw, is_admin=True)

    def _migrate_add_column_if_missing(self, table: str, column: str, definition: str) -> None:
        """
        Р•СЃР»Рё СЃС‚РѕР»Р±С†Р° column РІ С‚Р°Р±Р»РёС†Рµ table РЅРµС‚ вЂ” РґРѕР±Р°РІРёС‚СЊ РµРіРѕ СЃ definition (SQL).
        """
        cur = self._exec(f"PRAGMA table_info({table});")
        cols = [row["name"] for row in cur.fetchall()]
        if column not in cols:
            self._exec(f"ALTER TABLE {table} ADD COLUMN {column} {definition};", (), commit=True)

    # ---------- users ----------
    def add_user(
        self,
        username: str,
        phone: str = "",
        full_name: str = "",
        password: str = "",
        is_admin: bool = False,
    ) -> int:
        """
        Р’РѕР·РІСЂР°С‰Р°РµС‚ id РЅРѕРІРѕРіРѕ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ (int).
        РџСЂРё РєРѕРЅС„Р»РёРєС‚Рµ username РІРѕР·РІСЂР°С‰Р°РµС‚ СЃСѓС‰РµСЃС‚РІСѓСЋС‰РёР№ id.
        """
        username = safe_str(username)
        phone = safe_str(phone)
        full_name = safe_str(full_name)
        password = safe_str(password)
        role = "admin" if is_admin else "user"
        ts = int(time.time())

        try:
            cur = self._exec(
                "INSERT INTO users (username, password, phone, full_name, role, created_ts) VALUES (?, ?, ?, ?, ?, ?);",
                (username, password, phone, full_name, role, ts),
                commit=True,
            )
            return safe_int(cur.lastrowid, 0)
        except sqlite3.IntegrityError:
            # username exists вЂ” РІРµСЂРЅСѓС‚СЊ id СЃСѓС‰РµСЃС‚РІСѓСЋС‰РµРіРѕ
            existing = self.get_user_by_username(username)
            return existing["id"] if existing else 0

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        username = safe_str(username)
        cur = self._exec("SELECT * FROM users WHERE username = ? LIMIT 1;", (username,))
        row = cur.fetchone()
        return dict(row) if row else None

    def get_user_by_id(self, user_id: Any) -> Optional[Dict[str, Any]]:
        user_id = safe_int(user_id, default=0)
        cur = self._exec("SELECT * FROM users WHERE id = ? LIMIT 1;", (user_id,))
        row = cur.fetchone()
        return dict(row) if row else None

    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        username = safe_str(username)
        password = safe_str(password)
        cur = self._exec("SELECT * FROM users WHERE username = ? AND password = ? LIMIT 1;", (username, password))
        row = cur.fetchone()
        return dict(row) if row else None

    def get_admin_count(self) -> int:
        cur = self._exec("SELECT COUNT(1) as c FROM users WHERE role = 'admin';")
        row = cur.fetchone()
        return safe_int(row["c"] if row and "c" in row.keys() else 0, 0)

    # ---------- services ----------
    def add_service(self, name: str, price: Any = 0.0, boss_percent: Any = 0, boss_fixed_amount: Any = 0.0) -> int:
        name = safe_str(name)
        price = safe_float(price, 0.0)
        boss_percent = safe_int(boss_percent, 0)
        boss_fixed_amount = safe_float(boss_fixed_amount, 0.0)
        cur = self._exec(
            "INSERT INTO services (name, price, boss_percent, boss_fixed_amount) VALUES (?, ?, ?, ?);",
            (name, price, boss_percent, boss_fixed_amount),
            commit=True,
        )
        return safe_int(cur.lastrowid, 0)

    def delete_service(self, service_id: Any) -> bool:
        service_id = safe_int(service_id, 0)
        self._exec("DELETE FROM services WHERE id = ?;", (service_id,), commit=True)
        return True

    def get_services(self) -> List[Dict[str, Any]]:
        cur = self._exec("SELECT * FROM services ORDER BY name;")
        rows = cur.fetchall()
        return [dict(r) for r in rows] if rows else []

    def get_service_by_id(self, service_id: Any) -> Optional[Dict[str, Any]]:
        service_id = safe_int(service_id, 0)
        cur = self._exec("SELECT * FROM services WHERE id = ? LIMIT 1;", (service_id,))
        row = cur.fetchone()
        return dict(row) if row else None

    # ---------- daily records ----------
    def add_daily_record(
        self,
        date_ts: Optional[int],
        service_id: Optional[int],
        orders_count: Any,
        service_name: str,
        total_income: Any,
        total_amount: Any,
        master_id: Optional[int] = None,
        master_income: Any = 0.0,
        boss_income: Any = 0.0,
        kaspi: Any = 0.0,
        description: str = "",
    ) -> int:
        date_ts = safe_int(date_ts, int(time.time()))
        service_id = safe_int(service_id, 0)
        orders_count = safe_int(orders_count, 0)
        service_name = safe_str(service_name)
        total_income = safe_float(total_income, 0.0)
        total_amount = safe_float(total_amount, 0.0)
        master_id = safe_int(master_id, 0)
        master_income = safe_float(master_income, 0.0)
        boss_income = safe_float(boss_income, 0.0)
        kaspi = safe_float(kaspi, 0.0)
        description = safe_str(description)

        cur = self._exec(
            """
            INSERT INTO daily_records
                (date_ts, service_id, service_name, orders_count, total_income, total_amount,
                 master_id, master_income, boss_income, kaspi, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (date_ts, service_id, service_name, orders_count, total_income, total_amount, master_id, master_income, boss_income, kaspi, description),
            commit=True,
        )
        return safe_int(cur.lastrowid, 0)

    def get_daily_records(self, since_ts: Optional[int] = None) -> List[Dict[str, Any]]:
        if since_ts:
            cur = self._exec("SELECT * FROM daily_records WHERE date_ts >= ? ORDER BY date_ts DESC;", (safe_int(since_ts),))
        else:
            cur = self._exec("SELECT * FROM daily_records ORDER BY date_ts DESC;")
        rows = cur.fetchall()
        return [dict(r) for r in rows] if rows else []

    # ---------- reports ----------
    def get_monthly_report(self, month: int, year: int) -> List[Dict[str, Any]]:
        """
        Р’РѕР·РІСЂР°С‰Р°РµС‚ СЃРїРёСЃРѕРє Р·Р°РїРёСЃРµР№ (Р°РіСЂРµРіР°С‚) Р·Р° РјРµСЃСЏС†.
        month: 1..12, year: e.g. 2025
        """
        month = safe_int(month, 0)
        year = safe_int(year, 0)
        if month <= 0 or year <= 0:
            return []

        # РґРёР°РїР°Р·РѕРЅ unix ts
        import datetime
        start = int(datetime.datetime(year, month, 1).timestamp())
        if month == 12:
            end = int(datetime.datetime(year + 1, 1, 1).timestamp())
        else:
            end = int(datetime.datetime(year, month + 1, 1).timestamp())

        cur = self._exec(
            "SELECT service_name, SUM(orders_count) as orders, SUM(total_income) as income FROM daily_records WHERE date_ts >= ? AND date_ts < ? GROUP BY service_name;",
            (start, end),
        )
        rows = cur.fetchall()
        return [dict(r) for r in rows] if rows else []

    def get_monthly_payout(self, month: int, year: int) -> Tuple[float, int, List[Dict[str, Any]]]:
        """
        Р’РѕР·РІСЂР°С‰Р°РµС‚ (total_income, total_orders, rows)
        """
        rows = self.get_monthly_report(month, year)
        total_income = sum(safe_float(r.get("income", 0.0)) for r in rows)
        total_orders = sum(safe_int(r.get("orders", 0)) for r in rows)
        return (total_income, total_orders, rows)

    # ---------- settings ----------
    def set_setting(self, key: str, value: str) -> None:
        key = safe_str(key)
        value = safe_str(value)
        self._exec("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?);", (key, value), commit=True)

    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        key = safe_str(key)
        cur = self._exec("SELECT value FROM settings WHERE key = ? LIMIT 1;", (key,))
        row = cur.fetchone()
        return safe_str(row["value"], default if default is not None else "") if row else (default if default is not None else "")

    # ---------- utilities ----------
    def close(self) -> None:
        try:
            self.conn.close()
        except Exception:
            pass

    def __enter__(self) -> "Database":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


# gui/windows/add_daily_record_window.py
from typing import Optional, Callable
import os
import sqlite3
import time
import traceback

try:
    import customtkinter as ctk
except Exception:
    raise RuntimeError("РЈСЃС‚Р°РЅРѕРІРёС‚Рµ customtkinter: pip install customtkinter")

DB_DEFAULT = os.path.join("database", "database.sqlite")


def _conn(db_path=DB_DEFAULT):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


class AddDailyRecordWindow:
    def __init__(self, db_path: str = DB_DEFAULT, on_saved: Optional[Callable] = None):
        self.db_path = db_path
        self.conn = _conn(db_path)
        self.on_saved = on_saved

        self.win = ctk.CTkToplevel()
        self.win.title("Р”РѕР±Р°РІРёС‚СЊ Р·Р°РїРёСЃСЊ")
        self.win.geometry("420x360")
        self._build_ui()

    def _build_ui(self):
        frame = ctk.CTkFrame(self.win)
        frame.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(frame, text="РЎРµСЂРІРёСЃ (ID РёР»Рё РёРјСЏ)").pack(anchor="w")
        self.service_entry = ctk.CTkEntry(frame)
        self.service_entry.pack(fill="x", pady=(4, 8))

        ctk.CTkLabel(frame, text="РњР°СЃС‚РµСЂ (username РёР»Рё ID)").pack(anchor="w")
        self.user_entry = ctk.CTkEntry(frame)
        self.user_entry.pack(fill="x", pady=(4, 8))

        ctk.CTkLabel(frame, text="РљРѕР»РёС‡РµСЃС‚РІРѕ").pack(anchor="w")
        self.qty_entry = ctk.CTkEntry(frame)
        self.qty_entry.insert(0, "1")
        self.qty_entry.pack(fill="x", pady=(4, 8))

        ctk.CTkLabel(frame, text="РЎСѓРјРјР° (total)").pack(anchor="w")
        self.total_entry = ctk.CTkEntry(frame)
        self.total_entry.pack(fill="x", pady=(4, 8))

        ctk.CTkLabel(frame, text="РћРїРёСЃР°РЅРёРµ (РѕРїС†РёРѕРЅР°Р»СЊРЅРѕ)").pack(anchor="w")
        self.desc_entry = ctk.CTkEntry(frame)
        self.desc_entry.pack(fill="x", pady=(4, 8))

        btn = ctk.CTkButton(frame, text="РЎРѕС…СЂР°РЅРёС‚СЊ", command=self._on_save)
        btn.pack(pady=(8, 0))

        self.status = ctk.CTkLabel(frame, text="")
        self.status.pack(pady=(6, 0))

    def _resolve_service_id(self, val):
        cur = self.conn.cursor()
        try:
            v = int(val)
            cur.execute("SELECT id FROM services WHERE id = ?", (v,))
            r = cur.fetchone()
            if r:
                return r["id"]
        except Exception:
            pass
        # try by name
        cur.execute("SELECT id FROM services WHERE name = ?", (val,))
        r = cur.fetchone()
        return r["id"] if r else None

    def _resolve_user_id(self, val):
        cur = self.conn.cursor()
        try:
            v = int(val)
            cur.execute("SELECT id FROM users WHERE id = ?", (v,))
            r = cur.fetchone()
            if r:
                return r["id"]
        except Exception:
            pass
        cur.execute("SELECT id FROM users WHERE username = ?", (val,))
        r = cur.fetchone()
        return r["id"] if r else None

    def _on_save(self):
        service_val = self.service_entry.get().strip()
        user_val = self.user_entry.get().strip()
        qty = int(self.qty_entry.get() or 1)
        try:
            total = float(self.total_entry.get() or 0)
        except Exception:
            total = 0.0
        desc = self.desc_entry.get().strip()

        sid = self._resolve_service_id(service_val)
        uid = self._resolve_user_id(user_val)

        if sid is None:
            self.status.configure(text="РЎРµСЂРІРёСЃ РЅРµ РЅР°Р№РґРµРЅ. Р”РѕР±Р°РІСЊС‚Рµ СЃРµСЂРІРёСЃ РІ СЂР°Р·РґРµР»Рµ 'РЈСЃР»СѓРіРё'.")
            return
        if uid is None:
            self.status.configure(text="РњР°СЃС‚РµСЂ РЅРµ РЅР°Р№РґРµРЅ. Р”РѕР±Р°РІСЊС‚Рµ РјР°СЃС‚РµСЂР° РІ 'РЎРѕС‚СЂСѓРґРЅРёРєРё'.")
            return

        cur = self.conn.cursor()
        ts = int(time.time())
        cur.execute("""INSERT INTO daily_records (service_id, user_id, quantity, total, created_at, description)
                       VALUES (?, ?, ?, ?, ?, ?)""", (sid, uid, qty, total, ts, desc))
        self.conn.commit()
        self.status.configure(text="Р—Р°РїРёСЃСЊ СЃРѕС…СЂР°РЅРµРЅР°.")
        if self.on_saved:
            try:
                self.on_saved()
            except Exception:
                traceback.print_exc()
        # optionally close
        # self.win.destroy()