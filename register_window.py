# gui/windows/register_window.py
import customtkinter as ctk
from tkinter import messagebox
from database.db_manager import Database

class RegisterWindow:
    def __init__(self, parent, db: Database, on_registered=None):
        """
        parent: родительское окно (tk window)
        db: экземпляр Database
        on_registered: optional callback(user_dict) при успешной регистрации
        """
        self.parent = parent
        self.db = db
        self.on_registered = on_registered

        self.win = ctk.CTkToplevel(self.parent)
        self.win.title("Регистрация")
        self.win.geometry("420x380")
        try:
            self.win.transient(parent)
            self.win.grab_set()
        except Exception:
            pass

        self._build()

    def _build(self):
        frame = ctk.CTkFrame(self.win, corner_radius=12)
        frame.pack(expand=True, fill="both", padx=16, pady=16)

        ctk.CTkLabel(frame, text="Новая учётная запись", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(6,12))

        self.username = ctk.CTkEntry(frame, placeholder_text="Логин")
        self.username.pack(fill="x", pady=6)

        self.phone = ctk.CTkEntry(frame, placeholder_text="Телефон (опционально)")
        self.phone.pack(fill="x", pady=6)

        self.fullname = ctk.CTkEntry(frame, placeholder_text="ФИО (опционально)")
        self.fullname.pack(fill="x", pady=6)

        self.password = ctk.CTkEntry(frame, placeholder_text="Пароль", show="*")
        self.password.pack(fill="x", pady=6)

        # роль: менеджер или сотрудник
        self.role = ctk.CTkOptionMenu(frame, values=["employee", "manager"])
        self.role.set("employee")
        self.role.pack(pady=10)

        self.status = ctk.CTkLabel(frame, text="", text_color="red")
        self.status.pack()

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=8)

        ctk.CTkButton(btn_frame, text="Создать", command=self.create_user).pack(side="left", padx=(0,8))
        ctk.CTkButton(btn_frame, text="Закрыть", fg_color=None, command=self.close).pack(side="left")

    def create_user(self):
        uname = (self.username.get() or "").strip()
        pwd = (self.password.get() or "").strip()
        phone = (self.phone.get() or "").strip()
        fullname = (self.fullname.get() or "").strip()
        role = (self.role.get() or "employee")

        if not uname or not pwd:
            self.status.configure(text="Логин и пароль обязательны")
            return

        try:
            uid = self.db.add_user(username=uname, password=pwd, full_name=fullname, phone=phone, role=role)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать пользователя: {e}")
            return

        user = self.db.get_user_by_id(uid)
        messagebox.showinfo("Готово", "Пользователь создан")
        if callable(self.on_registered):
            self.on_registered(user)
        self.close()

    def close(self):
        try:
            self.win.grab_release()
        except Exception:
            pass
        try:
            self.win.destroy()
        except Exception:
            pass
