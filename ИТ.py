import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

EXPENSES_FILE = "expenses.json"

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("900x600")

        self.expenses = self.load_expenses()
        self.categories = ["Food", "Transport", "Entertainment", "Health", "Shopping", "Bills", "Other"]

        self.create_widgets()
        self.update_expenses_table()

    def create_widgets(self):
        input_frame = tk.LabelFrame(self.root, text="Add Expense", padx=10, pady=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(input_frame, text="Amount:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.amount_entry = tk.Entry(input_frame, width=15)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Category:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.category_combo = ttk.Combobox(input_frame, values=self.categories, width=15)
        self.category_combo.grid(row=0, column=3, padx=5, pady=5)
        self.category_combo.current(0)

        tk.Label(input_frame, text="Date (YYYY-MM-DD):").grid(row=0, column=4, sticky=tk.W, padx=5, pady=5)
        self.date_entry = tk.Entry(input_frame, width=12)
        self.date_entry.grid(row=0, column=5, padx=5, pady=5)
        self.date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))

        add_btn = tk.Button(input_frame, text="Add Expense", command=self.add_expense)
        add_btn.grid(row=0, column=6, padx=10, pady=5)

        filter_frame = tk.LabelFrame(self.root, text="Filter", padx=10, pady=10)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(filter_frame, text="Category:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.filter_category = ttk.Combobox(filter_frame, values=["All"] + self.categories, width=15)
        self.filter_category.grid(row=0, column=1, padx=5, pady=5)
        self.filter_category.current(0)

        tk.Label(filter_frame, text="From Date (YYYY-MM-DD):").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.from_date_entry = tk.Entry(filter_frame, width=12)
        self.from_date_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(filter_frame, text="To Date (YYYY-MM-DD):").grid(row=0, column=4, sticky=tk.W, padx=5, pady=5)
        self.to_date_entry = tk.Entry(filter_frame, width=12)
        self.to_date_entry.grid(row=0, column=5, padx=5, pady=5)

        filter_btn = tk.Button(filter_frame, text="Apply Filter", command=self.apply_filter)
        filter_btn.grid(row=0, column=6, padx=10, pady=5)

        table_frame = tk.LabelFrame(self.root, text="Expenses", padx=10, pady=10)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("id", "amount", "category", "date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        self.tree.heading("id", text="ID")
        self.tree.heading("amount", text="Amount ($)")
        self.tree.heading("category", text="Category")
        self.tree.heading("date", text="Date")
        self.tree.column("id", width=50)
        self.tree.column("amount", width=100)
        self.tree.column("category", width=150)
        self.tree.column("date", width=120)
        self.tree.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, padx=10, pady=5)

        total_label = tk.Label(bottom_frame, text="Total for filtered period: $0.00", font=("Arial", 12, "bold"))
        total_label.pack(side=tk.LEFT, padx=5)

        self.total_label = total_label

        delete_btn = tk.Button(bottom_frame, text="Delete Selected", command=self.delete_expense)
        delete_btn.pack(side=tk.RIGHT, padx=5)

        save_btn = tk.Button(bottom_frame, text="Save to JSON", command=self.save_expenses_to_file)
        save_btn.pack(side=tk.RIGHT, padx=5)

    def load_expenses(self):
        if os.path.exists(EXPENSES_FILE):
            with open(EXPENSES_FILE, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except:
                    return []
        return []

    def save_expenses_to_file(self):
        with open(EXPENSES_FILE, "w", encoding="utf-8") as f:
            json.dump(self.expenses, f, indent=4)
        messagebox.showinfo("Saved", f"Expenses saved to {EXPENSES_FILE}")

    def add_expense(self):
        amount_str = self.amount_entry.get().strip()
        category = self.category_combo.get()
        date_str = self.date_entry.get().strip()

        if not amount_str:
            messagebox.showwarning("Input Error", "Amount cannot be empty")
            return
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except:
            messagebox.showerror("Input Error", "Amount must be a positive number")
            return

        if not category:
            messagebox.showwarning("Input Error", "Please select a category")
            return

        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except:
            messagebox.showerror("Input Error", "Date must be in YYYY-MM-DD format")
            return

        new_id = max([e["id"] for e in self.expenses], default=0) + 1
        expense = {
            "id": new_id,
            "amount": amount,
            "category": category,
            "date": date_str
        }
        self.expenses.append(expense)
        self.save_expenses_to_file()
        self.clear_inputs()
        self.apply_filter()

    def clear_inputs(self):
        self.amount_entry.delete(0, tk.END)
        self.category_combo.current(0)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))

    def delete_expense(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select an expense to delete")
            return
        item = selected[0]
        expense_id = int(self.tree.item(item, "values")[0])
        self.expenses = [e for e in self.expenses if e["id"] != expense_id]
        self.save_expenses_to_file()
        self.apply_filter()

    def apply_filter(self):
        category = self.filter_category.get()
        from_date = self.from_date_entry.get().strip()
        to_date = self.to_date_entry.get().strip()

        filtered = self.expenses[:]

        if category != "All":
            filtered = [e for e in filtered if e["category"] == category]

        if from_date:
            try:
                from_dt = datetime.strptime(from_date, "%Y-%m-%d")
                filtered = [e for e in filtered if datetime.strptime(e["date"], "%Y-%m-%d") >= from_dt]
            except:
                messagebox.showerror("Filter Error", "Invalid from-date format. Use YYYY-MM-DD")
                return

        if to_date:
            try:
                to_dt = datetime.strptime(to_date, "%Y-%m-%d")
                filtered = [e for e in filtered if datetime.strptime(e["date"], "%Y-%m-%d") <= to_dt]
            except:
                messagebox.showerror("Filter Error", "Invalid to-date format. Use YYYY-MM-DD")
                return

        self.update_expenses_table(filtered)

        total = sum(e["amount"] for e in filtered)
        self.total_label.config(text=f"Total for filtered period: ${total:.2f}")

    def update_expenses_table(self, expenses_list=None):
        for row in self.tree.get_children():
            self.tree.delete(row)
        if expenses_list is None:
            expenses_list = self.expenses
        for exp in expenses_list:
            self.tree.insert("", tk.END, values=(exp["id"], f"{exp['amount']:.2f}", exp["category"], exp["date"]))

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
    __pycache__/
*.pyc
*.pyo
*.pyd
.Python
venv/
env/
ENV/
expenses.json
.DS_Store
