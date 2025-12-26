# gui/windows/employees_window.py
import customtkinter as ctk
from tkinter import messagebox, simpledialog
from database.db_manager import Database

class EmployeesWindow:
    def __init__(self, parent, db: Database):
        self.parent = parent
        self.db = db
        for w in parent.winfo_children():
            w.destroy()
        self._build()

    def _build(self):
        ctk.CTkLabel(self.parent, text="Сотрудники", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        frame = ctk.CTkFrame(self.parent)
        frame.pack(fill="both", expand=True, padx=12, pady=8)

        self.listbox = ctk.CTkTextbox(frame)
        self.listbox.pack(fill="both", expand=True, padx=8, pady=8)

        btn_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        btn_frame.pack(pady=8)
        ctk.CTkButton(btn_frame, text="Добавить сотрудника", command=self._create_user).pack(side="left", padx=6)
        ctk.CTkButton(btn_frame, text="Обновить", command=self._load).pack(side="left", padx=6)

        self._load()

    def _load(self):
        self.listbox.delete("1.0", "end")
        try:
            users = self.db.get_users()
            for u in users:
                self.listbox.insert("end", f"{u.get('id')} | {u.get('username')} | {u.get('full_name')} | role={u.get('role')}\n")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _create_user(self):
        uname = simpledialog.askstring("Новый пользователь", "Логин:", parent=self.parent)
        if not uname:
            return
        pwd = simpledialog.askstring("Пароль", "Пароль:", parent=self.parent, show="*")
        if not pwd:
            return
        role = simpledialog.askstring("Роль", "Роль (manager/employee):", parent=self.parent)
        role = role or "employee"
        try:
            self.db.add_user(username=uname, password=pwd, full_name="", phone="", role=role)
            messagebox.showinfo("Готово", "Пользователь создан")
            self._load()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
