import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from io import BytesIO
from PIL import Image, ImageTk

FAVORITES_FILE = "favorites.json"

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("900x600")

        self.favorites = self.load_favorites()
        self.avatar_images = {}

        self.create_widgets()
        self.update_favorites_display()

    def create_widgets(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10, fill=tk.X)

        tk.Label(top_frame, text="Username:").pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(top_frame, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        search_btn = tk.Button(top_frame, text="Search", command=self.search_users)
        search_btn.pack(side=tk.LEFT, padx=5)

        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_frame = tk.LabelFrame(main_frame, text="Search Results")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.results_tree = ttk.Treeview(left_frame, columns=("avatar", "username"), show="headings", height=20)
        self.results_tree.heading("avatar", text="Avatar")
        self.results_tree.heading("username", text="Username")
        self.results_tree.column("avatar", width=60, anchor="center")
        self.results_tree.column("username", width=150)
        self.results_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_tree.configure(yscrollcommand=scrollbar.set)

        add_fav_btn = tk.Button(left_frame, text="Add to Favorites", command=self.add_to_favorites)
        add_fav_btn.pack(pady=5)

        right_frame = tk.LabelFrame(main_frame, text="Favorites")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.fav_tree = ttk.Treeview(right_frame, columns=("username",), show="headings", height=20)
        self.fav_tree.heading("username", text="Username")
        self.fav_tree.column("username", width=200)
        self.fav_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        fav_scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.fav_tree.yview)
        fav_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.fav_tree.configure(yscrollcommand=fav_scrollbar.set)

        remove_fav_btn = tk.Button(right_frame, text="Remove from Favorites", command=self.remove_from_favorites)
        remove_fav_btn.pack(pady=5)

        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(pady=10)

        save_btn = tk.Button(bottom_frame, text="Save Favorites to JSON", command=self.save_favorites_to_file)
        save_btn.pack(side=tk.LEFT, padx=5)

        load_btn = tk.Button(bottom_frame, text="Load Favorites from JSON", command=self.load_favorites_from_file)
        load_btn.pack(side=tk.LEFT, padx=5)

    def load_favorites(self):
        if os.path.exists(FAVORITES_FILE):
            with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except:
                    return []
        return []

    def save_favorites_to_file(self):
        with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
            json.dump(self.favorites, f, indent=4)
        messagebox.showinfo("Saved", f"Favorites saved to {FAVORITES_FILE}")

    def load_favorites_from_file(self):
        if os.path.exists(FAVORITES_FILE):
            with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
                try:
                    self.favorites = json.load(f)
                    self.update_favorites_display()
                    messagebox.showinfo("Loaded", "Favorites loaded from file")
                except:
                    messagebox.showerror("Error", "Invalid JSON file")
        else:
            messagebox.showwarning("Not found", f"{FAVORITES_FILE} does not exist")

    def search_users(self):
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Input Error", "Search field cannot be empty")
            return

        url = f"https://api.github.com/search/users?q={query}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                users = data.get("items", [])
                self.results_tree.delete(*self.results_tree.get_children())
                for user in users:
                    username = user["login"]
                    avatar_url = user["avatar_url"]
                    self.add_user_to_results(username, avatar_url)
            else:
                messagebox.showerror("API Error", f"Error {response.status_code}: {response.text}")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def add_user_to_results(self, username, avatar_url):
        try:
            img_data = requests.get(avatar_url).content
            pil_img = Image.open(BytesIO(img_data))
            pil_img = pil_img.resize((40, 40), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(pil_img)
            self.avatar_images[username] = photo
            self.results_tree.insert("", tk.END, values=(username,), image=photo, tags=(username,))
            self.results_tree.set(self.results_tree.get_children()[-1], "avatar", "")
            self.results_tree.set(self.results_tree.get_children()[-1], "username", username)
        except Exception:
            self.results_tree.insert("", tk.END, values=("", username))

    def add_to_favorites(self):
        selected = self.results_tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a user from search results")
            return
        item = selected[0]
        username = self.results_tree.item(item, "values")[1]
        if username not in self.favorites:
            self.favorites.append(username)
            self.update_favorites_display()
        else:
            messagebox.showinfo("Already exists", f"{username} is already in favorites")

    def remove_from_favorites(self):
        selected = self.fav_tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a user from favorites")
            return
        item = selected[0]
        username = self.fav_tree.item(item, "values")[0]
        self.favorites.remove(username)
        self.update_favorites_display()

    def update_favorites_display(self):
        self.fav_tree.delete(*self.fav_tree.get_children())
        for user in self.favorites:
            self.fav_tree.insert("", tk.END, values=(user,))

if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()
