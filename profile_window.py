# gui/windows/profile_window.py
import customtkinter as ctk
from tkinter import messagebox
from database.db_manager import Database

class ProfileWindow:
    def __init__(self, parent, user_id: int, on_done=None):
        self.parent = parent
        self.db = Database()
        self.user_id = user_id
        self.on_done = on_done

        self.win = ctk.CTkToplevel(self.parent)
        self.win.title("Профиль")
        self.win.geometry("420x320")
        try:
            self.win.transient(parent)
            self.win.grab_set()
        except Exception:
            pass

        u = self.db.get_user_by_id(self.user_id)
        if not u:
            messagebox.showerror("Ошибка", "Пользователь не найден")
            self.win.destroy()
            return
        uid, username, phash, is_admin, full_name, phone, email = u

        frame = ctk.CTkFrame(self.win)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        ctk.CTkLabel(frame, text="ФИО:").pack(anchor="w", padx=8)
        self.fullname_entry = ctk.CTkEntry(frame)
        self.fullname_entry.pack(fill="x", padx=8, pady=6)
        self.fullname_entry.insert(0, full_name or "")

        ctk.CTkLabel(frame, text="Телефон:").pack(anchor="w", padx=8)
        self.phone_entry = ctk.CTkEntry(frame)
        self.phone_entry.pack(fill="x", padx=8, pady=6)
        self.phone_entry.insert(0, phone or "")

        ctk.CTkLabel(frame, text="Email:").pack(anchor="w", padx=8)
        self.email_entry = ctk.CTkEntry(frame)
        self.email_entry.pack(fill="x", padx=8, pady=6)
        self.email_entry.insert(0, email or "")

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=8)
        ctk.CTkButton(btn_frame, text="Сохранить", command=self.save).pack(side="left", padx=6)
        ctk.CTkButton(btn_frame, text="Закрыть", command=self.close).pack(side="left", padx=6)

    def save(self):
        full_name = self.fullname_entry.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()
        try:
            self.db.cursor.execute("UPDATE users SET full_name=?, phone=?, email=? WHERE id=?", (full_name, phone, email, self.user_id))
            self.db.conn.commit()
            messagebox.showinfo("Готово", "Профиль обновлён")
            if callable(self.on_done):
                self.on_done()
        except Exception:
            messagebox.showerror("Ошибка", "Не удалось обновить профиль")

    def close(self):
        try:
            self.win.grab_release()
        except Exception:
            pass
        try:
            self.win.destroy()
        except Exception:
            pass
