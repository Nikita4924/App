from typing import Any, Optional
from database.db_manager import Database, safe_float, safe_int

class AdjustBalanceWindow:
    """
    РЈС‚РёР»РёС‚Р°СЂРЅРѕРµ РѕРєРЅРѕ РґР»СЏ РєРѕСЂСЂРµРєС‚РёСЂРѕРІРѕРє Р±Р°Р»Р°РЅСЃР° / СЂСѓС‡РЅС‹С… С‚СЂР°РЅР·Р°РєС†РёР№.
    """

    def __init__(self, db_path: str = "database/database.sqlite"):
        self.db = Database(db_path)

    def adjust_balance(
        self,
        amount: Any,
        user_id: Optional[Any] = None,
        master_income: Any = 0.0,
        boss_income: Any = 0.0,
        description: str = ""
    ) -> int:
        """
        РЎРѕР·РґР°С‘С‚ Р·Р°РїРёСЃСЊ Рѕ РїР»Р°С‚РµР¶Рµ/РєРѕСЂСЂРµРєС†РёРё.
        amount, master_income, boss_income РјРѕРіСѓС‚ Р±С‹С‚СЊ СЃС‚СЂРѕРєР°РјРё/С‡РёСЃР»Р°РјРё.
        user_id РјРѕР¶РµС‚ Р±С‹С‚СЊ None РёР»Рё С‡РёСЃР»РѕРј/СЃС‚СЂРѕРєРѕР№.
        Р’РѕР·РІСЂР°С‰Р°РµС‚ id СЃРѕР·РґР°РЅРЅРѕР№ Р·Р°РїРёСЃРё (payments).
        """
        amt = safe_float(amount, 0.0)
        mid = safe_int(user_id, 0) if user_id is not None else 0
        master_inc = safe_float(master_income, 0.0)
        boss_inc = safe_float(boss_income, 0.0)
        # РЎРѕР±РёСЂР°РµРј РѕРїРёСЃР°РЅРёРµ
        desc = f"{description} | master_income={master_inc} boss_income={boss_inc}"
        return int(self.db.add_payment(master_id=mid, amount=amt, description=desc))


import customtkinter as ctk
from tkinter import messagebox
from database.db_manager import Database


class EmployeesWindow:
    def __init__(self, parent, db: Database):
        self.db = db
        self.parent = parent

        for w in parent.winfo_children():
            w.destroy()

        self._build()

    def _build(self):
        ctk.CTkLabel(
            self.parent,
            text="РЎРѕС‚СЂСѓРґРЅРёРєРё",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)

        self.listbox = ctk.CTkTextbox(self.parent)
        self.listbox.pack(expand=True, fill="both", padx=20, pady=10)

        self._load()

    def _load(self):
        self.listbox.delete("1.0", "end")
        users = self.db.get_users()
        for u in users:
            self.listbox.insert(
                "end",
                f"{u['id']} | {u['username']} | {u['full_name']}\n"
            )


import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import Optional
import csv
from datetime import datetime

from database.db_manager import Database


