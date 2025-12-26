# КОПИРУЙТЕ ВСЁ ОТСЮДА ↓↓↓
import customtkinter as ctk
from tkinter import messagebox, filedialog
from database.db_manager import db
import csv
from datetime import datetime, timedelta

class ManagerDashboard(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("📊 Dashboard (менеджер)")
        self.geometry("1200x800")
        self.resizable(True, True)
        
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # Заголовок
        title = ctk.CTkLabel(self, text="📊 Дашборд - Все записи", 
                           font=ctk.CTkFont(size=28, weight="bold"))
        title.pack(pady=20)

        # Фильтры
        filter_frame = ctk.CTkFrame(self)
        filter_frame.pack(fill="x", padx=20, pady=10)

        # Дата "с"
        ctk.CTkLabel(filter_frame, text="С:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
        self.from_date_var = ctk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
        from_date = ctk.CTkEntry(filter_frame, textvariable=self.from_date_var, width=120)
        from_date.pack(side="left", padx=5)

        # Дата "по"  
        ctk.CTkLabel(filter_frame, text="По:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
        self.to_date_var = ctk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        to_date = ctk.CTkEntry(filter_frame, textvariable=self.to_date_var, width=120)
        to_date.pack(side="left", padx=5)

        # Фильтр по мастеру
        ctk.CTkLabel(filter_frame, text="Мастер:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(30,10))
        self.master_filter_var = ctk.StringVar()
        self.master_combo = ctk.CTkComboBox(filter_frame, variable=self.master_filter_var, width=200)
        self.master_combo.pack(side="left", padx=5)
        self.load_masters_filter()

        # Кнопки фильтрации и экспорта
        filter_btn = ctk.CTkButton(filter_frame, text="🔄 Фильтровать", command=self.load_data,
                                 fg_color="blue", width=120)
        filter_btn.pack(side="right", padx=10)

        export_btn = ctk.CTkButton(filter_frame, text="📊 Экспорт CSV", command=self.export_csv,
                                 fg_color="green", width=120)
        export_btn.pack(side="right", padx=10)

        # Статистика
        stats_frame = ctk.CTkFrame(self)
        stats_frame.pack(fill="x", padx=20, pady=10)
        self.stats_label = ctk.CTkLabel(stats_frame, text="Загрузка...", 
                                      font=ctk.CTkFont(size=16, weight="bold"))
        self.stats_label.pack(pady=10)

        # Таблица
        table_frame = ctk.CTkScrollableFrame(self, height=500)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Создаем таблицу
        columns = ("ID", "Дата", "Услуга", "Мастер", "Кол-во", "Сумма", "Мастер %", "Босс %", "Описание")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)

        # Настраиваем колонки
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        self.tree.pack(fill="both", expand=True)

    def load_masters_filter(self):
        """Загрузить мастеров для фильтра"""
        users = db.get_users()
        masters = [(u['id'], f"{u['full_name']} ({u['username']})") for u in users]
        master_names = ["Все"] + [name for _, name in masters]
        self.master_combo.configure(values=master_names)

    def load_data(self):
        """Загрузить данные в таблицу"""
        try:
            # Парсим фильтры
            from_date = int(datetime.strptime(self.from_date_var.get(), "%Y-%m-%d").timestamp())
            to_date = int(datetime.strptime(self.to_date_var.get() + " 23:59:59", "%Y-%m-%d %H:%M:%S").timestamp())
            
            master_id = None
            if self.master_filter_var.get() != "Все":
                # Парсим мастера из текста "Имя (username)"
                username = self.master_filter_var.get().split('(')[-1].replace(')', '')
                user = db.authenticate(username, username)
                if user:
                    master_id = user['id']

            # Получаем данные
            records = db.get_daily_records(from_date, to_date, master_id)
            
            # Очищаем таблицу
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Заполняем таблицу
            total_sum = 0
            for record in records:
                date_str = datetime.fromtimestamp(record['date_ts']).strftime("%d.%m.%Y")
                master_name = "Неизвестно"
                if record['master_id']:
                    master = next((u for u in db.get_users() if u['id'] == record['master_id']), None)
                    master_name = master['full_name'] if master else "Неизвестно"
                
                self.tree.insert("", "end", values=(
                    record['id'],
                    date_str,
                    record['service_name'],
                    master_name,
                    record['orders_count'],
                    f"{record['total_amount']:.0f} ₸",
                    f"{record['master_income']:.0f} ₸",
                    f"{record['boss_income']:.0f} ₸",
                    record['description'] or ""
                ))
                
                total_sum += record['total_amount']
            
            # Обновляем статистику
            count = len(records)
            self.stats_label.configure(text=f"📈 Найдено записей: {count} | Общая сумма: {total_sum:.0f} ₸")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {str(e)}")

    def export_csv(self):
        """Экспорт в CSV"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialname=f"barber_report_{datetime.now().strftime('%Y%m%d')}.csv"
            )
            
            if not filename:
                return
            
            from_date = int(datetime.strptime(self.from_date_var.get(), "%Y-%m-%d").timestamp())
            to_date = int(datetime.strptime(self.to_date_var.get() + " 23:59:59", "%Y-%m-%d %H:%M:%S").timestamp())
            
            master_id = None
            if self.master_filter_var.get() != "Все":
                username = self.master_filter_var.get().split('(')[-1].replace(')', '')
                user = db.authenticate(username, username)
                if user:
                    master_id = user['id']
            
            records = db.get_daily_records(from_date, to_date, master_id)
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['ID', 'Дата', 'Услуга', 'Мастер', 'Количество', 'Сумма', 
                            'Мастер_доход', 'Босс_доход', 'Описание']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                total_sum = 0
                for record in records:
                    date_str = datetime.fromtimestamp(record['date_ts']).strftime("%d.%m.%Y %H:%M")
                    master_name = "Неизвестно"
                    if record['master_id']:
                        master = next((u for u in db.get_users() if u['id'] == record['master_id']), None)
                        master_name = master['full_name'] if master else "Неизвестно"
                    
                    writer.writerow({
                        'ID': record['id'],
                        'Дата': date_str,
                        'Услуга': record['service_name'],
                        'Мастер': master_name,
                        'Количество': record['orders_count'],
                        'Сумма': record['total_amount'],
                        'Мастер_доход': record['master_income'],
                        'Босс_доход': record['boss_income'],
                        'Описание': record['description'] or ''
                    })
                    total_sum += record['total_amount']
            
            messagebox.showinfo("Успех", f"✅ CSV сохранён: {filename}\nЗаписей: {len(records)}\nСумма: {total_sum:.0f} ₸")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать: {str(e)}")
