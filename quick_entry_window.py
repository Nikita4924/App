# КОПИРУЙТЕ ВСЁ ОТСЮДА ↓↓↓
import customtkinter as ctk
from tkinter import messagebox, ttk
from database.db_manager import db
from datetime import datetime
import tkinter as tk

class QuickEntryWindow(ctk.CTkToplevel):
    def __init__(self, parent, current_user):
        super().__init__(parent)
        self.current_user = current_user
        self.title("Быстрая запись")
        self.geometry("500x650")
        self.resizable(False, False)
        
        # Центрируем окно
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        self.load_services()
        self.load_masters()

    def create_widgets(self):
        # Заголовок
        title_label = ctk.CTkLabel(self, text="📝 Быстрая запись", 
                                  font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)

        # Основной фрейм
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Дата
        date_frame = ctk.CTkFrame(main_frame)
        date_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(date_frame, text="📅 Дата:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        date_entry = ctk.CTkEntry(date_frame, textvariable=self.date_var, width=200, 
                                 placeholder_text="YYYY-MM-DD")
        date_entry.pack(anchor="w", padx=10, pady=5)

        # Услуга
        service_frame = ctk.CTkFrame(main_frame)
        service_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(service_frame, text="✂️ Услуга:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        self.service_var = ctk.StringVar()
        self.service_combo = ctk.CTkComboBox(service_frame, variable=self.service_var, 
                                           width=300, state="readonly")
        self.service_combo.pack(anchor="w", padx=10, pady=5)
        self.service_entry = ctk.CTkEntry(service_frame, placeholder_text="Или введите новую услугу")
        self.service_entry.pack(anchor="w", padx=10, pady=5, fill="x")

        # Мастер
        master_frame = ctk.CTkFrame(main_frame)
        master_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(master_frame, text="👨‍✂️ Мастер:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        self.master_var = ctk.StringVar()
        self.master_combo = ctk.CTkComboBox(master_frame, variable=self.master_var, 
                                          width=300, state="readonly")
        self.master_combo.pack(anchor="w", padx=10, pady=5)

        # Количество и сумма
        amounts_frame = ctk.CTkFrame(main_frame)
        amounts_frame.pack(fill="x", padx=20, pady=10)
        
        # Количество
        ctk.CTkLabel(amounts_frame, text="🔢 Количество:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        self.quantity_var = ctk.StringVar(value="1")
        quantity_entry = ctk.CTkEntry(amounts_frame, textvariable=self.quantity_var, width=100)
        quantity_entry.pack(anchor="w", padx=10, pady=5)

        # Сумма
        ctk.CTkLabel(amounts_frame, text="💰 Сумма (KZT):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(15,5))
        self.amount_var = ctk.StringVar(value="3000")
        amount_entry = ctk.CTkEntry(amounts_frame, textvariable=self.amount_var, width=150)
        amount_entry.pack(anchor="w", padx=10, pady=5)

        # Описание
        desc_frame = ctk.CTkFrame(main_frame)
        desc_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(desc_frame, text="📝 Описание:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        self.desc_var = ctk.StringVar()
        desc_entry = ctk.CTkEntry(desc_frame, textvariable=self.desc_var, height=40)
        desc_entry.pack(fill="x", padx=10, pady=5)

        # Кнопки
        btn_frame = ctk.CTkFrame(main_frame)
        btn_frame.pack(fill="x", padx=20, pady=20)
        
        save_btn = ctk.CTkButton(btn_frame, text="💾 Сохранить", command=self.save_record,
                               fg_color="green", hover_color="darkgreen", width=120, height=40)
        save_btn.pack(side="right", padx=10, pady=10)
        
        clear_btn = ctk.CTkButton(btn_frame, text="🔄 Очистить", command=self.clear_form,
                                fg_color="orange", hover_color="darkorange", width=120, height=40)
        clear_btn.pack(side="right", padx=10, pady=10)
        
        cancel_btn = ctk.CTkButton(btn_frame, text="❌ Отмена", command=self.destroy,
                                 fg_color="red", hover_color="darkred", width=120, height=40)
        cancel_btn.pack(side="right", padx=10, pady=10)

        # Статус
        self.status_label = ctk.CTkLabel(main_frame, text="", font=ctk.CTkFont(size=14))
        self.status_label.pack(pady=10)

    def load_services(self):
        """Загрузить список услуг"""
        services = db.get_services()
        service_names = [s['name'] for s in services]
        self.service_combo.configure(values=service_names)

    def load_masters(self):
        """Загрузить список мастеров"""
        users = db.get_users()
        masters = [u for u in users if u['role'] != 'admin']  # Только мастера
        master_names = [f"{u['full_name']} ({u['username']})" for u in masters]
        if not master_names:
            master_names = ["admin (admin)"]  # Если нет мастеров
        self.master_combo.configure(values=master_names)

    def clear_form(self):
        """Очистить форму"""
        self.service_var.set("")
        self.service_entry.delete(0, "end")
        self.master_var.set("")
        self.quantity_var.set("1")
        self.amount_var.set("3000")
        self.desc_var.set("")
        self.date_var.set(datetime.now().strftime("%Y-%m-%d"))
        self.status_label.configure(text="")

    def save_record(self):
        """Сохранить запись"""
        try:
            # Получаем данные
            service_name = self.service_var.get() or self.service_entry.get().strip()
            if not service_name:
                messagebox.showerror("Ошибка", "Введите название услуги!")
                return

            master_text = self.master_var.get()
            if not master_text:
                messagebox.showerror("Ошибка", "Выберите мастера!")
                return

            # Парсим мастера (имя (username))
            master_username = master_text.split('(')[-1].replace(')', '').strip()
            master = db.authenticate(master_username, master_username)  # Пока пароль = логину
            if not master:
                messagebox.showerror("Ошибка", "Мастер не найден!")
                return

            # Данные записи
            record_data = {
                'date_ts': int(datetime.strptime(self.date_var.get(), "%Y-%m-%d").timestamp()),
                'service_id': 1,  # Пока хардкод, потом найдем по имени
                'service_name': service_name,
                'orders_count': int(self.quantity_var.get()),
                'total_income': float(self.amount_var.get()),
                'total_amount': float(self.amount_var.get()),
                'master_id': master['id']
            }

            # Сохраняем
            record_id = db.add_daily_record(**record_data)
            
            self.status_label.configure(text="✅ Запись добавлена! ID: " + str(record_id), 
                                      text_color="green")
            
            # Очищаем форму для следующей записи
            self.after(2000, self.clear_form)
            
        except ValueError as e:
            self.status_label.configure(text="❌ Ошибка данных: " + str(e), text_color="red")
        except Exception as e:
            self.status_label.configure(text="❌ Ошибка: " + str(e), text_color="red")
