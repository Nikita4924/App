# gui/windows/master_details_window.py
from typing import Optional
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


class MasterDetailsWindow:
    def __init__(self, db_path: str = DB_DEFAULT, master_id: Optional[int] = None):
        self.db_path = db_path
        self.conn = _conn(db_path)
        self.master_id = master_id

        self.win = ctk.CTkToplevel()
        self.win.title("Р”РµС‚Р°Р»Рё РјР°СЃС‚РµСЂР°")
        self.win.geometry("520x380")
        self._build_ui()
        if master_id is not None:
            self._load_master(master_id)

    def _build_ui(self):
        frm = ctk.CTkFrame(self.win)
        frm.pack(fill="both", expand=True, padx=12, pady=12)

        self.info = ctk.CTkLabel(frm, text="Р’С‹Р±РµСЂРёС‚Рµ РјР°СЃС‚РµСЂР°", anchor="w")
        self.info.pack(fill="x")

        self.records_box = ctk.CTkTextbox(frm, height=220)
        self.records_box.pack(fill="both", expand=True, pady=(8, 8))

        btn_frame = ctk.CTkFrame(frm)
        btn_frame.pack(fill="x")
        self.pay_amount = ctk.CTkEntry(btn_frame, placeholder_text="РЎСѓРјРјР° РґР»СЏ РІС‹РїР»Р°С‚С‹")
        self.pay_amount.pack(side="left", fill="x", expand=True, padx=(0, 8))
        pay_btn = ctk.CTkButton(btn_frame, text="Р”РѕР±Р°РІРёС‚СЊ РІС‹РїР»Р°С‚Сѓ", command=self._add_payment)
        pay_btn.pack(side="left")

    def _load_master(self, master_id: int):
        cur = self.conn.cursor()
        cur.execute("SELECT id, username, full_name FROM users WHERE id = ?", (master_id,))
        u = cur.fetchone()
        if not u:
            self.info.configure(text="РњР°СЃС‚РµСЂ РЅРµ РЅР°Р№РґРµРЅ")
            return
        self.info.configure(text=f"{u['username']} вЂ” {u['full_name'] or ''}")
        cur.execute("SELECT amount, created_at, note FROM payments WHERE master_id = ? ORDER BY created_at DESC", (master_id,))
        rows = cur.fetchall()
        self.records_box.delete("0.0", "end")
        for r in rows:
            ts = time.strftime("%Y-%m-%d %H:%M", time.localtime(r["created_at"] or 0))
            self.records_box.insert("end", f"[{ts}] {r['amount']} вЂ” {r['note'] or ''}\n")

    def _add_payment(self):
        if not self.master_id:
            return
        try:
            amount = float(self.pay_amount.get() or 0)
        except Exception:
            amount = 0.0
        cur = self.conn.cursor()
        ts = int(time.time())
        cur.execute("INSERT INTO payments (master_id, amount, created_at, note) VALUES (?, ?, ?, ?)",
                    (self.master_id, amount, ts, "Р СѓС‡РЅР°СЏ РІС‹РїР»Р°С‚Р°"))
        self.conn.commit()
        self._load_master(self.master_id)