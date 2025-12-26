import customtkinter as ctk
from tkinter import messagebox
from database.db_manager import db
from gui.windows.main_window import MainWindow
from gui.windows.manager_dashboard import ManagerDashboard


class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Barber Dashboard — Вход")
        self.geometry("460x420")
        self.resizable(False, False)

        ctk.set_appearance_mode("System")      # Light/Dark от системы
        ctk.set_default_color_theme("blue")    # Можно заменить на свой json‑тему

        self._build()

    def _build(self):
        outer = ctk.CTkFrame(self, corner_radius=20)
        outer.pack(expand=True, fill="both", padx=30, pady=30)

        header = ctk.CTkLabel(
            outer,
            text="Barber Dashboard",
            font=ctk.CTkFont(size=26, weight="bold"),
        )
        header.pack(pady=(20, 5))

        subtitle = ctk.CTkLabel(
            outer,
            text="Вход для сотрудников и менеджера",
            font=ctk.CTkFont(size=13),
            text_color=("gray40", "gray70"),
        )
        subtitle.pack(pady=(0, 20))

        # ЛОГИН
        login_frame = ctk.CTkFrame(outer, fg_color="transparent")
        login_frame.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(login_frame, text="Логин", anchor="w").pack(anchor="w")
        self.username_entry = ctk.CTkEntry(
            login_frame,
            placeholder_text="manager / employee1",
            height=38,
        )
        self.username_entry.pack(fill="x", pady=(4, 8))

        # ПАРОЛЬ
        ctk.CTkLabel(login_frame, text="Пароль", anchor="w").pack(anchor="w")
        self.password_entry = ctk.CTkEntry(
            login_frame,
            placeholder_text="manager / 123",
            show="*",
            height=38,
        )
        self.password_entry.pack(fill="x", pady=(4, 8))

        # КНОПКА
        ctk.CTkButton(
            outer,
            text="Войти",
            command=self._login,
            height=42,
            corner_radius=10,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=(18, 10), padx=10, fill="x")

        # Подсказки по тестовым аккаунтам
        hint = ctk.CTkLabel(
            outer,
            text="👑 manager / manager\n👨‍💼 employee1 / 123\n👨‍💼 employee2 / 123",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray70"),
            justify="left",
        )
        hint.pack(pady=(5, 10))

    def _login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Ошибка", "Введите логин и пароль.")
            return

        user = db.authenticate(username, password)
        if not user:
            messagebox.showerror("Ошибка", "Неверный логин или пароль.")
            return

        self.destroy()
        if user["role"] == "manager":
            ManagerDashboard(user).mainloop()
        else:
            MainWindow(user).mainloop()
