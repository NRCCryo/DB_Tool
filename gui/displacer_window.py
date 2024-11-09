# gui/displacer_window.py

import tkinter as tk
from tkinter import ttk, messagebox
from db_ops.models import Displacer
from logger import logger
from sqlalchemy.orm import Session

class DisplacerWindow(tk.Toplevel):
    def __init__(self, parent, session: Session):
        super().__init__(parent)
        self.session = session
        self.title("Insert New Displacer")
        self.geometry("400x300")
        self.setup_ui()
        logger.info("DisplacerWindow initialized.")

    def setup_ui(self):
        ttk.Label(self, text="Displacer Serial Number:").pack(pady=5)
        self.displacer_serial_input = ttk.Entry(self)
        self.displacer_serial_input.pack(pady=5)

        ttk.Label(self, text="Status:").pack(pady=5)
        self.status_input = ttk.Entry(self)
        self.status_input.pack(pady=5)

        ttk.Label(self, text="Notes:").pack(pady=5)
        self.notes_input = ttk.Entry(self)
        self.notes_input.pack(pady=5)

        ttk.Label(self, text="Initial Open Date (YYYY-MM-DD):").pack(pady=5)
        self.initial_open_date_input = ttk.Entry(self)
        self.initial_open_date_input.pack(pady=5)

        submit_button = ttk.Button(self, text="Submit", command=self.create_displacer)
        submit_button.pack(pady=10)

    def create_displacer(self):
        try:
            displacer_serial = self.displacer_serial_input.get().strip()
            status = self.status_input.get().strip()
            notes = self.notes_input.get().strip()
            initial_open_date = self.initial_open_date_input.get().strip()

            if not displacer_serial:
                raise ValueError("Displacer Serial Number is required.")

            # Check if Displacer already exists
            existing_displacer = self.session.query(Displacer).filter_by(displacer_serial_number=displacer_serial).first()
            if existing_displacer:
                raise ValueError("Displacer with this Serial Number already exists.")

            # Create new Displacer
            new_displacer = Displacer(
                displacer_serial_number=displacer_serial,
                status=status,
                notes=notes,
                initial_open_date=initial_open_date
            )
            self.session.add(new_displacer)
            self.session.commit()
            logger.info(f"Created new Displacer with Serial Number '{displacer_serial}' and ID {new_displacer.displacer_id}.")

            messagebox.showinfo("Success", "New displacer inserted successfully.")
            self.destroy()

        except ValueError as ve:
            logger.error(f"Value error: {ve}")
            messagebox.showerror("Input Error", str(ve))
        except Exception as e:
            logger.error(f"Unexpected error during displacer creation: {e}")
            messagebox.showerror("Error", f"Failed to insert displacer:\n{e}")
