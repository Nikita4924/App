import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import Optional
import csv
from datetime import datetime

from database.db_manager import Database


class ExportWindow(ctk.CTkToplevel):
    """
    Окно экспорта операций в CSV.
    Позволяет сохранять выгрузку по:
    - диапазону дат
    - конкретному мастеру
    - всему списку услуг
    """

    def __init__(self, parent, preset_master_id: Optional[int] = None):
        super().__init__(parent)

        self.title("Экспорт CSV")
        self.geometry("520x260")
        self.resizable(False, False)

        self.db = Database()

        # Заголовок
        ctk.CTkLabel(
            self,
            text="Экспорт данных в CSV",
            font=("Arial", 16)
        ).pack(pady=10)

        # Форма
        form = ctk.CTkFrame(self)
        form.pack(fill="x", padx=12, pady=6)

        # Дата от
        ctk.CTkLabel(form, text="Начальная дата (YYYY-MM-DD):").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        self.start_entry = ctk.CTkEntry(form, width=160)
        self.start_entry.grid(row=0, column=1, sticky="w", padx=6, pady=6)

        # Дата до
        ctk.CTkLabel(form, text="Конечная дата (YYYY-MM-DD):").grid(row=1, column=0, sticky="w", padx=6, pady=6)
        self.end_entry = ctk.CTkEntry(form, width=160)
        self.end_entry.grid(row=1, column=1, sticky="w", padx=6, pady=6)

        # Фильтр по мастеру
        ctk.CTkLabel(form, text="Мастер (ID, опционально):").grid(row=2, column=0, sticky="w", padx=6, pady=6)
        self.master_entry = ctk.CTkEntry(form, width=160)
        self.master_entry.grid(row=2, column=1, sticky="w", padx=6, pady=6)

        if preset_master_id is not None:
            self.master_entry.insert(0, str(preset_master_id))

        # Кнопка экспорта
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=12)

        ctk.CTkButton(
            btn_frame,
            text="Выбрать файл и экспортировать",
            command=self.export_csv
        ).pack(padx=6, pady=6)

    # ================================ #
    #            EXPORT LOGIC          #
    # ================================ #

    def export_csv(self):
        """Сформировать SQL-запрос -> выгрузить в CSV."""
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
                messagebox.showerror("Ошибка", "ID мастера должен быть числом")
                return

        if where:
            query += " WHERE " + " AND ".join(where)

        query += " ORDER BY s.date ASC"

        # Выполняем SQL
        try:
            cur = self.db.cursor
            cur.execute(query, tuple(params))
            rows = cur.fetchall()
        except Exception as e:
            messagebox.showerror("Ошибка БД", f"Не удалось получить данные:\n{e}")
            return

        if not rows:
            if not messagebox.askyesno("Пусто", "Нет данных по выбранным фильтрам. Сохранить пустой CSV?"):
                return

        # Сохранение файла
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV файлы", "*.csv")],
            initialfile=f"barber_export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        )

        if not filepath:
            return

        # Записываем CSV
        try:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)

                writer.writerow([
                    "ID", "Дата", "Мастер", "Сумма",
                    "Доход мастера", "Доход менеджера", "Описание"
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

            messagebox.showinfo("Готово", f"CSV успешно сохранён:\n{filepath}")
            self.destroy()

        except Exception as e:
            messagebox.showerror("Ошибка записи", f"Не удалось сохранить файл:\n{e}")
