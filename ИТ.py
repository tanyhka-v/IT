import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from PIL import Image, ImageTk   # для отображения аватаров
from io import BytesIO

# ------------------ Работа с избранным ------------------
FAVORITES_FILE = "favorites.json"

def load_favorites():
    if os.path.exists(FAVORITES_FILE):
        with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_favorites(favorites):
    with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
        json.dump(favorites, f, indent=2)

# ------------------ GitHub API ------------------
GITHUB_API_SEARCH = "https://api.github.com/search/users"

def search_users(query):
    """Возвращает список найденных пользователей или None при ошибке"""
    params = {"q": query, "per_page": 20}
    try:
        response = requests.get(GITHUB_API_SEARCH, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("items", [])
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Ошибка API", f"Не удалось выполнить поиск:\n{e}")
        return None

# ------------------ GUI приложение ------------------
class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("800x600")
        self.favorites = load_favorites()  # список логинов

        # Поле ввода
        tk.Label(root, text="Введите имя пользователя GitHub:").pack(pady=5)
        self.entry = tk.Entry(root, width=50)
        self.entry.pack(pady=5)
        self.entry.bind("<Return>", lambda e: self.search())

        # Кнопка поиска
        tk.Button(root, text="Поиск", command=self.search).pack(pady=5)

        # Таблица результатов
        columns = ("Логин", "Аватар", "Ссылка", "Действие")
        self.tree = ttk.Treeview(root, columns=columns, show="headings", height=15)
        self.tree.heading("Логин", text="Логин")
        self.tree.heading("Аватар", text="Аватар (ID)")
        self.tree.heading("Ссылка", text="Профиль")
        self.tree.heading("Действие", text="")
        self.tree.column("Логин", width=150)
        self.tree.column("Аватар", width=80)
        self.tree.column("Ссылка", width=300)
        self.tree.column("Действие", width=100)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Кнопка показать избранное
        tk.Button(root, text="Показать избранное", command=self.show_favorites).pack(pady=5)

        # Словарь для хранения кнопок внутри строк (логин -> кнопка)
        self.buttons = {}

        # Привязываем клик по строке для открытия профиля
        self.tree.bind("<Double-1>", self.open_profile)

    def search(self):
        query = self.entry.get().strip()
        if not query:
            messagebox.showwarning("Пустой запрос", "Поле поиска не должно быть пустым!")
            return

        users = search_users(query)
        if users is None:
            return
        self.display_results(users)

    def display_results(self, users):
        # Очищаем таблицу
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.buttons.clear()

        for user in users:
            login = user["login"]
            avatar_url = user["avatar_url"]
            profile_url = user["html_url"]

            # Добавляем строку
            item_id = self.tree.insert("", tk.END, values=(login, "Загрузка...", profile_url, ""))

            # Асинхронно загружаем аватар (для простоты используем after)
            self.load_avatar(avatar_url, item_id)

            # Кнопка "В избранное" / "Удалить"
            if login in self.favorites:
                btn_text = "Удалить"
                cmd = lambda l=login: self.remove_from_favorites(l)
            else:
                btn_text = "В избранное"
                cmd = lambda l=login: self.add_to_favorites(l)

            btn = tk.Button(self.tree, text=btn_text, command=cmd)
            self.tree.set(item_id, "Действие", "")
            self.tree.update_idletasks()
            # Размещаем кнопку в столбце "Действие"
            self.tree.set(item_id, "Действие", btn_text)  # временно текст, потом заменим
            # Лучше использовать колонку для текста, но для кнопки нужен bind.
            # Вариант: хранить кнопку отдельно и менять текст.
            # Упростим – вместо кнопок будем использовать текст-ссылку и менять по клику.
            # Переделаем: в колонке "Действие" будет текст "⭐" или "★", клик по строке.
            # Так надёжнее.
        # Переделаем: сделаем клик по строке для добавления/удаления, а текст с эмодзи.
        self.refresh_favorite_indicators(users)

    def load_avatar(self, url, item_id):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            img_data = response.content
            img = Image.open(BytesIO(img_data))
            img = img.resize((40, 40), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            # Сохраняем ссылку, чтобы не удалил сборщик мусора
            if not hasattr(self, 'avatar_images'):
                self.avatar_images = {}
            self.avatar_images[item_id] = photo
            self.tree.set(item_id, "Аватар", "✅")  # просто индикатор
            # Можно добавить картинку, но в Treeview сложно. Упростим до текста.
            self.tree.set(item_id, "Аватар", "🖼️")
        except:
            self.tree.set(item_id, "Аватар", "❌")

    def refresh_favorite_indicators(self, users):
        for user in users:
            login = user["login"]
            # Найти строку с этим логином
            for item in self.tree.get_children():
                if self.tree.item(item, "values")[0] == login:
                    if login in self.favorites:
                        self.tree.set(item, "Действие", "★ Удалить")
                    else:
                        self.tree.set(item, "Действие", "☆ Добавить")
                    break

    def add_to_favorites(self, login):
        if login not in self.favorites:
            self.favorites.append(login)
            save_favorites(self.favorites)
            messagebox.showinfo("Избранное", f"Пользователь {login} добавлен в избранное.")
            self.update_favorite_display(login, True)

    def remove_from_favorites(self, login):
        if login in self.favorites:
            self.favorites.remove(login)
            save_favorites(self.favorites)
            messagebox.showinfo("Избранное", f"Пользователь {login} удалён из избранного.")
            self.update_favorite_display(login, False)

    def update_favorite_display(self, login, is_favorite):
        for item in self.tree.get_children():
            if self.tree.item(item, "values")[0] == login:
                if is_favorite:
                    self.tree.set(item, "Действие", "★ Удалить")
                else:
                    self.tree.set(item, "Действие", "☆ Добавить")
                break

    def show_favorites(self):
        if not self.favorites:
            messagebox.showinfo("Избранное", "Список избранных пользователей пуст.")
            return
        # Делаем запрос по каждому пользователю, чтобы показать детали
        favorites_data = []
        for login in self.favorites:
            url = f"https://api.github.com/users/{login}"
            try:
                resp = requests.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    favorites_data.append(data)
                else:
                    favorites_data.append({"login": login, "html_url": "#", "avatar_url": ""})
            except:
                favorites_data.append({"login": login, "html_url": "#", "avatar_url": ""})
        self.display_results(favorites_data)

    def open_profile(self, event):
        """Открыть профиль по двойному клику"""
        item = self.tree.selection()[0]
        login = self.tree.item(item, "values")[0]
        profile_url = self.tree.item(item, "values")[2]
        import webbrowser
        webbrowser.open(profile_url)

if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()