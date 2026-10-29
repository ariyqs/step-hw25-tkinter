"""
Домашнее задание №25 — Программы с интерфейсом (GUI)

Программа на tkinter делает запрос к https://jsonplaceholder.typicode.com
по выбранному ресурсу и id, показывает полученный объект
и сохраняет его в папку saved/ в формате JSON.
"""

import json
import os
import tkinter as tk
from tkinter import ttk, messagebox

import requests

BASE_URL = "https://jsonplaceholder.typicode.com"

# Ресурсы jsonplaceholder и максимальный id для каждого
RESOURCES = {
    "posts": 100,
    "comments": 500,
    "albums": 100,
    "photos": 5000,
    "todos": 200,
    "users": 10,
}

# Папка для сохранения — рядом с main.py
SAVE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("JSONPlaceholder Viewer")
        self.geometry("620x520")
        self.minsize(520, 420)

        self.current_data = None  # последний полученный объект
        self.current_resource = None
        self.current_id = None

        self.build_ui()

    # ---------- Интерфейс ----------
    def build_ui(self):
        # Заголовок
        tk.Label(self, text="JSONPlaceholder Viewer",
                 font=("Arial", 16, "bold")).pack(pady=(12, 4))
        tk.Label(self, text="Запрос объекта по id и сохранение в папку",
                 fg="gray").pack()

        # Строка ввода: ресурс + id + кнопка
        form = tk.Frame(self)
        form.pack(fill="x", padx=16, pady=12)

        tk.Label(form, text="Ресурс:").grid(row=0, column=0, sticky="w")
        self.resource_var = tk.StringVar(value="posts")
        self.resource_box = ttk.Combobox(form, textvariable=self.resource_var,
                                         values=list(RESOURCES), state="readonly",
                                         width=12)
        self.resource_box.grid(row=0, column=1, padx=(4, 16))

        tk.Label(form, text="ID:").grid(row=0, column=2, sticky="w")
        self.id_entry = tk.Entry(form, width=8)
        self.id_entry.insert(0, "1")
        self.id_entry.grid(row=0, column=3, padx=(4, 16))
        self.id_entry.bind("<Return>", lambda e: self.fetch())

        tk.Button(form, text="Получить", width=12,
                  command=self.fetch).grid(row=0, column=4)

        # Нижняя панель: кнопка сохранения + статус
        # (пакуем раньше текстового поля, чтобы она всегда была видна)
        bottom = tk.Frame(self)
        bottom.pack(side="bottom", fill="x", padx=16, pady=12)

        self.save_btn = tk.Button(bottom, text="Сохранить в папку", width=18,
                                  state="disabled", command=self.save)
        self.save_btn.pack(side="left")

        self.status = tk.Label(bottom, text="Введите id и нажмите «Получить»",
                               fg="gray", anchor="w")
        self.status.pack(side="left", padx=12, fill="x", expand=True)

        # Поле с результатом (занимает всё оставшееся место)
        result_frame = tk.Frame(self)
        result_frame.pack(fill="both", expand=True, padx=16)

        self.text = tk.Text(result_frame, font=("Consolas", 11), wrap="word",
                            height=12, state="disabled")
        scroll = tk.Scrollbar(result_frame, command=self.text.yview)
        self.text.configure(yscrollcommand=scroll.set)
        self.text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def show_text(self, content):
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self.text.configure(state="disabled")

    def set_status(self, msg, color="gray"):
        self.status.configure(text=msg, fg=color)

    # ---------- Логика ----------
    def fetch(self):
        resource = self.resource_var.get()
        raw_id = self.id_entry.get().strip()

        # Проверка ввода
        if not raw_id.isdigit() or int(raw_id) < 1:
            messagebox.showerror("Ошибка", "ID должен быть целым числом больше 0")
            return
        obj_id = int(raw_id)
        max_id = RESOURCES[resource]
        if obj_id > max_id:
            messagebox.showerror("Ошибка", f"Для «{resource}» id от 1 до {max_id}")
            return

        url = f"{BASE_URL}/{resource}/{obj_id}"
        self.set_status(f"Запрос: {url} ...")
        self.update_idletasks()

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            self.current_data = None
            self.save_btn.configure(state="disabled")
            self.show_text("")
            self.set_status("Ошибка запроса", "red")
            messagebox.showerror("Ошибка сети", str(e))
            return

        self.current_data = data
        self.current_resource = resource
        self.current_id = obj_id
        self.show_text(json.dumps(data, ensure_ascii=False, indent=4))
        self.save_btn.configure(state="normal")
        self.set_status(f"Получено: {resource}/{obj_id}", "green")

    def save(self):
        if self.current_data is None:
            return
        os.makedirs(SAVE_DIR, exist_ok=True)
        filename = f"{self.current_resource}_{self.current_id}.json"
        path = os.path.join(SAVE_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.current_data, f, ensure_ascii=False, indent=4)
        self.set_status(f"Сохранено: saved/{filename}", "green")
        messagebox.showinfo("Готово", f"Файл сохранён:\n{path}")


if __name__ == "__main__":
    App().mainloop()
