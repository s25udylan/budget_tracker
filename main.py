import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys
from datetime import datetime, timedelta
import calendar

# --- Color Palettes ---
LIGHT_THEME = {
    "BACKGROUND": "#FFFFFF",
    "FRAME": "#F0F0F0",
    "TEXT": "#000000",
    "INPUT_BG": "#EAEAEA",
    "BUTTON": "#DDDDDD",
    "ACCENT_GREEN": "#2E8B57",
    "ACCENT_RED": "#DC143C",
    "LISTBOX_SELECT_BG": "#0078D7" 
}

DARK_THEME = {
    "BACKGROUND": "#000080",
    "FRAME": "#0000CD",
    "TEXT": "#FFFFFF",
    "INPUT_BG": "#ADD8E6",
    "BUTTON": "#4682B4",
    "ACCENT_GREEN": "#00FF00",
    "ACCENT_RED": "#FF4500",
    "LISTBOX_SELECT_BG": "#4682B4"
}

# --- Font Definitions ---
FONT_TITLE = ("Arial", 24, "bold")
FONT_HEADER = ("Arial", 14, "bold")
FONT_BODY = ("Arial", 12)
FONT_BODY_BOLD = ("Arial", 12, "bold")

# --- Data Management ---
DATA_FILE = "finances_data.json"

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_data():
    """Loads data from the JSON file. If no file exists, creates a default structure."""
    if not os.path.exists(DATA_FILE):
        return {
            "accounts": [{"name": "My Wallet", "balance": 0}],
            "categories": ["Food", "Transport", "Shopping", "Bills", "Misc"],
            "budgets": {"Food": 500},
            "transactions": [],
            "loans": [],
            "theme": "light" # Default theme
        }
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            if 'loans' not in data: data['loans'] = []
            if 'theme' not in data: data['theme'] = 'light'
            for t in data['transactions']:
                if 'id' not in t:
                    t['id'] = datetime.strptime(t['date'], '%Y-%m-%d').timestamp() + t['amount']
            return data
    except (json.JSONDecodeError, FileNotFoundError):
        return {
            "accounts": [], "categories": [], "budgets": {}, "transactions": [], "loans": [], "theme": "light"
        }

