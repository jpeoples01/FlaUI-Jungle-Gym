"""
Jungle Gym - A Desktop Testing Playground
A rich dummy application with many UI components for automated testing practice.
Every widget, tab, and control has a unique name/ID for easy test targeting.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
import json
import math
import random
import time
import threading
import os
import csv
import io


# ─────────────────────────────────────────────────────────────────────────────
# MAIN APPLICATION
# ─────────────────────────────────────────────────────────────────────────────

class JungleGymApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Jungle Gym – Testing Playground")
        self.geometry("1000x720")
        self.minsize(800, 600)
        self.resizable(True, True)

        # Shared application state
        self.status_var = tk.StringVar(value="Ready")
        self.logged_in = tk.BooleanVar(value=False)
        self.current_user = tk.StringVar(value="")
        self.item_list = []          # backing data for the list/table tabs
        self.timer_running = False
        self.timer_seconds = 0
        self.timer_thread = None
        self.undo_stack = []

        self._build_menu()
        self._build_notebook()
        self._build_statusbar()

    # ── MENU ────────────────────────────────────────────────────────────────
    def _build_menu(self):
        menubar = tk.Menu(self, name="menubar")

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, name="menu_file")
        file_menu.add_command(label="New",        command=self._menu_new)
        file_menu.add_command(label="Open…",      command=self._menu_open)
        file_menu.add_command(label="Save…",      command=self._menu_save)
        file_menu.add_separator()
        file_menu.add_command(label="Export CSV", command=self._menu_export_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Exit",       command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0, name="menu_edit")
        edit_menu.add_command(label="Undo",       command=self._menu_undo)
        edit_menu.add_command(label="Clear All",  command=self._menu_clear_all)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, name="menu_view")
        self.dark_mode_var = tk.BooleanVar(value=False)
        view_menu.add_checkbutton(label="Dark Mode (stub)", variable=self.dark_mode_var)
        menubar.add_cascade(label="View", menu=view_menu)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, name="menu_help")
        help_menu.add_command(label="About", command=self._menu_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=menubar)

    # ── NOTEBOOK (TABS) ─────────────────────────────────────────────────────
    def _build_notebook(self):
        self.notebook = ttk.Notebook(self, name="main_notebook")
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        tabs = [
            ("Login",        self._build_login_tab),
            ("Forms",        self._build_forms_tab),
            ("List / CRUD",  self._build_list_tab),
            ("Table",        self._build_table_tab),
            ("Calculator",   self._build_calculator_tab),
            ("Timer",        self._build_timer_tab),
            ("File I/O",     self._build_fileio_tab),
            ("Dialogs",      self._build_dialogs_tab),
            ("Misc Widgets", self._build_misc_tab),
        ]
        for label, builder in tabs:
            frame = ttk.Frame(self.notebook, name=f"tab_{label.lower().replace(' ', '_').replace('/', '_')}")
            self.notebook.add(frame, text=label)
            builder(frame)

    # ── STATUS BAR ──────────────────────────────────────────────────────────
    def _build_statusbar(self):
        bar = ttk.Frame(self, relief=tk.SUNKEN)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        ttk.Label(bar, text="Status:").pack(side=tk.LEFT, padx=4)
        ttk.Label(bar, textvariable=self.status_var, name="lbl_status").pack(side=tk.LEFT)

        self.user_status_lbl = ttk.Label(bar, text="Not logged in", name="lbl_user_status", foreground="grey")
        self.user_status_lbl.pack(side=tk.RIGHT, padx=8)

    def _set_status(self, msg):
        self.status_var.set(msg)

    # ═════════════════════════════════════════════════════════════════════════
    # TAB 1 – LOGIN
    # ═════════════════════════════════════════════════════════════════════════
    def _build_login_tab(self, parent):
        frame = ttk.LabelFrame(parent, text="User Login", name="frame_login", padding=20)
        frame.pack(expand=True)

        ttk.Label(frame, text="Username:").grid(row=0, column=0, sticky=tk.E, pady=4)
        self.login_user_entry = ttk.Entry(frame, name="entry_username", width=25)
        self.login_user_entry.grid(row=0, column=1, padx=8)

        ttk.Label(frame, text="Password:").grid(row=1, column=0, sticky=tk.E, pady=4)
        self.login_pass_entry = ttk.Entry(frame, name="entry_password", show="*", width=25)
        self.login_pass_entry.grid(row=1, column=1, padx=8)

        ttk.Label(frame, text="Role:").grid(row=2, column=0, sticky=tk.E, pady=4)
        self.login_role_combo = ttk.Combobox(
            frame, name="combo_role",
            values=["Admin", "Editor", "Viewer", "Guest"],
            state="readonly", width=22
        )
        self.login_role_combo.current(0)
        self.login_role_combo.grid(row=2, column=1, padx=8)

        self.remember_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="Remember me", variable=self.remember_var,
                        name="chk_remember").grid(row=3, column=1, sticky=tk.W, padx=8)

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=12)
        ttk.Button(btn_frame, text="Login",  name="btn_login",  command=self._do_login).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Logout", name="btn_logout", command=self._do_logout).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Clear",  name="btn_login_clear", command=self._clear_login).pack(side=tk.LEFT, padx=4)

        self.login_result_lbl = ttk.Label(frame, text="", name="lbl_login_result")
        self.login_result_lbl.grid(row=5, column=0, columnspan=2)

        # Validation rules hint
        ttk.Label(frame, text="(Valid creds: admin/admin123, editor/edit456, viewer/view789)",
                  foreground="grey").grid(row=6, column=0, columnspan=2, pady=6)

        # Demo accounts
        self._valid_accounts = {
            "admin":  ("admin123",  "Admin"),
            "editor": ("edit456",   "Editor"),
            "viewer": ("view789",   "Viewer"),
            "guest":  ("",          "Guest"),
        }

    def _do_login(self):
        user = self.login_user_entry.get().strip().lower()
        pw   = self.login_pass_entry.get()
        role = self.login_role_combo.get()

        if user not in self._valid_accounts:
            self.login_result_lbl.config(text="❌ Unknown username", foreground="red", name="lbl_login_result")
            self._set_status("Login failed – unknown user")
            return

        expected_pw, expected_role = self._valid_accounts[user]
        if pw != expected_pw:
            self.login_result_lbl.config(text="❌ Wrong password", foreground="red")
            self._set_status("Login failed – wrong password")
            return

        self.logged_in.set(True)
        self.current_user.set(user)
        self.login_result_lbl.config(text=f"✅ Welcome, {user}! (Role: {role})", foreground="green")
        self.user_status_lbl.config(text=f"Logged in as: {user} [{role}]", foreground="green")
        self._set_status(f"Logged in as {user}")

    def _do_logout(self):
        self.logged_in.set(False)
        self.current_user.set("")
        self.login_result_lbl.config(text="Logged out.", foreground="black")
        self.user_status_lbl.config(text="Not logged in", foreground="grey")
        self._set_status("Logged out")

    def _clear_login(self):
        self.login_user_entry.delete(0, tk.END)
        self.login_pass_entry.delete(0, tk.END)
        self.login_result_lbl.config(text="")
        self._set_status("Login form cleared")

    # ═════════════════════════════════════════════════════════════════════════
    # TAB 2 – FORMS
    # ═════════════════════════════════════════════════════════════════════════
    def _build_forms_tab(self, parent):
        canvas = tk.Canvas(parent)
        scroll = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        inner = ttk.Frame(canvas, name="frame_forms_inner")
        canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # ── Personal info
        grp1 = ttk.LabelFrame(inner, text="Personal Information", padding=10)
        grp1.pack(fill=tk.X, padx=10, pady=8)

        fields = [
            ("First Name",  "entry_firstname"),
            ("Last Name",   "entry_lastname"),
            ("Email",       "entry_email"),
            ("Phone",       "entry_phone"),
            ("Age",         "entry_age"),
        ]
        self.form_entries = {}
        for i, (label, name) in enumerate(fields):
            ttk.Label(grp1, text=label + ":").grid(row=i, column=0, sticky=tk.E, padx=6, pady=3)
            e = ttk.Entry(grp1, name=name, width=30)
            e.grid(row=i, column=1, padx=6, pady=3, sticky=tk.W)
            self.form_entries[name] = e

        # ── Address
        grp2 = ttk.LabelFrame(inner, text="Address", padding=10)
        grp2.pack(fill=tk.X, padx=10, pady=8)

        ttk.Label(grp2, text="Street:").grid(row=0, column=0, sticky=tk.E, padx=6, pady=3)
        self.addr_street = ttk.Entry(grp2, name="entry_street", width=40)
        self.addr_street.grid(row=0, column=1, padx=6, pady=3)

        ttk.Label(grp2, text="City:").grid(row=1, column=0, sticky=tk.E, padx=6, pady=3)
        self.addr_city = ttk.Entry(grp2, name="entry_city", width=25)
        self.addr_city.grid(row=1, column=1, padx=6, pady=3, sticky=tk.W)

        ttk.Label(grp2, text="Country:").grid(row=2, column=0, sticky=tk.E, padx=6, pady=3)
        self.addr_country = ttk.Combobox(grp2, name="combo_country", width=22,
                                          values=["United Kingdom","United States","Canada","Australia","Germany","France","Japan","Other"])
        self.addr_country.current(0)
        self.addr_country.grid(row=2, column=1, padx=6, pady=3, sticky=tk.W)

        # ── Preferences
        grp3 = ttk.LabelFrame(inner, text="Preferences", padding=10)
        grp3.pack(fill=tk.X, padx=10, pady=8)

        self.pref_newsletter = tk.BooleanVar(value=True)
        self.pref_updates    = tk.BooleanVar(value=False)
        self.pref_tips       = tk.BooleanVar(value=True)
        ttk.Checkbutton(grp3, text="Subscribe to newsletter", variable=self.pref_newsletter, name="chk_newsletter").grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(grp3, text="Product updates",         variable=self.pref_updates,    name="chk_updates").grid(row=1, column=0, sticky=tk.W)
        ttk.Checkbutton(grp3, text="Tips & tricks",           variable=self.pref_tips,       name="chk_tips").grid(row=2, column=0, sticky=tk.W)

        ttk.Label(grp3, text="Theme:").grid(row=0, column=1, padx=20, sticky=tk.E)
        self.theme_var = tk.StringVar(value="Light")
        for j, t in enumerate(["Light", "Dark", "System"]):
            ttk.Radiobutton(grp3, text=t, variable=self.theme_var, value=t,
                            name=f"radio_theme_{t.lower()}").grid(row=j, column=2, sticky=tk.W)

        ttk.Label(grp3, text="Font size:").grid(row=3, column=0, sticky=tk.W, pady=6)
        self.font_size_spin = ttk.Spinbox(grp3, name="spin_fontsize", from_=8, to=32, width=6)
        self.font_size_spin.set(12)
        self.font_size_spin.grid(row=3, column=1, sticky=tk.W, padx=20)

        # ── Notes
        grp4 = ttk.LabelFrame(inner, text="Notes", padding=10)
        grp4.pack(fill=tk.X, padx=10, pady=8)
        self.notes_text = tk.Text(grp4, name="text_notes", height=5, width=60, wrap=tk.WORD)
        self.notes_text.pack(padx=4, pady=4)

        # ── Buttons
        btn_row = ttk.Frame(inner)
        btn_row.pack(pady=10)
        ttk.Button(btn_row, text="Submit Form",   name="btn_form_submit", command=self._form_submit).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_row, text="Reset Form",    name="btn_form_reset",  command=self._form_reset).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_row, text="Validate Only", name="btn_form_validate", command=self._form_validate).pack(side=tk.LEFT, padx=6)

        self.form_feedback = ttk.Label(inner, text="", name="lbl_form_feedback")
        self.form_feedback.pack(pady=4)

    def _form_validate(self):
        errors = []
        if not self.form_entries["entry_firstname"].get().strip():
            errors.append("First name required")
        email = self.form_entries["entry_email"].get().strip()
        if email and "@" not in email:
            errors.append("Email looks invalid")
        age = self.form_entries["entry_age"].get().strip()
        if age and not age.isdigit():
            errors.append("Age must be a number")
        if errors:
            self.form_feedback.config(text="⚠ " + "; ".join(errors), foreground="orange")
            self._set_status("Validation errors")
            return False
        self.form_feedback.config(text="✅ Validation passed", foreground="green")
        self._set_status("Form valid")
        return True

    def _form_submit(self):
        if self._form_validate():
            data = {n: e.get() for n, e in self.form_entries.items()}
            data["notes"] = self.notes_text.get("1.0", tk.END).strip()
            self.undo_stack.append(("form_submit", data))
            self.form_feedback.config(text="✅ Form submitted!", foreground="green")
            self._set_status("Form submitted")

    def _form_reset(self):
        for e in self.form_entries.values():
            e.delete(0, tk.END)
        self.notes_text.delete("1.0", tk.END)
        self.form_feedback.config(text="Form reset.", foreground="grey")
        self._set_status("Form reset")

    # ═════════════════════════════════════════════════════════════════════════
    # TAB 3 – LIST / CRUD
    # ═════════════════════════════════════════════════════════════════════════
    def _build_list_tab(self, parent):
        top = ttk.Frame(parent, padding=6)
        top.pack(fill=tk.X)

        ttk.Label(top, text="Item:").pack(side=tk.LEFT, padx=4)
        self.list_entry = ttk.Entry(top, name="entry_list_item", width=28)
        self.list_entry.pack(side=tk.LEFT, padx=4)

        ttk.Button(top, text="Add",    name="btn_list_add",    command=self._list_add).pack(side=tk.LEFT, padx=2)
        ttk.Button(top, text="Edit",   name="btn_list_edit",   command=self._list_edit).pack(side=tk.LEFT, padx=2)
        ttk.Button(top, text="Delete", name="btn_list_delete", command=self._list_delete).pack(side=tk.LEFT, padx=2)
        ttk.Button(top, text="Clear All", name="btn_list_clear", command=self._list_clear).pack(side=tk.LEFT, padx=2)

        # Search bar
        search_row = ttk.Frame(parent, padding=4)
        search_row.pack(fill=tk.X)
        ttk.Label(search_row, text="Search:").pack(side=tk.LEFT, padx=4)
        self.list_search_var = tk.StringVar()
        self.list_search_var.trace_add("write", self._list_search)
        ttk.Entry(search_row, textvariable=self.list_search_var, name="entry_list_search", width=28).pack(side=tk.LEFT, padx=4)
        ttk.Button(search_row, text="Sort A→Z", name="btn_list_sort_asc",  command=lambda: self._list_sort(False)).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_row, text="Sort Z→A", name="btn_list_sort_desc", command=lambda: self._list_sort(True)).pack(side=tk.LEFT, padx=2)

        # Listbox
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        self.listbox = tk.Listbox(list_frame, name="listbox_items", yscrollcommand=scrollbar.set,
                                   selectmode=tk.EXTENDED, font=("Courier", 11))
        scrollbar.config(command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.pack(fill=tk.BOTH, expand=True)

        self.list_count_lbl = ttk.Label(parent, text="Items: 0", name="lbl_list_count")
        self.list_count_lbl.pack(anchor=tk.W, padx=6)

        # Pre-populate
        for item in ["Apple", "Banana", "Cherry", "Date", "Elderberry"]:
            self._list_append(item)

    def _list_append(self, text):
        self.item_list.append(text)
        self.listbox.insert(tk.END, text)
        self.list_count_lbl.config(text=f"Items: {len(self.item_list)}")

    def _list_add(self):
        text = self.list_entry.get().strip()
        if not text:
            self._set_status("Cannot add empty item")
            return
        self.undo_stack.append(("list_add", text))
        self._list_append(text)
        self.list_entry.delete(0, tk.END)
        self._set_status(f"Added: {text}")

    def _list_edit(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Edit", "Select an item to edit.", parent=self)
            return
        idx = sel[0]
        old = self.item_list[idx]
        new_text = self.list_entry.get().strip()
        if not new_text:
            messagebox.showwarning("Edit", "Enter new text in the field above.", parent=self)
            return
        self.undo_stack.append(("list_edit", idx, old, new_text))
        self.item_list[idx] = new_text
        self.listbox.delete(idx)
        self.listbox.insert(idx, new_text)
        self._set_status(f"Edited: {old} → {new_text}")

    def _list_delete(self):
        sel = list(self.listbox.curselection())
        if not sel:
            messagebox.showwarning("Delete", "Select item(s) to delete.", parent=self)
            return
        deleted = [self.item_list[i] for i in sel]
        self.undo_stack.append(("list_delete", sel, deleted))
        for i in reversed(sel):
            self.item_list.pop(i)
            self.listbox.delete(i)
        self.list_count_lbl.config(text=f"Items: {len(self.item_list)}")
        self._set_status(f"Deleted {len(deleted)} item(s)")

    def _list_clear(self):
        self.undo_stack.append(("list_clear", list(self.item_list)))
        self.item_list.clear()
        self.listbox.delete(0, tk.END)
        self.list_count_lbl.config(text="Items: 0")
        self._set_status("List cleared")

    def _list_search(self, *_):
        query = self.list_search_var.get().lower()
        self.listbox.delete(0, tk.END)
        for item in self.item_list:
            if query in item.lower():
                self.listbox.insert(tk.END, item)

    def _list_sort(self, reverse):
        self.item_list.sort(reverse=reverse)
        self.listbox.delete(0, tk.END)
        for item in self.item_list:
            self.listbox.insert(tk.END, item)
        self._set_status("Sorted" + (" Z→A" if reverse else " A→Z"))

    # ═════════════════════════════════════════════════════════════════════════
    # TAB 4 – TABLE (Treeview)
    # ═════════════════════════════════════════════════════════════════════════
    def _build_table_tab(self, parent):
        cols = ("ID", "Name", "Category", "Price", "In Stock")

        toolbar = ttk.Frame(parent, padding=4)
        toolbar.pack(fill=tk.X)
        ttk.Button(toolbar, text="Add Row",    name="btn_table_add",    command=self._table_add_row).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Delete Row", name="btn_table_delete", command=self._table_delete_row).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Populate Sample Data", name="btn_table_populate",
                   command=self._table_populate).pack(side=tk.LEFT, padx=2)

        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        self.tree = ttk.Treeview(tree_frame, name="treeview_products", columns=cols,
                                  show="headings", yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)

        widths = [50, 160, 120, 80, 80]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col, command=lambda c=col: self._tree_sort(c))
            self.tree.column(col, width=w, anchor=tk.CENTER)

        self.tree_row_id = 0

        # Edit row popup
        self.tree.bind("<Double-1>", self._table_edit_popup)

        self._table_populate()

    def _table_populate(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.tree_row_id = 0
        sample = [
            ("Widget Pro",    "Hardware",  "£19.99", "Yes"),
            ("Gizmo Deluxe",  "Software",  "£9.49",  "No"),
            ("Thingamajig",   "Hardware",  "£4.00",  "Yes"),
            ("Doohickey",     "Accessory", "£12.50", "Yes"),
            ("Whatchamacallit","Service",  "£0.00",  "N/A"),
        ]
        for name, cat, price, stock in sample:
            self.tree_row_id += 1
            self.tree.insert("", tk.END, values=(self.tree_row_id, name, cat, price, stock))
        self._set_status("Table populated with sample data")

    def _table_add_row(self):
        self.tree_row_id += 1
        self.tree.insert("", tk.END, values=(self.tree_row_id, "New Item", "—", "£0.00", "?"))
        self._set_status("Row added")

    def _table_delete_row(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Delete", "Select a row to delete.", parent=self)
            return
        for item in sel:
            self.tree.delete(item)
        self._set_status("Row(s) deleted")

    def _table_edit_popup(self, event):
        item = self.tree.identify_row(event.y)
        col  = self.tree.identify_column(event.x)
        if not item or not col:
            return
        col_idx = int(col[1:]) - 1
        values  = list(self.tree.item(item, "values"))
        if col_idx == 0:
            return  # don't edit ID

        popup = tk.Toplevel(self, name="popup_table_edit")
        popup.title("Edit Cell")
        popup.resizable(False, False)
        ttk.Label(popup, text=f"Column: {self.tree['columns'][col_idx]}").pack(padx=12, pady=4)
        var = tk.StringVar(value=values[col_idx])
        entry = ttk.Entry(popup, textvariable=var, name="entry_cell_edit", width=28)
        entry.pack(padx=12, pady=4)
        entry.focus()

        def save():
            values[col_idx] = var.get()
            self.tree.item(item, values=values)
            popup.destroy()
            self._set_status("Cell updated")

        ttk.Button(popup, text="Save",   name="btn_cell_save",   command=save).pack(side=tk.LEFT, padx=10, pady=8)
        ttk.Button(popup, text="Cancel", name="btn_cell_cancel", command=popup.destroy).pack(side=tk.LEFT, padx=4, pady=8)

    def _tree_sort(self, col):
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        try:
            data.sort(key=lambda t: float(t[0].replace("£", "").replace(",", "")))
        except ValueError:
            data.sort()
        for idx, (_, k) in enumerate(data):
            self.tree.move(k, "", idx)
        self._set_status(f"Sorted by {col}")

    # ═════════════════════════════════════════════════════════════════════════
    # TAB 5 – CALCULATOR
    # ═════════════════════════════════════════════════════════════════════════
    def _build_calculator_tab(self, parent):
        outer = ttk.Frame(parent)
        outer.pack(expand=True)

        self.calc_display_var = tk.StringVar(value="0")
        self.calc_expr = ""
        self.calc_just_evaled = False

        disp = ttk.Entry(outer, textvariable=self.calc_display_var, name="entry_calc_display",
                         font=("Courier", 20), justify=tk.RIGHT, width=18, state="readonly")
        disp.grid(row=0, column=0, columnspan=4, sticky=tk.EW, pady=6)

        buttons = [
            ("C",  "#d9534f"), ("±",   "#6c757d"), ("%",   "#6c757d"), ("÷",   "#f0ad4e"),
            ("7",  None),      ("8",   None),      ("9",   None),      ("×",   "#f0ad4e"),
            ("4",  None),      ("5",   None),      ("6",   None),      ("-",   "#f0ad4e"),
            ("1",  None),      ("2",   None),      ("3",   None),      ("+",   "#f0ad4e"),
            ("0",  None),      (".",   None),      ("√",   "#6c757d"), ("=",   "#5cb85c"),
        ]

        for i, (lbl, bg) in enumerate(buttons):
            row, col = divmod(i, 4)
            safe_name = lbl.replace("÷", "div").replace("×", "mul").replace("+", "plus")\
                           .replace("-", "minus").replace("=", "eq").replace(".", "dot")\
                           .replace("√", "sqrt").replace("%", "pct").replace("±", "negate")
            btn = tk.Button(outer, text=lbl, name=f"btn_calc_{safe_name}",
                            width=4, height=2, font=("Arial", 14),
                            bg=bg or "#e9ecef",
                            command=lambda l=lbl: self._calc_press(l))
            btn.grid(row=row + 1, column=col, padx=3, pady=3, sticky=tk.EW)

        self.calc_history_lbl = ttk.Label(outer, text="", name="lbl_calc_history", foreground="grey")
        self.calc_history_lbl.grid(row=6, column=0, columnspan=4)

    def _calc_press(self, key):
        cur = self.calc_display_var.get()

        if key == "C":
            self.calc_expr = ""
            self.calc_display_var.set("0")
            self.calc_just_evaled = False
        elif key == "=":
            expr = self.calc_expr.replace("÷", "/").replace("×", "*")
            try:
                result = eval(expr, {"__builtins__": {}}, {})
                result = round(result, 10)
                if isinstance(result, float) and result.is_integer():
                    result = int(result)
                self.calc_history_lbl.config(text=f"{self.calc_expr} = {result}")
                self.calc_expr = str(result)
                self.calc_display_var.set(str(result))
                self.calc_just_evaled = True
            except Exception:
                self.calc_display_var.set("Error")
                self.calc_expr = ""
        elif key == "√":
            try:
                val = float(self.calc_expr or cur)
                result = round(math.sqrt(val), 10)
                self.calc_history_lbl.config(text=f"√{val} = {result}")
                self.calc_expr = str(result)
                self.calc_display_var.set(str(result))
                self.calc_just_evaled = True
            except Exception:
                self.calc_display_var.set("Error")
        elif key == "%":
            try:
                val = float(self.calc_expr or cur)
                result = val / 100
                self.calc_expr = str(result)
                self.calc_display_var.set(str(result))
                self.calc_just_evaled = True
            except Exception:
                self.calc_display_var.set("Error")
        elif key == "±":
            try:
                val = float(self.calc_expr or cur)
                result = -val
                self.calc_expr = str(result)
                self.calc_display_var.set(str(result))
            except Exception:
                pass
        else:
            if self.calc_just_evaled and key not in "÷×+-":
                self.calc_expr = ""
                self.calc_just_evaled = False
            self.calc_expr += key
            self.calc_display_var.set(self.calc_expr)

    # ═════════════════════════════════════════════════════════════════════════
    # TAB 6 – TIMER / STOPWATCH
    # ═════════════════════════════════════════════════════════════════════════
    def _build_timer_tab(self, parent):
        f = ttk.Frame(parent)
        f.pack(expand=True)

        self.timer_display_var = tk.StringVar(value="00:00:00")
        self.lap_times = []

        ttk.Label(f, textvariable=self.timer_display_var, name="lbl_timer_display",
                  font=("Courier", 40)).pack(pady=20)

        btn_row = ttk.Frame(f)
        btn_row.pack()
        ttk.Button(btn_row, text="Start",  name="btn_timer_start",  command=self._timer_start).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_row, text="Pause",  name="btn_timer_pause",  command=self._timer_pause).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_row, text="Reset",  name="btn_timer_reset",  command=self._timer_reset).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_row, text="Lap",    name="btn_timer_lap",    command=self._timer_lap).pack(side=tk.LEFT, padx=6)

        self.timer_state_lbl = ttk.Label(f, text="State: Stopped", name="lbl_timer_state")
        self.timer_state_lbl.pack(pady=6)

        ttk.Label(f, text="Lap Times:").pack()
        self.lap_listbox = tk.Listbox(f, name="listbox_laps", height=8, width=25)
        self.lap_listbox.pack(pady=4)

    def _timer_start(self):
        if not self.timer_running:
            self.timer_running = True
            self.timer_state_lbl.config(text="State: Running")
            self._set_status("Timer running")
            self.timer_thread = threading.Thread(target=self._timer_tick, daemon=True)
            self.timer_thread.start()

    def _timer_pause(self):
        self.timer_running = False
        self.timer_state_lbl.config(text="State: Paused")
        self._set_status("Timer paused")

    def _timer_reset(self):
        self.timer_running = False
        self.timer_seconds = 0
        self.timer_display_var.set("00:00:00")
        self.timer_state_lbl.config(text="State: Stopped")
        self.lap_times.clear()
        self.lap_listbox.delete(0, tk.END)
        self._set_status("Timer reset")

    def _timer_lap(self):
        if self.timer_running:
            t = self.timer_seconds
            h, r = divmod(t, 3600)
            m, s = divmod(r, 60)
            label = f"Lap {len(self.lap_times)+1}: {h:02}:{m:02}:{s:02}"
            self.lap_times.append(t)
            self.lap_listbox.insert(tk.END, label)
            self._set_status(f"Lap recorded: {label}")

    def _timer_tick(self):
        while self.timer_running:
            time.sleep(1)
            if self.timer_running:
                self.timer_seconds += 1
                h, r = divmod(self.timer_seconds, 3600)
                m, s = divmod(r, 60)
                self.timer_display_var.set(f"{h:02}:{m:02}:{s:02}")

    # ═════════════════════════════════════════════════════════════════════════
    # TAB 7 – FILE I/O
    # ═════════════════════════════════════════════════════════════════════════
    def _build_fileio_tab(self, parent):
        f = ttk.Frame(parent, padding=10)
        f.pack(fill=tk.BOTH, expand=True)

        ttk.Label(f, text="File Path:").grid(row=0, column=0, sticky=tk.E, pady=4)
        self.file_path_var = tk.StringVar()
        ttk.Entry(f, textvariable=self.file_path_var, name="entry_filepath", width=45).grid(row=0, column=1, padx=4)
        ttk.Button(f, text="Browse…", name="btn_browse", command=self._browse_file).grid(row=0, column=2, padx=4)

        ttk.Button(f, text="Open & Read",  name="btn_file_open",  command=self._file_open).grid(row=1, column=0, columnspan=2, pady=4, sticky=tk.W, padx=4)
        ttk.Button(f, text="Save Content", name="btn_file_save",  command=self._file_save).grid(row=1, column=1, pady=4, sticky=tk.E, padx=4)
        ttk.Button(f, text="Clear",        name="btn_fileio_clear", command=self._fileio_clear).grid(row=1, column=2, pady=4, padx=4)

        self.file_content_text = tk.Text(f, name="text_file_content", height=18, width=70, wrap=tk.WORD)
        sb = ttk.Scrollbar(f, orient=tk.VERTICAL, command=self.file_content_text.yview)
        self.file_content_text.configure(yscrollcommand=sb.set)
        self.file_content_text.grid(row=2, column=0, columnspan=3, sticky=tk.NSEW, pady=4)
        sb.grid(row=2, column=3, sticky=tk.NS)

        self.file_feedback = ttk.Label(f, text="", name="lbl_file_feedback")
        self.file_feedback.grid(row=3, column=0, columnspan=3, sticky=tk.W)
        f.rowconfigure(2, weight=1)
        f.columnconfigure(1, weight=1)

    def _browse_file(self):
        path = filedialog.askopenfilename(parent=self,
            filetypes=[("Text files", "*.txt"), ("JSON", "*.json"), ("CSV", "*.csv"), ("All", "*.*")])
        if path:
            self.file_path_var.set(path)

    def _file_open(self):
        path = self.file_path_var.get().strip()
        if not path:
            self.file_feedback.config(text="⚠ No path specified", foreground="orange")
            return
        try:
            with open(path, "r", encoding="utf-8") as fh:
                content = fh.read()
            self.file_content_text.delete("1.0", tk.END)
            self.file_content_text.insert("1.0", content)
            self.file_feedback.config(text=f"✅ Opened: {path}", foreground="green")
            self._set_status("File opened")
        except Exception as e:
            self.file_feedback.config(text=f"❌ Error: {e}", foreground="red")

    def _file_save(self):
        path = filedialog.asksaveasfilename(parent=self, defaultextension=".txt",
            filetypes=[("Text", "*.txt"), ("JSON", "*.json"), ("All", "*.*")])
        if not path:
            return
        content = self.file_content_text.get("1.0", tk.END)
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(content)
            self.file_feedback.config(text=f"✅ Saved to: {path}", foreground="green")
            self._set_status("File saved")
        except Exception as e:
            self.file_feedback.config(text=f"❌ Error: {e}", foreground="red")

    def _fileio_clear(self):
        self.file_content_text.delete("1.0", tk.END)
        self.file_path_var.set("")
        self.file_feedback.config(text="")
        self._set_status("File I/O cleared")

    # ═════════════════════════════════════════════════════════════════════════
    # TAB 8 – DIALOGS
    # ═════════════════════════════════════════════════════════════════════════
    def _build_dialogs_tab(self, parent):
        f = ttk.LabelFrame(parent, text="Dialog Launchers", padding=16)
        f.pack(expand=True, padx=20, pady=20, fill=tk.X)

        dialogs = [
            ("Info Dialog",        "btn_dialog_info",     self._dlg_info),
            ("Warning Dialog",     "btn_dialog_warning",  self._dlg_warning),
            ("Error Dialog",       "btn_dialog_error",    self._dlg_error),
            ("Yes/No Question",    "btn_dialog_yesno",    self._dlg_yesno),
            ("OK/Cancel",          "btn_dialog_okcancel", self._dlg_okcancel),
            ("Input Dialog",       "btn_dialog_input",    self._dlg_input),
            ("Color Picker",       "btn_dialog_color",    self._dlg_color),
            ("Open File Dialog",   "btn_dialog_openfile", self._dlg_openfile),
            ("Save File Dialog",   "btn_dialog_savefile", self._dlg_savefile),
            ("Choose Directory",   "btn_dialog_directory",self._dlg_directory),
        ]
        for i, (label, name, cmd) in enumerate(dialogs):
            ttk.Button(f, text=label, name=name, command=cmd, width=22).grid(
                row=i // 2, column=i % 2, padx=10, pady=6, sticky=tk.W)

        self.dialog_result_lbl = ttk.Label(parent, text="Dialog result will appear here",
                                            name="lbl_dialog_result", foreground="grey")
        self.dialog_result_lbl.pack(pady=10)

    def _dlg_result(self, msg):
        self.dialog_result_lbl.config(text=f"Result: {msg}", foreground="black")
        self._set_status(f"Dialog result: {msg}")

    def _dlg_info(self):
        messagebox.showinfo("Information", "This is an informational message.", parent=self)
        self._dlg_result("Info dismissed")

    def _dlg_warning(self):
        messagebox.showwarning("Warning", "This is a warning!", parent=self)
        self._dlg_result("Warning dismissed")

    def _dlg_error(self):
        messagebox.showerror("Error", "Something went wrong.", parent=self)
        self._dlg_result("Error dismissed")

    def _dlg_yesno(self):
        ans = messagebox.askyesno("Question", "Do you want to proceed?", parent=self)
        self._dlg_result("Yes" if ans else "No")

    def _dlg_okcancel(self):
        ans = messagebox.askokcancel("Confirm", "Are you sure?", parent=self)
        self._dlg_result("OK" if ans else "Cancel")

    def _dlg_input(self):
        popup = tk.Toplevel(self, name="popup_input_dialog")
        popup.title("Input")
        popup.resizable(False, False)
        ttk.Label(popup, text="Enter a value:").pack(padx=16, pady=8)
        var = tk.StringVar()
        ttk.Entry(popup, textvariable=var, name="entry_input_dialog", width=24).pack(padx=16)

        def submit():
            self._dlg_result(f"Input: '{var.get()}'")
            popup.destroy()

        ttk.Button(popup, text="OK",     name="btn_input_ok",     command=submit).pack(side=tk.LEFT, padx=16, pady=10)
        ttk.Button(popup, text="Cancel", name="btn_input_cancel", command=popup.destroy).pack(side=tk.LEFT, padx=4, pady=10)

    def _dlg_color(self):
        color = colorchooser.askcolor(parent=self, title="Pick a colour")
        if color and color[1]:
            self._dlg_result(f"Color: {color[1]}")
        else:
            self._dlg_result("Color picker cancelled")

    def _dlg_openfile(self):
        path = filedialog.askopenfilename(parent=self)
        self._dlg_result(f"Open: {path or 'cancelled'}")

    def _dlg_savefile(self):
        path = filedialog.asksaveasfilename(parent=self)
        self._dlg_result(f"Save: {path or 'cancelled'}")

    def _dlg_directory(self):
        path = filedialog.askdirectory(parent=self)
        self._dlg_result(f"Dir: {path or 'cancelled'}")

    # ═════════════════════════════════════════════════════════════════════════
    # TAB 9 – MISC WIDGETS
    # ═════════════════════════════════════════════════════════════════════════
    def _build_misc_tab(self, parent):
        canvas = tk.Canvas(parent)
        sb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(fill=tk.BOTH, expand=True)
        inner = ttk.Frame(canvas, name="frame_misc_inner")
        canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # ── Progress bar
        pg = ttk.LabelFrame(inner, text="Progress Bar", padding=8)
        pg.pack(fill=tk.X, padx=10, pady=6)
        self.progress_var = tk.IntVar(value=0)
        self.progressbar = ttk.Progressbar(pg, name="progressbar_main", variable=self.progress_var,
                                            maximum=100, length=300, mode="determinate")
        self.progressbar.pack(pady=4)
        pb_btn = ttk.Frame(pg)
        pb_btn.pack()
        ttk.Button(pb_btn, text="+10",   name="btn_progress_inc",   command=lambda: self._progress_change(10)).pack(side=tk.LEFT, padx=4)
        ttk.Button(pb_btn, text="-10",   name="btn_progress_dec",   command=lambda: self._progress_change(-10)).pack(side=tk.LEFT, padx=4)
        ttk.Button(pb_btn, text="Fill",  name="btn_progress_fill",  command=lambda: self.progress_var.set(100)).pack(side=tk.LEFT, padx=4)
        ttk.Button(pb_btn, text="Reset", name="btn_progress_reset", command=lambda: self.progress_var.set(0)).pack(side=tk.LEFT, padx=4)
        ttk.Button(pb_btn, text="Animate", name="btn_progress_anim", command=self._progress_animate).pack(side=tk.LEFT, padx=4)
        self.progress_lbl = ttk.Label(pg, text="0%", name="lbl_progress_pct")
        self.progress_lbl.pack()

        # ── Scale / Slider
        sl = ttk.LabelFrame(inner, text="Sliders", padding=8)
        sl.pack(fill=tk.X, padx=10, pady=6)
        self.scale_h_var = tk.DoubleVar(value=50)
        self.scale_v_var = tk.DoubleVar(value=25)
        ttk.Label(sl, text="Horizontal:").grid(row=0, column=0, sticky=tk.E)
        h_scale = ttk.Scale(sl, variable=self.scale_h_var, from_=0, to=100,
                             orient=tk.HORIZONTAL, length=220, name="scale_horizontal")
        h_scale.grid(row=0, column=1, padx=8)
        self.scale_h_lbl = ttk.Label(sl, text="50.0", name="lbl_scale_h_val")
        self.scale_h_lbl.grid(row=0, column=2)
        h_scale.config(command=lambda v: self.scale_h_lbl.config(text=f"{float(v):.1f}"))

        ttk.Label(sl, text="Vertical:").grid(row=1, column=0, sticky=tk.E, pady=6)
        v_scale = ttk.Scale(sl, variable=self.scale_v_var, from_=0, to=100,
                             orient=tk.VERTICAL, length=80, name="scale_vertical")
        v_scale.grid(row=1, column=1, padx=8)
        self.scale_v_lbl = ttk.Label(sl, text="25.0", name="lbl_scale_v_val")
        self.scale_v_lbl.grid(row=1, column=2)
        v_scale.config(command=lambda v: self.scale_v_lbl.config(text=f"{float(v):.1f}"))

        # ── Toggle / Switch (via Checkbutton)
        tog = ttk.LabelFrame(inner, text="Toggles & Flags", padding=8)
        tog.pack(fill=tk.X, padx=10, pady=6)
        self.toggle_vars = {}
        for i, (label, name) in enumerate([
            ("Feature A enabled", "toggle_feature_a"),
            ("Feature B enabled", "toggle_feature_b"),
            ("Maintenance mode",  "toggle_maintenance"),
            ("Verbose logging",   "toggle_verbose"),
            ("Beta features",     "toggle_beta"),
        ]):
            var = tk.BooleanVar(value=(i % 2 == 0))
            self.toggle_vars[name] = var
            ttk.Checkbutton(tog, text=label, variable=var, name=name).grid(
                row=i // 2, column=i % 2, sticky=tk.W, padx=12, pady=2)

        # ── Colour swatch output
        col_frame = ttk.LabelFrame(inner, text="Colour Swatch (pick changes swatch)", padding=8)
        col_frame.pack(fill=tk.X, padx=10, pady=6)
        self.swatch = tk.Label(col_frame, name="lbl_color_swatch",
                                bg="#4287f5", width=10, height=2, text="#4287f5")
        self.swatch.pack(side=tk.LEFT, padx=8)
        ttk.Button(col_frame, text="Pick Colour", name="btn_swatch_pick",
                   command=self._pick_swatch).pack(side=tk.LEFT, padx=8)

        # ── Read-only info panel
        info = ttk.LabelFrame(inner, text="App Info (read-only)", padding=8)
        info.pack(fill=tk.X, padx=10, pady=6)
        info_data = [
            ("App name",    "Jungle Gym"),
            ("Version",     "1.0.0"),
            ("Framework",   "Python tkinter"),
            ("Purpose",     "Automated testing playground"),
        ]
        for i, (k, v) in enumerate(info_data):
            ttk.Label(info, text=f"{k}:").grid(row=i, column=0, sticky=tk.E, padx=4)
            e = ttk.Entry(info, name=f"info_{k.lower().replace(' ', '_')}", width=34)
            e.insert(0, v)
            e.config(state="readonly")
            e.grid(row=i, column=1, padx=6, pady=2, sticky=tk.W)

        # ── Random data generator
        rnd = ttk.LabelFrame(inner, text="Random Data Generator", padding=8)
        rnd.pack(fill=tk.X, padx=10, pady=6)
        ttk.Button(rnd, text="Generate Random Name",   name="btn_rand_name",   command=self._gen_name).pack(side=tk.LEFT, padx=6)
        ttk.Button(rnd, text="Generate Random Number", name="btn_rand_number", command=self._gen_number).pack(side=tk.LEFT, padx=6)
        ttk.Button(rnd, text="Generate UUID",          name="btn_rand_uuid",   command=self._gen_uuid).pack(side=tk.LEFT, padx=6)
        self.rand_output_var = tk.StringVar(value="—")
        ttk.Label(rnd, textvariable=self.rand_output_var, name="lbl_rand_output",
                  font=("Courier", 11)).pack(pady=4)

    def _progress_change(self, delta):
        new = max(0, min(100, self.progress_var.get() + delta))
        self.progress_var.set(new)
        self.progress_lbl.config(text=f"{new}%")
        self._set_status(f"Progress: {new}%")

    def _progress_animate(self):
        self.progress_var.set(0)
        def run():
            for i in range(101):
                self.progress_var.set(i)
                self.progress_lbl.config(text=f"{i}%")
                time.sleep(0.03)
        threading.Thread(target=run, daemon=True).start()

    def _pick_swatch(self):
        colour = colorchooser.askcolor(parent=self, title="Pick a colour")
        if colour and colour[1]:
            self.swatch.config(bg=colour[1], text=colour[1])

    def _gen_name(self):
        first = random.choice(["Alice","Bob","Charlie","Diana","Eve","Frank","Grace","Hank"])
        last  = random.choice(["Smith","Jones","Williams","Brown","Taylor","Davies","Wilson"])
        self.rand_output_var.set(f"{first} {last}")
        self._set_status("Name generated")

    def _gen_number(self):
        n = random.randint(1, 1_000_000)
        self.rand_output_var.set(str(n))
        self._set_status("Number generated")

    def _gen_uuid(self):
        import uuid
        self.rand_output_var.set(str(uuid.uuid4()))
        self._set_status("UUID generated")

    # ═════════════════════════════════════════════════════════════════════════
    # MENU HANDLERS
    # ═════════════════════════════════════════════════════════════════════════
    def _menu_new(self):
        self._form_reset()
        self._list_clear()
        self._set_status("New – everything reset")

    def _menu_open(self):
        path = filedialog.askopenfilename(parent=self,
            filetypes=[("JSON", "*.json"), ("Text", "*.txt"), ("All", "*.*")])
        if path:
            self.file_path_var.set(path)
            self._file_open()
            self._set_status(f"Opened via menu: {path}")

    def _menu_save(self):
        self._file_save()

    def _menu_export_csv(self):
        path = filedialog.asksaveasfilename(parent=self, defaultextension=".csv",
            filetypes=[("CSV", "*.csv")])
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as fh:
                writer = csv.writer(fh)
                writer.writerow(["Item"])
                for item in self.item_list:
                    writer.writerow([item])
            self._set_status(f"Exported CSV to {path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e), parent=self)

    def _menu_undo(self):
        if not self.undo_stack:
            messagebox.showinfo("Undo", "Nothing to undo.", parent=self)
            return
        action = self.undo_stack.pop()
        self._set_status(f"Undo: {action[0]}")

    def _menu_clear_all(self):
        if messagebox.askyesno("Clear All", "Clear everything?", parent=self):
            self._menu_new()

    def _menu_about(self):
        messagebox.showinfo(
            "About Jungle Gym",
            "Jungle Gym v1.0\n\nA desktop testing playground.\n"
            "Contains: Login, Forms, List/CRUD, Table,\n"
            "Calculator, Timer, File I/O, Dialogs, and more.\n\n"
            "Built with Python + tkinter.",
            parent=self
        )


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = JungleGymApp()
    app.mainloop()