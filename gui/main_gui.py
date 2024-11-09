# gui/main_gui.py

import tkinter as tk
from tkinter import ttk, messagebox
from sqlalchemy.orm import Session
from db_ops.new_order import NewOrderInserter
from db_ops.search import SearchOperator
from db_ops.mass_import import MassImporter
from db_ops.update_order import UpdateOrder
from logger import logger
from gui.insert_order_window import InsertOrderWindow
from gui.displacer_window import DisplacerWindow
from gui.coldhead_window import ColdheadWindow
from gui.add_test_window import AddTestWindow
from gui.import_window import ImportWindow
from gui.detail_window import DetailWindow


class GUIFace:
    def __init__(self, root: tk.Tk, db_session: Session):
        self.root = root
        self.db_session = db_session
        self.new_order_inserter = NewOrderInserter(db_session)
        self.search_operator = SearchOperator(db_session)
        self.mass_importer = MassImporter(db_session)
        self.update_order = UpdateOrder(db_session)
        logger.info("GUIFace initialized with Database operators.")

        # Initialize UI components
        self.setup_ui()

    def setup_ui(self):
        # Set up main window
        self.root.title("Database Management Hub")
        self.root.geometry("1400x800")
        self.root.configure(padx=10, pady=10)

        # Add search frame, action buttons, and treeview
        self.create_main_frames()
        self.create_search_fields()
        self.create_action_buttons()
        self.create_treeview()

    def create_main_frames(self):
        # Main frame
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill="x", pady=10)

        # Frames for search and actions
        self.search_frame = ttk.LabelFrame(top_frame, text="Filter Search Criteria", padding=(10, 10))
        self.search_frame.pack(side="left", fill="x", padx=(0, 10))
        self.actions_frame = ttk.LabelFrame(top_frame, text="Actions", padding=(10, 10))
        self.actions_frame.pack(side="right", padx=(0, 10))

        # Frame for search results
        self.results_frame = ttk.LabelFrame(self.root, text="Search Results", padding=(10, 10))
        self.results_frame.pack(fill="both", expand=True, pady=10)

    def create_search_fields(self):
        # Configure grid layout for search frame
        for i in range(4):
            self.search_frame.rowconfigure(i, pad=5)
        self.search_frame.columnconfigure(1, weight=1)

        # Input fields for search criteria
        self.serial_number_input = self.create_input_field("Coldhead Serial Number:", 0)
        self.wip_number_input = self.create_input_field("WIP Number:", 1)
        self.displacer_serial_input = self.create_input_field("Displacer Serial Number:", 2)
        self.test_id_input = self.create_input_field("Test ID:", 3)

    def create_input_field(self, label_text, row):
        label = ttk.Label(self.search_frame, text=label_text)
        label.grid(row=row, column=0, sticky="w")
        entry = ttk.Entry(self.search_frame)
        entry.grid(row=row, column=1, sticky="ew")
        return entry

    def create_action_buttons(self):
        # Create Search and Show All Buttons
        search_button = tk.Button(
            self.search_frame,
            text="Search",
            command=self.button_search,
            bg="#4CAF50",
            fg="white",
            font=("Helvetica", 10, "bold"),
            width=10
        )
        search_button.grid(row=4, column=0, padx=5, pady=10, sticky="e")

        show_all_button = tk.Button(
            self.search_frame,
            text="Show All",
            command=self.button_show_all,
            bg="#2196F3",
            fg="white",
            font=("Helvetica", 10, "bold"),
            width=10
        )
        show_all_button.grid(row=4, column=1, padx=5, pady=10, sticky="w")

        # Additional action buttons for data insertion and import
        insert_displacer_button = ttk.Button(self.actions_frame, text="Insert Displacer", command=self.open_displacer_window)
        insert_displacer_button.pack(pady=5, fill=tk.X)

        insert_order_button = ttk.Button(self.actions_frame, text="Insert Order", command=self.open_insert_order_window)
        insert_order_button.pack(pady=5, fill=tk.X)

        insert_coldhead_button = ttk.Button(self.actions_frame, text="Insert Coldhead", command=self.open_coldhead_window)
        insert_coldhead_button.pack(pady=5, fill=tk.X)

        import_button = ttk.Button(self.actions_frame, text="Import from Excel", command=self.open_import_window)
        import_button.pack(pady=5, fill=tk.X)

        add_test_button = ttk.Button(self.actions_frame, text="Add Test", command=self.open_add_test_window)
        add_test_button.pack(pady=5, fill=tk.X)

    def create_treeview(self):
        # Set up columns for the Treeview
        columns = [
            "wip_number", "coldhead_id", "coldhead_serial_number",
            "displacer_serial_number", "arrival_date", "teardown_date",
            "wip_status", "displacer_status", "displacer_notes", "initial_open_date"
        ]

        # Create Treeview widget with scrollbars
        tree_frame = ttk.Frame(self.results_frame)
        tree_frame.pack(fill="both", expand=True)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")

        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        # Define headings for each column
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=120, anchor="center")

        # Apply style for row colors
        style = ttk.Style()
        style.configure("Treeview", rowheight=25)
        self.tree.tag_configure("oddrow", background="lightgrey")
        self.tree.tag_configure("evenrow", background="white")

        # Bind double-click to open details
        self.tree.bind("<Double-1>", self.open_detail_window_event)

    def button_search(self):
        try:
            # Retrieve input values
            coldhead_serial = self.serial_number_input.get().strip()
            wip_number = self.wip_number_input.get().strip()
            displacer_serial = self.displacer_serial_input.get().strip()
            test_id = self.test_id_input.get().strip()

            # Execute search
            search_results = self.search_operator.flexible_search(
                coldhead_serial=coldhead_serial or None,
                wip_number=wip_number or None,
                displacer_serial=displacer_serial or None,
                test_id=test_id or None
            )

            # Update treeview with results
            self.update_treeview(search_results)
            logger.info("Search completed successfully.")
        except Exception as e:
            logger.exception("Error during search.")
            messagebox.showerror("Error", f"Search failed: {e}")

    def button_show_all(self):
        try:
            # Clear search criteria and show all records
            search_results = self.search_operator.flexible_search()
            self.update_treeview(search_results)
            logger.info("Show all records executed.")
        except Exception as e:
            logger.exception("Error during show all.")
            messagebox.showerror("Error", f"Show All failed: {e}")

    def update_treeview(self, data):
        # Clear previous data
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Populate with new data
        for idx, (key, details) in enumerate(data.items()):
            values = [details.get(col, "N/A") for col in self.tree["columns"]]
            tag = "oddrow" if idx % 2 == 0 else "evenrow"
            self.tree.insert("", "end", values=values, tags=(tag,))

    def open_detail_window_event(self, event):
        self.open_detail_window()

    def open_detail_window(self):
        # Open detailed window for selected record
        selected_item = self.tree.selection()
        if selected_item:
            item_values = self.tree.item(selected_item[0], "values")
            wip_details = {
                "wip_number": item_values[0],
                "coldhead_id": item_values[1],
                "coldhead_serial_number": item_values[2],
                "displacer_serial_number": item_values[3],
                "arrival_date": item_values[4],
                "teardown_date": item_values[5],
                "wip_status": item_values[6],
                "displacer_status": item_values[7],
                "displacer_notes": item_values[8],
                "initial_open_date": item_values[9],
            }

            # Fetch associated test data
            tests = self.search_operator.fetch_tests(wip_details["wip_number"])
            test_list = [dict(row) for row in tests] if tests else []

            try:
                DetailWindow(self.root, wip_details, test_list, self.db_session)
            except Exception as e:
                logger.exception("Failed to open DetailWindow.")
                messagebox.showerror("Error", f"Failed to open details: {e}")

    # Functions to open other windows
    def open_displacer_window(self):
        try:
            DisplacerWindow(self.root, self.db_session)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open DisplacerWindow:\n{e}")

    def open_insert_order_window(self):
        try:
            InsertOrderWindow(self.root, self.db_session)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open InsertOrderWindow:\n{e}")

    def open_coldhead_window(self):
        try:
            ColdheadWindow(self.root, self.db_session)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open ColdheadWindow:\n{e}")

    def open_import_window(self):
        try:
            ImportWindow(self.root, self.db_session)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open ImportWindow:\n{e}")

    def open_add_test_window(self):
        try:
            AddTestWindow(self.root, self.db_session)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open AddTestWindow:\n{e}")