def save_data(data):
    """Saves the given data to the JSON file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# --- Main Application Class ---
class BudgetApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.data = load_data()
        self.theme_mode = tk.StringVar(value=self.data.get('theme', 'light'))

        self.title("Finances")
        self.geometry("1100x750")
        try:
            icon_path = resource_path("icon.ico")
            self.iconbitmap(icon_path)
        except tk.TclError:
            print("Warning: Could not load application icon 'icon.ico'.")
        
        # Main layout
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Status bar at the bottom
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        
        self.help_button = ttk.Button(self.status_frame, text="?", command=self.show_help_popup, width=2)
        self.help_button.pack(side=tk.LEFT)
        
        self.dev_label = ttk.Label(self.status_frame, text="Developed By: s25udylan", font=("Arial", 8))
        self.dev_label.pack(side=tk.RIGHT)

        # Top content frame
        top_content_frame = ttk.Frame(self.main_frame)
        top_content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.title_label = ttk.Label(top_content_frame, text="Finances")
        self.title_label.pack(pady=10)

        # Theme toggle button
        self.theme_toggle_button = ttk.Button(top_content_frame, text="Toggle Theme", command=self.toggle_theme)
        self.theme_toggle_button.place(relx=0.98, y=10, anchor="ne")

        # Navigation Buttons
        self.nav_frame = ttk.Frame(top_content_frame)
        self.nav_frame.pack(pady=10, fill=tk.X)
        
        self.frames = {}
        button_info = {
            "Dashboard": DashboardFrame,
            "Expenses": ExpensesFrame,
            "Accounts": AccountsFrame,
            "Categories": CategoriesFrame,
            "Budgets": BudgetsFrame,
            "Loans": LoansFrame
        }

        for text, FrameClass in button_info.items():
            btn = ttk.Button(self.nav_frame, text=text, command=lambda f=FrameClass: self.show_frame(f))
            btn.pack(side=tk.LEFT, padx=5, expand=True)
        
        self.container = ttk.Frame(top_content_frame)
        self.container.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        for F in (DashboardFrame, ExpensesFrame, AccountsFrame, CategoriesFrame, BudgetsFrame, LoansFrame):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.apply_theme() # Apply initial theme
        self.show_frame(DashboardFrame)

    def toggle_theme(self):
        new_mode = 'dark' if self.theme_mode.get() == 'light' else 'light'
        self.theme_mode.set(new_mode)
        self.data['theme'] = new_mode
        self.apply_theme()
        
    def show_help_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Help")
        popup.geometry("600x650")
        theme = LIGHT_THEME if self.theme_mode.get() == 'light' else DARK_THEME
        popup.configure(bg=theme["FRAME"])
        popup.transient(self)
        popup.grab_set()

        help_text = """
        **How to Use the 'Finances' App**

        **IMPORTANT: Your Data**
        - All your data is stored in a file named 'finances_data.json'
          which is located in the same directory as the application.
        - DO NOT delete this file unless you want to permanently erase
          all your accounts, transactions, and settings.
        - It's a good idea to back up this file periodically.

        **Dashboard:**
        - A quick overview of your finances.
        - View total account balances and total loan amounts.
        - See the progress of your monthly budgets.
        - Use the '< Prev Month' and 'Next Month >' buttons to view historical data.

        **Expenses:**
        - Log all your payments, including regular expenses and loan payments.
        - To add a payment: Fill in the date, amount, category, account, and description, then click 'Add Payment'.
        - To edit a payment: Select a transaction, click 'Edit Selected', make changes, and click 'Save Changes'.
        - To delete a payment: Select a transaction and click 'Delete Selected'.
        - Use the filter options to search for specific transactions.

        **Accounts:**
        - Manage your different accounts (e.g., bank, wallet).
        - 'Add Account': Creates a new account with an initial balance.
        - 'Add Funds': Select an account and add money to it.
        - 'Transfer Funds': Move money between two of your accounts.
        - 'Delete Selected': Removes the selected account.

        **Categories:**
        - Manage your spending categories (e.g., Food, Shopping). These are used for expenses and budgets.

        **Budgets:**
        - Set a monthly spending limit for each of your categories.

        **Loans:**
        - Track money you owe. Edit a loan's name or total amount.
        - Pay off loans by creating a payment in the 'Expenses' tab and selecting the loan from the category dropdown.

        **Theme:**
        - Click 'Toggle Theme' to switch between light and dark mode.
        """
        
        text_widget = tk.Text(popup, wrap=tk.WORD, bg=theme["FRAME"], fg=theme["TEXT"], font=FONT_BODY, relief=tk.FLAT, bd=0, padx=10, pady=10)
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED) # Make it read-only
        text_widget.pack(expand=True, fill=tk.BOTH)

        close_button = ttk.Button(popup, text="Close", command=popup.destroy)
        close_button.pack(pady=10)

    def apply_theme(self):
        theme = LIGHT_THEME if self.theme_mode.get() == 'light' else DARK_THEME
        
        # Configure main window
        self.configure(bg=theme["BACKGROUND"])
        self.main_frame.configure(bg=theme["BACKGROUND"])
        
        # Configure styles
        style = ttk.Style(self)
        style.theme_use("clam")
        
        style.configure("TFrame", background=theme["FRAME"])
        style.configure("TLabel", background=theme["FRAME"], foreground=theme["TEXT"], font=FONT_BODY)
        style.configure("Header.TLabel", background=theme["FRAME"], font=FONT_HEADER, foreground=theme["TEXT"])
        style.configure("Title.TLabel", background=theme["BACKGROUND"], font=FONT_TITLE, foreground=theme["TEXT"])
        style.configure("Background.TFrame", background=theme["BACKGROUND"])

        style.configure("TButton", background=theme["BUTTON"], foreground=theme["TEXT"], font=FONT_BODY_BOLD, borderwidth=1)
        style.map("TButton", background=[("active", theme["INPUT_BG"])])
        
        style.configure("TEntry", fieldbackground=theme["INPUT_BG"], foreground=theme["TEXT"], font=FONT_BODY)
        style.configure("Treeview", 
                        background=theme["INPUT_BG"], 
                        foreground=theme["TEXT"], 
                        fieldbackground=theme["INPUT_BG"],
                        font=FONT_BODY,
                        rowheight=25)
        style.configure("Treeview.Heading", font=FONT_BODY_BOLD, background=theme["BUTTON"], foreground=theme["TEXT"])
        style.map("Treeview.Heading", background=[("active", theme["INPUT_BG"])])
        
        style.configure("Vertical.TScrollbar", background=theme["BUTTON"], troughcolor=theme["FRAME"])
        style.configure("TProgressbar", troughcolor=theme["FRAME"], background=theme["ACCENT_GREEN"])
        style.configure("TLabelframe", background=theme["FRAME"], relief="groove", borderwidth=2)
        style.configure("TLabelframe.Label", background=theme["FRAME"], foreground=theme["TEXT"], font=FONT_BODY_BOLD)
        
        # Update progress bar styles
        s = ttk.Style()
        s.configure("Green.Horizontal.TProgressbar", background=theme["ACCENT_GREEN"])
        s.configure("Red.Horizontal.TProgressbar", background=theme["ACCENT_RED"])

        # Update all frames and their specific widgets
        self.nav_frame.configure(style="Background.TFrame")
        self.status_frame.configure(style="Background.TFrame")
        self.dev_label.configure(style="TLabel", background=theme["BACKGROUND"])
        self.help_button.configure(style="TButton")

        for frame in self.frames.values():
            frame.update_styles(theme)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.refresh_data()
        frame.tkraise()

    def refresh_all_frames(self):
        save_data(self.data)
        for frame in self.frames.values():
            frame.refresh_data()
    
    def on_closing(self):
        save_data(self.data)
        self.destroy()

# --- Base Frame Class ---
class BaseFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.data = controller.data

    def refresh_data(self):
        pass

    def update_styles(self, theme):
        self.configure(style="TFrame")
        for widget in self.winfo_children():
            if isinstance(widget, (ttk.Frame, ttk.Label, ttk.Button, ttk.Entry, ttk.Combobox, ttk.Treeview)):
                pass

# --- Page Frames ---
class DashboardFrame(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        
        self.view_date = datetime.now()

        # Header with month navigation
        self.header_frame = ttk.Frame(self)
        self.header_frame.pack(pady=10)
        
        self.prev_month_btn = ttk.Button(self.header_frame, text="< Prev Month", command=self.go_to_previous_month)
        self.prev_month_btn.pack(side=tk.LEFT, padx=20)
        
        self.month_label = ttk.Label(self.header_frame, text="", style="Header.TLabel")
        self.month_label.pack(side=tk.LEFT, expand=True)
        
        self.next_month_btn = ttk.Button(self.header_frame, text="Next Month >", command=self.go_to_next_month)
        self.next_month_btn.pack(side=tk.RIGHT, padx=20)
        
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.X, expand=True, padx=20, pady=10)

        # Account Balances Section
        self.accounts_container = ttk.Frame(top_frame, padding=10)
        self.accounts_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.accounts_header_label = ttk.Label(self.accounts_container, text="Account Balances", font=FONT_HEADER)
        self.accounts_header_label.pack(pady=(0,5))
        
        accounts_scroll_frame = ttk.Frame(self.accounts_container, height=100)
        accounts_scroll_frame.pack(fill=tk.X, expand=True)
        accounts_scroll_frame.propagate(False)
        self.accounts_display = tk.Text(accounts_scroll_frame, wrap=tk.NONE, relief=tk.FLAT, bd=0)
        accounts_scrollbar = ttk.Scrollbar(accounts_scroll_frame, orient="vertical", command=self.accounts_display.yview)
        self.accounts_display.configure(yscrollcommand=accounts_scrollbar.set)
        accounts_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.accounts_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.accounts_total_label = ttk.Label(self.accounts_container, text="", font=FONT_BODY_BOLD)
        self.accounts_total_label.pack(pady=(5,0))

        # Loan Status Section
        self.loans_container = ttk.Frame(top_frame, padding=10)
        self.loans_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        self.loans_header_label = ttk.Label(self.loans_container, text="Loan Balances", font=FONT_HEADER)
        self.loans_header_label.pack(pady=(0,5))

        loans_scroll_frame = ttk.Frame(self.loans_container, height=100)
        loans_scroll_frame.pack(fill=tk.X, expand=True)
        loans_scroll_frame.propagate(False)
        self.loans_display = tk.Text(loans_scroll_frame, wrap=tk.NONE, relief=tk.FLAT, bd=0)
        loans_scrollbar = ttk.Scrollbar(loans_scroll_frame, orient="vertical", command=self.loans_display.yview)
        self.loans_display.configure(yscrollcommand=loans_scrollbar.set)
        loans_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.loans_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.loans_total_label = ttk.Label(self.loans_container, text="", font=FONT_BODY_BOLD)
        self.loans_total_label.pack(pady=(5,0))
        
        # Budget Status Section
        self.budgets_frame_container = ttk.Frame(self, padding=10)
        self.budgets_frame_container.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

    def go_to_previous_month(self):
        self.view_date = self.view_date.replace(day=1) - timedelta(days=1)
        self.refresh_data()

    def go_to_next_month(self):
        _, last_day = calendar.monthrange(self.view_date.year, self.view_date.month)
        self.view_date = self.view_date.replace(day=1) + timedelta(days=last_day)
        self.refresh_data()

    def refresh_data(self):
        self.month_label.config(text=self.view_date.strftime("%B %Y"))
        now = datetime.now()
        self.next_month_btn.config(state=tk.DISABLED if self.view_date.year == now.year and self.view_date.month == now.month else tk.NORMAL)
        
        # Accounts
        self.accounts_display.config(state=tk.NORMAL)
        self.accounts_display.delete('1.0', tk.END)
        total_balance = sum(acc.get('balance', 0) for acc in self.data['accounts'])
        for acc in self.data['accounts']:
            self.accounts_display.insert(tk.END, f"{acc['name']}: {acc.get('balance', 0):,.2f}\n")
        self.accounts_display.config(state=tk.DISABLED)
        self.accounts_total_label.config(text=f"Total Balance: {total_balance:,.2f}")

        # Loans
        self.loans_display.config(state=tk.NORMAL)
        self.loans_display.delete('1.0', tk.END)
        total_debt = sum(l.get('remaining_balance', 0) for l in self.data['loans'])
        for loan in self.data['loans']:
            self.loans_display.insert(tk.END, f"{loan['name']}: {loan.get('remaining_balance', 0):,.2f}\n")
        self.loans_display.config(state=tk.DISABLED)
        self.loans_total_label.config(text=f"Total Owed: {total_debt:,.2f}")

        # Budgets
        for widget in self.budgets_frame_container.winfo_children():
            widget.destroy()
        
        self.budget_header_label = ttk.Label(self.budgets_frame_container, text="Monthly Budget Status", font=FONT_HEADER)
        self.budget_header_label.pack()

        monthly_spending = {cat: 0 for cat in self.data['categories']}
        for trans in self.data['transactions']:
            try:
                trans_date = datetime.strptime(trans['date'], "%Y-%m-%d")
                if trans_date.year == self.view_date.year and trans_date.month == self.view_date.month and trans['category'] in monthly_spending:
                    monthly_spending[trans['category']] += trans['amount']
            except (ValueError, TypeError): continue

        for category, budget_amount in self.data['budgets'].items():
            spent = monthly_spending.get(category, 0)
            percentage = (spent / budget_amount) * 100 if budget_amount > 0 else 0
            p_frame = ttk.Frame(self.budgets_frame_container, padding=5)
            p_frame.pack(fill=tk.X, pady=2)
            ttk.Label(p_frame, text=f"{category}: Spent {spent:,.2f} of {budget_amount:,.2f}").pack(side=tk.LEFT, fill=tk.X, expand=True)
            pb = ttk.Progressbar(p_frame, orient=tk.HORIZONTAL, length=200, mode='determinate', value=percentage)
            pb.pack(side=tk.RIGHT)
            pb.config(style="Red.Horizontal.TProgressbar" if percentage > 100 else "Green.Horizontal.TProgressbar")
    
    def update_styles(self, theme):
        super().update_styles(theme)
        self.header_frame.configure(style="TFrame")
        self.month_label.configure(style="Header.TLabel")
        self.accounts_container.configure(style="TFrame")
        self.loans_container.configure(style="TFrame")
        self.budgets_frame_container.configure(style="TFrame")

        self.accounts_header_label.configure(style="Header.TLabel")
        self.loans_header_label.configure(style="Header.TLabel")
        if hasattr(self, 'budget_header_label'):
            self.budget_header_label.configure(style="Header.TLabel")

        self.accounts_display.configure(bg=theme["FRAME"], fg=theme["TEXT"])
        self.loans_display.configure(bg=theme["FRAME"], fg=theme["TEXT"])
        self.accounts_total_label.configure(style="TLabel")
        self.loans_total_label.configure(style="TLabel")
        # Refresh to redraw progress bars with new style
        self.refresh_data()


class ExpensesFrame(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        # Top section for controls
        controls_frame = ttk.Frame(self, padding=10)
        controls_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # Add payment form
        self.add_frame = ttk.LabelFrame(controls_frame, text="Add/Edit Payment", padding=10)
        self.add_frame.grid(row=0, column=0, sticky="ns", padx=(0, 20))
        
        ttk.Label(self.add_frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0, sticky="w", padx=5)
        self.date_entry = ttk.Entry(self.add_frame, width=15)
        self.date_entry.grid(row=0, column=1, sticky="ew", padx=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        ttk.Label(self.add_frame, text="Amount:").grid(row=1, column=0, sticky="w", padx=5)
        self.amount_entry = ttk.Entry(self.add_frame, width=15)
        self.amount_entry.grid(row=1, column=1, sticky="ew", padx=5)
        
        ttk.Label(self.add_frame, text="Type/Category:").grid(row=2, column=0, sticky="w", padx=5)
        self.category_var = tk.StringVar()
        self.category_menu = ttk.Combobox(self.add_frame, textvariable=self.category_var, state='readonly', width=20)
        self.category_menu.grid(row=2, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(self.add_frame, text="Account:").grid(row=3, column=0, sticky="w", padx=5)
        self.account_var = tk.StringVar()
        self.account_menu = ttk.Combobox(self.add_frame, textvariable=self.account_var, state='readonly', width=20)
        self.account_menu.grid(row=3, column=1, sticky="ew", padx=5, pady=2)
        
        ttk.Label(self.add_frame, text="Description:").grid(row=4, column=0, sticky="w", padx=5)
        self.desc_entry = ttk.Entry(self.add_frame, width=30)
        self.desc_entry.grid(row=4, column=1, sticky="ew", padx=5, pady=2)

        self.add_button = ttk.Button(self.add_frame, text="Add Payment", command=self.add_payment)
        self.add_button.grid(row=5, column=1, pady=10)
        self.selected_transaction_id = None

        # Filter section
        self.filter_frame = ttk.LabelFrame(controls_frame, text="Filter Transactions", padding=10)
        self.filter_frame.grid(row=0, column=1, sticky="ns")

        ttk.Label(self.filter_frame, text="Filter by Category:").grid(row=0, column=0, sticky="w")
        self.filter_cat_var = tk.StringVar()
        self.filter_cat_menu = ttk.Combobox(self.filter_frame, textvariable=self.filter_cat_var, state='readonly')
        self.filter_cat_menu.grid(row=1, column=0, padx=5, pady=2, sticky="ew")

        ttk.Label(self.filter_frame, text="Filter by Description:").grid(row=2, column=0, sticky="w")
        self.filter_desc_entry = ttk.Entry(self.filter_frame)
        self.filter_desc_entry.grid(row=3, column=0, padx=5, pady=2, sticky="ew")

        filter_button_frame = ttk.Frame(self.filter_frame)
        filter_button_frame.grid(row=4, column=0, pady=10)
        ttk.Button(filter_button_frame, text="Apply Filter", command=self.filter_transactions).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_button_frame, text="Clear", command=self.clear_filters).pack(side=tk.LEFT)

        # Frame for transactions tree
        trans_frame = ttk.Frame(self, padding=10)
        trans_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=20)
        
        cols = ('Date', 'Description', 'Category', 'Amount', 'Account')
        self.tree = ttk.Treeview(trans_frame, columns=cols, show='headings', selectmode="browse")
        self.tree.column("#0", width=0, stretch=tk.NO)
        for col in cols:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(c, False))
            self.tree.column(col, width=150, anchor=tk.CENTER)
        self.tree.column('Description', width=250)
        
        self.tree.bind('<<TreeviewSelect>>', self.on_item_select)
        
        vsb = ttk.Scrollbar(trans_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Buttons for tree actions
        self.tree_button_frame = ttk.Frame(self)
        self.tree_button_frame.pack(pady=5)
        ttk.Button(self.tree_button_frame, text="Edit Selected", command=self.edit_payment).pack(side=tk.LEFT, padx=10)
        ttk.Button(self.tree_button_frame, text="Delete Selected", command=self.delete_payment).pack(side=tk.LEFT, padx=10)

    def on_item_select(self, event):
        if not self.tree.selection(): return
        self.selected_transaction_id = self.tree.item(self.tree.selection()[0], "text")

    def sort_treeview(self, col, reverse):
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]
        key = float if col == 'Amount' else str
        data.sort(key=lambda x: key(x[0]), reverse=reverse)
        for index, (val, child) in enumerate(data):
            self.tree.move(child, '', index)
        self.tree.heading(col, command=lambda: self.sort_treeview(col, not reverse))

    def populate_tree(self, transactions):
        self.tree.delete(*self.tree.get_children())
        for trans in sorted(transactions, key=lambda x: x['date'], reverse=True):
            values = (trans['date'], trans['description'], trans['category'], f"{trans['amount']:.2f}", trans['account_name'])
            self.tree.insert("", "end", text=trans['id'], values=values)

    def refresh_data(self):
        categories = self.data['categories']
        loan_names = [f"Loan: {l['name']}" for l in self.data['loans'] if l.get('remaining_balance', 0) > 0]
        all_options = sorted(categories) + sorted(loan_names)
        self.category_menu['values'] = all_options
        self.filter_cat_menu['values'] = [""] + all_options
        if all_options: self.category_var.set(all_options[0])

        account_names = [acc['name'] for acc in self.data['accounts']]
        self.account_menu['values'] = account_names
        if account_names: self.account_var.set(account_names[0])
        
        self.populate_tree(self.data['transactions'])
        self.clear_form()

    def filter_transactions(self):
        cat_filter = self.filter_cat_var.get()
        desc_filter = self.filter_desc_entry.get().lower()

        filtered_trans = [t for t in self.data['transactions'] 
                          if (not cat_filter or t['category'] == cat_filter)
                          and (not desc_filter or desc_filter in t['description'].lower())]
        self.populate_tree(filtered_trans)

    def clear_filters(self):
        self.filter_cat_var.set("")
        self.filter_desc_entry.delete(0, tk.END)
        self.populate_tree(self.data['transactions'])

    def clear_form(self):
        self.selected_transaction_id = None
        self.date_entry.delete(0, tk.END); self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.amount_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.add_button.config(text="Add Payment", command=self.add_payment)
        if self.tree.selection(): self.tree.selection_remove(self.tree.selection())

    def add_payment(self):
        try:
            date = self.date_entry.get(); datetime.strptime(date, "%Y-%m-%d")
            amount = float(self.amount_entry.get())
            if amount <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Check date (YYYY-MM-DD) and amount (positive number).")
            return

        category, account_name = self.category_var.get(), self.account_var.get()
        description = self.desc_entry.get() or "N/A"
        if not category or not account_name:
            messagebox.showerror("Invalid Input", "Category and Account must be selected.")
            return

        self.update_balances(amount, account_name, category)
        self.data['transactions'].append({
            "id": datetime.now().timestamp(), "date": date, "description": description,
            "amount": amount, "category": category, "account_name": account_name
        })
        messagebox.showinfo("Success", "Payment added.")
        self.controller.refresh_all_frames()

    def edit_payment(self):
        if not self.selected_transaction_id:
            messagebox.showwarning("No Selection", "Please select a transaction to edit.")
            return
        
        trans_to_edit = next((t for t in self.data['transactions'] if str(t['id']) == str(self.selected_transaction_id)), None)
        if not trans_to_edit:
            messagebox.showerror("Error", "Could not find selected transaction."); self.clear_form(); return
        
        self.date_entry.delete(0, tk.END); self.date_entry.insert(0, trans_to_edit['date'])
        self.amount_entry.delete(0, tk.END); self.amount_entry.insert(0, trans_to_edit['amount'])
        self.category_var.set(trans_to_edit['category'])
        self.account_var.set(trans_to_edit['account_name'])
        self.desc_entry.delete(0, tk.END); self.desc_entry.insert(0, trans_to_edit['description'])
        self.add_button.config(text="Save Changes", command=self.save_edited_payment)
    
    def save_edited_payment(self):
        original_trans = next((t for t in self.data['transactions'] if str(t['id']) == str(self.selected_transaction_id)), None)
        if not original_trans:
            messagebox.showerror("Error", "Transaction not found."); self.clear_form(); return

        self.update_balances(-original_trans['amount'], original_trans['account_name'], original_trans['category'])
        
        try:
            new_date, new_amount = self.date_entry.get(), float(self.amount_entry.get())
            datetime.strptime(new_date, "%Y-%m-%d")
            if new_amount <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Check date and amount.")
            self.update_balances(original_trans['amount'], original_trans['account_name'], original_trans['category'])
            return
        
        new_category, new_account = self.category_var.get(), self.account_var.get()
        new_description = self.desc_entry.get() or "N/A"
        
        self.update_balances(new_amount, new_account, new_category)
        
        original_trans.update({"date": new_date, "amount": new_amount, "category": new_category, "account_name": new_account, "description": new_description})
        messagebox.showinfo("Success", "Transaction updated.")
        self.controller.refresh_all_frames()

    def delete_payment(self):
        if not self.selected_transaction_id:
            messagebox.showwarning("No Selection", "Please select a transaction to delete.")
            return

        trans_to_delete = next((t for t in self.data['transactions'] if str(t['id']) == str(self.selected_transaction_id)), None)
        if not trans_to_delete:
            messagebox.showerror("Error", "Could not find transaction."); return

        if messagebox.askyesno("Confirm Deletion", f"Delete transaction: {trans_to_delete['description']} ({trans_to_delete['amount']:.2f})?"):
            self.update_balances(-trans_to_delete['amount'], trans_to_delete['account_name'], trans_to_delete['category'])
            self.data['transactions'].remove(trans_to_delete)
            messagebox.showinfo("Success", "Transaction deleted.")
            self.controller.refresh_all_frames()

    def update_balances(self, amount, account_name, category_selection):
        for acc in self.data['accounts']:
            if acc['name'] == account_name: acc['balance'] -= amount; break
        if category_selection.startswith("Loan: "):
            loan_name = category_selection.replace("Loan: ", "")
            for loan in self.data['loans']:
                if loan['name'] == loan_name: loan['remaining_balance'] -= amount; break
    
    def update_styles(self, theme):
        super().update_styles(theme)
        self.add_frame.configure(style="TLabelframe")
        self.filter_frame.configure(style="TLabelframe")
        self.tree_button_frame.configure(style="TFrame")
        for child in self.add_frame.winfo_children():
            if isinstance(child, ttk.Label): child.configure(style="TLabel")
        for child in self.filter_frame.winfo_children():
            if isinstance(child, ttk.Label): child.configure(style="TLabel")
        
class AccountsFrame(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.header_label = ttk.Label(self, text="Manage Accounts", style="Header.TLabel")
        self.header_label.pack(pady=10)

        tree_frame = ttk.Frame(self, padding=10)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        cols = ('Account Name', 'Current Balance')
        self.tree = ttk.Treeview(tree_frame, columns=cols, show='headings')
        self.tree.heading('Account Name', text='Account Name')
        self.tree.heading('Current Balance', text='Current Balance')
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(pady=10)
        
        ttk.Button(self.button_frame, text="Add Account", command=self.add_account).pack(side=tk.LEFT, padx=10)
        ttk.Button(self.button_frame, text="Add Funds", command=self.add_funds).pack(side=tk.LEFT, padx=10)
        ttk.Button(self.button_frame, text="Transfer Funds", command=self.transfer_funds).pack(side=tk.LEFT, padx=10)
        ttk.Button(self.button_frame, text="Delete Selected", command=self.delete_account).pack(side=tk.LEFT, padx=10)

    def refresh_data(self):
        self.tree.delete(*self.tree.get_children())
        for acc in self.data['accounts']:
            self.tree.insert("", "end", values=(acc['name'], f"{acc['balance']:,.2f}"))

    def add_account(self):
        self.show_account_popup("Add New Account")
    
    def delete_account(self):
        if not self.tree.focus(): messagebox.showwarning("No Selection", "Please select an account."); return
        account_name = self.tree.item(self.tree.focus())['values'][0]
        if messagebox.askyesno("Confirm", f"Delete account '{account_name}'?"):
            self.data['accounts'] = [acc for acc in self.data['accounts'] if acc['name'] != account_name]
            self.controller.refresh_all_frames()

    def add_funds(self):
        if not self.tree.focus(): messagebox.showwarning("No Selection", "Please select an account."); return
        self.show_funds_popup(self.tree.item(self.tree.focus())['values'][0])

    def transfer_funds(self):
        if len(self.data['accounts']) < 2:
            messagebox.showwarning("Not Enough Accounts", "You need at least two accounts."); return
        self.show_transfer_popup()
    
    def show_transfer_popup(self):
        popup = tk.Toplevel(self); popup.title("Transfer Funds"); popup.geometry("400x250")
        popup.transient(self.controller); popup.grab_set()
        
        theme = LIGHT_THEME if self.controller.theme_mode.get() == 'light' else DARK_THEME
        popup.configure(bg=theme["FRAME"])
        
        frame = ttk.Frame(popup, padding=20)
        frame.pack(expand=True, fill=tk.BOTH)
        
        account_names = [acc['name'] for acc in self.data['accounts']]
        ttk.Label(frame, text="From Account:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        from_var = tk.StringVar(); from_menu = ttk.Combobox(frame, textvariable=from_var, values=account_names, state='readonly')
        from_menu.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="To Account:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        to_var = tk.StringVar(); to_menu = ttk.Combobox(frame, textvariable=to_var, values=account_names, state='readonly')
        to_menu.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Amount:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        amount_entry = ttk.Entry(frame, width=20); amount_entry.grid(row=2, column=1, padx=5, pady=5); amount_entry.focus()

        def save():
            from_name, to_name = from_var.get(), to_var.get()
            if not from_name or not to_name: messagebox.showerror("Invalid Input", "Select both accounts.", parent=popup); return
            if from_name == to_name: messagebox.showerror("Invalid Input", "Cannot transfer to same account.", parent=popup); return
            try: amount = float(amount_entry.get()); assert amount > 0
            except: messagebox.showerror("Invalid Input", "Enter a valid positive amount.", parent=popup); return
            
            from_account = next(acc for acc in self.data['accounts'] if acc['name'] == from_name)
            if from_account['balance'] < amount: messagebox.showerror("Insufficient Funds", "Not enough funds for transfer.", parent=popup); return
            
            to_account = next(acc for acc in self.data['accounts'] if acc['name'] == to_name)
            from_account['balance'] -= amount; to_account['balance'] += amount
            self.controller.refresh_all_frames(); messagebox.showinfo("Success", "Transfer complete.", parent=self.controller); popup.destroy()

        ttk.Button(frame, text="Transfer", command=save).grid(row=3, column=0, columnspan=2, pady=20)
    
    def show_funds_popup(self, account_name):
        popup = tk.Toplevel(self); popup.title("Add Funds"); popup.geometry("350x150")
        popup.transient(self.controller); popup.grab_set()
        theme = LIGHT_THEME if self.controller.theme_mode.get() == 'light' else DARK_THEME
        popup.configure(bg=theme["FRAME"])
        
        frame = ttk.Frame(popup, padding=20); frame.pack(expand=True, fill=tk.BOTH)
        ttk.Label(frame, text=f"Account: {account_name}").grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        ttk.Label(frame, text="Amount to Add:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        amount_entry = ttk.Entry(frame, width=25); amount_entry.grid(row=1, column=1, padx=5, pady=5); amount_entry.focus()

        def save():
            try: amount = float(amount_entry.get()); assert amount > 0
            except: messagebox.showerror("Invalid Input", "Enter valid positive amount.", parent=popup); return
            for acc in self.data['accounts']:
                if acc['name'] == account_name: acc['balance'] += amount; break
            self.controller.refresh_all_frames(); messagebox.showinfo("Success", "Funds added.", parent=self.controller); popup.destroy()

        ttk.Button(frame, text="Add Funds", command=save).grid(row=2, column=0, columnspan=2, pady=10)

    def show_account_popup(self, title):
        popup = tk.Toplevel(self); popup.title(title); popup.geometry("350x200")
        popup.transient(self.controller); popup.grab_set()
        theme = LIGHT_THEME if self.controller.theme_mode.get() == 'light' else DARK_THEME
        popup.configure(bg=theme["FRAME"])
        
        frame = ttk.Frame(popup, padding=20); frame.pack(expand=True, fill=tk.BOTH)
        ttk.Label(frame, text="Account Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        name_entry = ttk.Entry(frame, width=25); name_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(frame, text="Initial Balance:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        balance_entry = ttk.Entry(frame, width=25); balance_entry.grid(row=1, column=1, padx=5, pady=5)
        
        def save():
            name = name_entry.get().strip()
            if not name: messagebox.showerror("Invalid Input", "Name cannot be empty.", parent=popup); return
            try: balance = float(balance_entry.get())
            except ValueError: messagebox.showerror("Invalid Input", "Enter a valid balance.", parent=popup); return
            if name in [acc['name'] for acc in self.data['accounts']]:
                messagebox.showerror("Duplicate", "Account name already exists.", parent=popup); return
            self.data['accounts'].append({"name": name, "balance": balance})
            self.controller.refresh_all_frames(); popup.destroy()

        ttk.Button(frame, text="Save", command=save).grid(row=2, column=0, columnspan=2, pady=10)

    def update_styles(self, theme):
        super().update_styles(theme)
        self.header_label.configure(style="Header.TLabel")
        self.button_frame.configure(style="TFrame")

class CategoriesFrame(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.header_label = ttk.Label(self, text="Manage Expense Categories", style="Header.TLabel")
        self.header_label.pack(pady=10)
        
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.listbox = tk.Listbox(main_frame, relief="flat", highlightthickness=0)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)
        
        self.add_frame = ttk.Frame(self, padding=10)
        self.add_frame.pack(pady=5)
        
        ttk.Label(self.add_frame, text="New Category:").pack(side=tk.LEFT, padx=5)
        self.new_cat_entry = ttk.Entry(self.add_frame, width=20)
        self.new_cat_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(self.add_frame, text="Add", command=self.add_category).pack(side=tk.LEFT)
        
        ttk.Button(self, text="Delete Selected Category", command=self.delete_category).pack(pady=10)

    def refresh_data(self):
        self.listbox.delete(0, tk.END)
        for cat in sorted(self.data['categories']):
            self.listbox.insert(tk.END, cat)

    def add_category(self):
        new_cat = self.new_cat_entry.get().strip()
        if new_cat and new_cat not in self.data['categories']:
            self.data['categories'].append(new_cat)
            self.new_cat_entry.delete(0, tk.END)
            self.controller.refresh_all_frames()
        elif not new_cat: messagebox.showwarning("Input Error", "Category name cannot be empty.")
        else: messagebox.showwarning("Duplicate", "This category already exists.")

    def delete_category(self):
        if not self.listbox.curselection(): messagebox.showwarning("No Selection", "Please select a category."); return
        category = self.listbox.get(self.listbox.curselection())
        if messagebox.askyesno("Confirm", f"Delete '{category}'?"):
            self.data['categories'].remove(category)
            if category in self.data['budgets']: del self.data['budgets'][category]
            self.controller.refresh_all_frames()

    def update_styles(self, theme):
        super().update_styles(theme)
        self.header_label.configure(style="Header.TLabel")
        self.listbox.configure(bg=theme["INPUT_BG"], fg=theme["TEXT"], font=FONT_BODY, selectbackground=theme["LISTBOX_SELECT_BG"])
        self.add_frame.configure(style="TFrame")
        for child in self.add_frame.winfo_children():
            if isinstance(child, ttk.Label): child.configure(style="TLabel")

class BudgetsFrame(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.header_label = ttk.Label(self, text="Set Monthly Budgets", style="Header.TLabel")
        self.header_label.pack(pady=10)

        self.container = ttk.Frame(self, padding="10")
        self.container.pack(fill=tk.BOTH, expand=True, padx=20)
        self.budget_entries = {}
        
        ttk.Button(self, text="Save Budgets", command=self.save_budgets).pack(pady=20)

    def refresh_data(self):
        for widget in self.container.winfo_children(): widget.destroy()
        self.budget_entries.clear()
        
        ttk.Label(self.container, text="Category").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(self.container, text="Budget Amount").grid(row=0, column=1, padx=5, pady=5)

        for row, category in enumerate(sorted(self.data['categories']), 1):
            ttk.Label(self.container, text=category).grid(row=row, column=0, sticky='w', padx=5, pady=3)
            entry = ttk.Entry(self.container, width=15)
            entry.grid(row=row, column=1, sticky='e', padx=5, pady=3)
            entry.insert(0, str(self.data['budgets'].get(category, "")))
            self.budget_entries[category] = entry

    def save_budgets(self):
        for category, entry in self.budget_entries.items():
            value = entry.get().strip()
            if value:
                try: self.data['budgets'][category] = float(value)
                except ValueError: messagebox.showerror("Invalid Input", f"Enter a valid number for '{category}'."); return
            elif category in self.data['budgets']: del self.data['budgets'][category]
        messagebox.showinfo("Success", "Budgets updated.")
        self.controller.refresh_all_frames()

    def update_styles(self, theme):
        super().update_styles(theme)
        self.header_label.configure(style="Header.TLabel")
        for child in self.container.winfo_children():
            if isinstance(child, ttk.Label): child.configure(style="TLabel")

class LoansFrame(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.header_label = ttk.Label(self, text="Manage Loans", style="Header.TLabel")
        self.header_label.pack(pady=10)

        tree_frame = ttk.Frame(self, padding=10)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        cols = ('Loan Name', 'Total Amount', 'Remaining Balance')
        self.tree = ttk.Treeview(tree_frame, columns=cols, show='headings')
        for col in cols: self.tree.heading(col, text=col)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(pady=10)
        
        ttk.Button(self.button_frame, text="Add Loan", command=self.add_loan).pack(side=tk.LEFT, padx=10)
        ttk.Button(self.button_frame, text="Edit Selected", command=self.edit_loan).pack(side=tk.LEFT, padx=10)
        ttk.Button(self.button_frame, text="Delete Selected", command=self.delete_loan).pack(side=tk.LEFT, padx=10)

    def refresh_data(self):
        self.tree.delete(*self.tree.get_children())
        for loan in self.data['loans']:
            self.tree.insert("", "end", values=(loan['name'], f"{loan['total_amount']:,.2f}", f"{loan['remaining_balance']:,.2f}"))

    def add_loan(self):
        self.show_loan_popup("Add New Loan")

    def edit_loan(self):
        if not self.tree.focus(): messagebox.showwarning("No Selection", "Please select a loan to edit."); return
        loan_name = self.tree.item(self.tree.focus())['values'][0]
        loan_data = next((l for l in self.data['loans'] if l['name'] == loan_name), None)
        if loan_data: self.show_loan_popup("Edit Loan", loan_data=loan_data)
        else: messagebox.showerror("Error", "Could not find selected loan.")

    def delete_loan(self):
        if not self.tree.focus(): messagebox.showwarning("No Selection", "Please select a loan to delete."); return
        loan_name = self.tree.item(self.tree.focus())['values'][0]
        if messagebox.askyesno("Confirm", f"Delete loan '{loan_name}'?"):
            self.data['loans'] = [l for l in self.data['loans'] if l['name'] != loan_name]
            self.controller.refresh_all_frames()

    def show_loan_popup(self, title, loan_data=None):
        popup = tk.Toplevel(self); popup.title(title); popup.geometry("350x200")
        popup.transient(self.controller); popup.grab_set()
        theme = LIGHT_THEME if self.controller.theme_mode.get() == 'light' else DARK_THEME
        popup.configure(bg=theme["FRAME"])
        
        frame = ttk.Frame(popup, padding=20); frame.pack(expand=True, fill=tk.BOTH)
        ttk.Label(frame, text="Loan Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        name_entry = ttk.Entry(frame, width=25); name_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(frame, text="Total Amount:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        amount_entry = ttk.Entry(frame, width=25); amount_entry.grid(row=1, column=1, padx=5, pady=5)
        
        if loan_data: name_entry.insert(0, loan_data['name']); amount_entry.insert(0, loan_data['total_amount'])

        def save():
            new_name = name_entry.get().strip()
            if not new_name: messagebox.showerror("Invalid Input", "Loan name cannot be empty.", parent=popup); return
            try: new_total = float(amount_entry.get()); assert new_total > 0
            except: messagebox.showerror("Invalid Input", "Enter a valid positive amount.", parent=popup); return
            
            is_new_name = loan_data is None or loan_data['name'] != new_name
            if is_new_name and new_name in [l['name'] for l in self.data['loans']]:
                messagebox.showerror("Duplicate", "Loan name already exists.", parent=popup); return

            if loan_data: # Edit
                old_name = loan_data['name']
                paid_off = loan_data['total_amount'] - loan_data['remaining_balance']
                loan_data.update({'name': new_name, 'total_amount': new_total, 'remaining_balance': new_total - paid_off})
                if old_name != new_name:
                    for t in self.data['transactions']:
                        if t['category'] == f"Loan: {old_name}": t['category'] = f"Loan: {new_name}"
            else: # Add
                self.data['loans'].append({'name': new_name, 'total_amount': new_total, 'remaining_balance': new_total})
            
            self.controller.refresh_all_frames(); popup.destroy()

        ttk.Button(frame, text="Save", command=save).grid(row=2, column=0, columnspan=2, pady=10)

    def update_styles(self, theme):
        super().update_styles(theme)
        self.header_label.configure(style="Header.TLabel")
        self.button_frame.configure(style="TFrame")

# --- Main execution ---
if __name__ == "__main__":
    app = BudgetApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
