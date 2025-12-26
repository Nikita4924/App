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