class ExportWindow(ctk.CTkToplevel):
    """
    РћРєРЅРѕ СЌРєСЃРїРѕСЂС‚Р° РѕРїРµСЂР°С†РёР№ РІ CSV.
    РџРѕР·РІРѕР»СЏРµС‚ СЃРѕС…СЂР°РЅСЏС‚СЊ РІС‹РіСЂСѓР·РєСѓ РїРѕ:
    - РґРёР°РїР°Р·РѕРЅСѓ РґР°С‚
    - РєРѕРЅРєСЂРµС‚РЅРѕРјСѓ РјР°СЃС‚РµСЂСѓ
    - РІСЃРµРјСѓ СЃРїРёСЃРєСѓ СѓСЃР»СѓРі
    """

    def __init__(self, parent, preset_master_id: Optional[int] = None):
        super().__init__(parent)

        self.title("РРєСЃРїРѕСЂС‚ CSV")
        self.geometry("520x260")
        self.resizable(False, False)

        self.db = Database()

        # Р—Р°РіРѕР»РѕРІРѕРє
        ctk.CTkLabel(
            self,
            text="РРєСЃРїРѕСЂС‚ РґР°РЅРЅС‹С… РІ CSV",
            font=("Arial", 16)
        ).pack(pady=10)

        # Р¤РѕСЂРјР°
        form = ctk.CTkFrame(self)
        form.pack(fill="x", padx=12, pady=6)

        # Р”Р°С‚Р° РѕС‚
        ctk.CTkLabel(form, text="РќР°С‡Р°Р»СЊРЅР°СЏ РґР°С‚Р° (YYYY-MM-DD):").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        self.start_entry = ctk.CTkEntry(form, width=160)
        self.start_entry.grid(row=0, column=1, sticky="w", padx=6, pady=6)

        # Р”Р°С‚Р° РґРѕ
        ctk.CTkLabel(form, text="РљРѕРЅРµС‡РЅР°СЏ РґР°С‚Р° (YYYY-MM-DD):").grid(row=1, column=0, sticky="w", padx=6, pady=6)
        self.end_entry = ctk.CTkEntry(form, width=160)
        self.end_entry.grid(row=1, column=1, sticky="w", padx=6, pady=6)

        # Р¤РёР»СЊС‚СЂ РїРѕ РјР°СЃС‚РµСЂСѓ
        ctk.CTkLabel(form, text="РњР°СЃС‚РµСЂ (ID, РѕРїС†РёРѕРЅР°Р»СЊРЅРѕ):").grid(row=2, column=0, sticky="w", padx=6, pady=6)
        self.master_entry = ctk.CTkEntry(form, width=160)
        self.master_entry.grid(row=2, column=1, sticky="w", padx=6, pady=6)

        if preset_master_id is not None:
            self.master_entry.insert(0, str(preset_master_id))

        # РљРЅРѕРїРєР° СЌРєСЃРїРѕСЂС‚Р°
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=12)

        ctk.CTkButton(
            btn_frame,
            text="Р’С‹Р±СЂР°С‚СЊ С„Р°Р№Р» Рё СЌРєСЃРїРѕСЂС‚РёСЂРѕРІР°С‚СЊ",
            command=self.export_csv
        ).pack(padx=6, pady=6)

    # ================================ #
    #            EXPORT LOGIC          #
    # ================================ #

    def export_csv(self):
        """РЎС„РѕСЂРјРёСЂРѕРІР°С‚СЊ SQL-Р·Р°РїСЂРѕСЃ -> РІС‹РіСЂСѓР·РёС‚СЊ РІ CSV."""
        start_date = self.start_entry.get().strip()
        end_date = self.end_entry.get().strip()
        master_id = self.master_entry.get().strip()

        query = """
        SELECT 
            s.id,
            s.date,
            u.username AS master_name,
            s.amount,
            s.master_income,
            s.boss_income,
            s.description
        FROM services s
        LEFT JOIN users u ON s.user_id = u.id
        """

        where = []
        params: list = []

        if start_date:
            where.append("date(s.date) >= date(?)")
            params.append(start_date)

        if end_date:
            where.append("date(s.date) <= date(?)")
            params.append(end_date)

        if master_id:
            try:
                params.append(int(master_id))
                where.append("s.user_id = ?")
            except ValueError:
                messagebox.showerror("РћС€РёР±РєР°", "ID РјР°СЃС‚РµСЂР° РґРѕР»Р¶РµРЅ Р±С‹С‚СЊ С‡РёСЃР»РѕРј")
                return

        if where:
            query += " WHERE " + " AND ".join(where)

        query += " ORDER BY s.date ASC"

        # Р’С‹РїРѕР»РЅСЏРµРј SQL
        try:
            cur = self.db.cursor
            cur.execute(query, tuple(params))
            rows = cur.fetchall()
        except Exception as e:
            messagebox.showerror("РћС€РёР±РєР° Р‘Р”", f"РќРµ СѓРґР°Р»РѕСЃСЊ РїРѕР»СѓС‡РёС‚СЊ РґР°РЅРЅС‹Рµ:\n{e}")
            return

        if not rows:
            if not messagebox.askyesno("РџСѓСЃС‚Рѕ", "РќРµС‚ РґР°РЅРЅС‹С… РїРѕ РІС‹Р±СЂР°РЅРЅС‹Рј С„РёР»СЊС‚СЂР°Рј. РЎРѕС…СЂР°РЅРёС‚СЊ РїСѓСЃС‚РѕР№ CSV?"):
                return

        # РЎРѕС…СЂР°РЅРµРЅРёРµ С„Р°Р№Р»Р°
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV С„Р°Р№Р»С‹", "*.csv")],
            initialfile=f"barber_export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        )

        if not filepath:
            return

        # Р—Р°РїРёСЃС‹РІР°РµРј CSV
        try:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)

                writer.writerow([
                    "ID", "Р”Р°С‚Р°", "РњР°СЃС‚РµСЂ", "РЎСѓРјРјР°",
                    "Р”РѕС…РѕРґ РјР°СЃС‚РµСЂР°", "Р”РѕС…РѕРґ РјРµРЅРµРґР¶РµСЂР°", "РћРїРёСЃР°РЅРёРµ"
                ])

                for r in rows:
                    try:
                        writer.writerow([
                            r["id"],
                            r["date"],
                            r["master_name"],
                            r["amount"],
                            r["master_income"],
                            r["boss_income"],
                            r["description"],
                        ])
                    except Exception:
                        writer.writerow(list(r))

            messagebox.showinfo("Р“РѕС‚РѕРІРѕ", f"CSV СѓСЃРїРµС€РЅРѕ СЃРѕС…СЂР°РЅС‘РЅ:\n{filepath}")
            self.destroy()

        except Exception as e:
            messagebox.showerror("РћС€РёР±РєР° Р·Р°РїРёСЃРё", f"РќРµ СѓРґР°Р»РѕСЃСЊ СЃРѕС…СЂР°РЅРёС‚СЊ С„Р°Р№Р»:\n{e}")


