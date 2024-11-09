# gui/import_window.py

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from sqlalchemy.orm import Session
from db_ops.mass_import import MassImporter
from logger import logger


class ImportWindow:
    def __init__(self, parent: tk.Tk, db_session: Session):
        """
        Initialize the ImportWindow.

        :param parent: The parent Tkinter window.
        :param db_session: SQLAlchemy session object.
        """
        self.parent = parent
        self.db_session = db_session
        self.mass_importer = MassImporter(db_session)
        self.window = tk.Toplevel(parent)
        self.window.title("Import Data from Excel")
        self.window.geometry("600x300")
        self.window.configure(padx=10, pady=10)

        # Initialize instance attributes
        self.label = None
        self.file_path_var = None
        self.entry = None
        self.browse_button = None
        self.import_button = None

        self.create_widgets()

    def create_widgets(self):
        """
        Create widgets for the Import window.
        """
        # Label and Entry for Excel file path
        self.label = ttk.Label(self.window, text="Select Excel File to Import:")
        self.label.pack(pady=10)

        self.file_path_var = tk.StringVar()
        self.entry = ttk.Entry(self.window, textvariable=self.file_path_var, width=60)
        self.entry.pack(pady=5)

        self.browse_button = ttk.Button(
            self.window, text="Browse", command=self.browse_file
        )
        self.browse_button.pack(pady=5)

        # Import Button
        self.import_button = ttk.Button(
            self.window,
            text="Import",
            command=self.import_data,
            width=15,
            style="Import.TButton",
        )
        self.import_button.pack(pady=20)

        # Configure style for Import button
        style = ttk.Style()
        style.configure("Import.TButton", background="#4CAF50", foreground="white")

    def browse_file(self):
        """
        Open a file dialog to select an Excel file.
        """
        file_path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel Files", "*.xlsx *.xls"), ("All Files", "*.*")],
        )
        if file_path:
            self.file_path_var.set(file_path)

    def import_data(self):
        """
        Trigger the mass import process.
        """
        excel_path = self.file_path_var.get().strip()
        if not excel_path:
            messagebox.showwarning(
                "No File Selected", "Please select an Excel file to import."
            )
            return

        try:
            # Call the mass import function
            self.mass_importer.mass_insert_from_excel(excel_path)
            messagebox.showinfo(
                "Import Successful", "Data imported successfully from Excel."
            )
            self.window.destroy()
        except ValueError as ve:
            logger.error(f"Import Error: {ve}")
            messagebox.showerror("Import Error", str(ve))
        except Exception as e:
            logger.exception(f"Error during import_data: {e}")
            messagebox.showerror("Error", f"An error occurred during import:\n{e}")