import customtkinter as ctk
from tkinter import messagebox

from database.db_manager import Database
from gui.windows.register_window import RegisterWindow


class LoginWindow:
    def __init__(self, db_path="database/database.sqlite"):
        self.db = Database(db_path)

        self.root = ctk.CTk()
        self.root.title("Barber App вЂ” Р’С…РѕРґ")
        self.root.geometry("380x360")
        self.root.resizable(False, False)

        self._build()

    def _build(self):
        frame = ctk.CTkFrame(self.root, corner_radius=14)
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(
            frame,
            text="Barber App",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(10, 5))

        ctk.CTkLabel(
            frame,
            text="Р’С…РѕРґ РІ СЃРёСЃС‚РµРјСѓ",
            font=ctk.CTkFont(size=14)
        ).pack(pady=(0, 20))

        self.username = ctk.CTkEntry(frame, placeholder_text="Р›РѕРіРёРЅ")
        self.username.pack(fill="x", pady=6)

        self.password = ctk.CTkEntry(frame, placeholder_text="РџР°СЂРѕР»СЊ", show="*")
        self.password.pack(fill="x", pady=6)

        ctk.CTkButton(
            frame,
            text="Р’РѕР№С‚Рё",
            command=self._login
        ).pack(pady=(20, 10), fill="x")

        ctk.CTkButton(
            frame,
            text="Р РµРіРёСЃС‚СЂР°С†РёСЏ",
            fg_color="gray",
            command=self._open_register
        ).pack(fill="x")

    # ===================== #
    #        ACTIONS        #
    # ===================== #

    def _login(self):
        username = self.username.get().strip()
        password = self.password.get().strip()

        if not username or not password:
            messagebox.showerror("РћС€РёР±РєР°", "Р’РІРµРґРёС‚Рµ Р»РѕРіРёРЅ Рё РїР°СЂРѕР»СЊ")
            return

        user = self.db.authenticate(username, password)
        if not user:
            messagebox.showerror("РћС€РёР±РєР°", "РќРµРІРµСЂРЅС‹Р№ Р»РѕРіРёРЅ РёР»Рё РїР°СЂРѕР»СЊ")
            return

        self._open_main(user)

    def _open_register(self):
        def after_register(user: dict | None):
            if user:
                self._open_main(user)

        RegisterWindow(
            parent=self.root,
            db=self.db,
            on_success=after_register
        )

    def _open_main(self, user: dict):
        self.root.destroy()
        from gui.windows.main_window import MainWindow
        MainWindow(user).run()

    def run(self):

        self.root.mainloop()