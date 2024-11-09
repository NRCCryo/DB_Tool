# gui/coldhead_window.py

import tkinter as tk
from tkinter import ttk, messagebox
from sqlalchemy.orm import Session
from db_ops.models import Coldhead, Displacer
from db_ops.error_handler import DuplicateEntryError, InvalidDataError, DatabaseError
from logger import logger


class ColdheadWindow:
    def __init__(self, parent: tk.Tk, db_session: Session):
        self.parent = parent
        self.db_session = db_session
        self.window = tk.Toplevel(parent)
        self.window.title("Insert New Coldhead")
        self.window.geometry("400x450")
        self.window.configure(padx=10, pady=10)

        # Initialize instance attributes
        self.frame = None
        self.serial_number_label = None
        self.serial_number_entry = None
        self.displacer_serial_label = None
        self.displacer_serial_input = None
        self.insert_button = None

        self.create_widgets()

    def create_widgets(self):
        self.frame = ttk.Frame(self.window)
        self.frame.pack(fill="both", expand=True, pady=20)

        # Coldhead Serial Number
        self.serial_number_label = ttk.Label(self.frame, text="Coldhead Serial Number:")
        self.serial_number_label.pack(pady=5)
        self.serial_number_entry = ttk.Entry(self.frame, width=40)
        self.serial_number_entry.pack(pady=5)

        # Optional Displacer Serial Number
        self.displacer_serial_label = ttk.Label(
            self.frame, text="Displacer Serial Number (Optional):"
        )
        self.displacer_serial_label.pack(pady=5)
        self.displacer_serial_input = ttk.Entry(self.frame, width=40)
        self.displacer_serial_input.pack(pady=5)

        # Insert Button
        self.insert_button = ttk.Button(
            self.frame,
            text="Insert Coldhead",
            command=self.insert_coldhead,
            style="Insert.TButton",
        )
        self.insert_button.pack(pady=20)

        # Configure style for Insert button
        style = ttk.Style()
        style.configure("Insert.TButton", background="#4CAF50", foreground="white")

    def insert_coldhead(self):
        serial_number = self.serial_number_entry.get().strip()
        displacer_serial = self.displacer_serial_input.get().strip() or None

        if not serial_number:
            messagebox.showerror("Input Error", "Coldhead Serial Number is required.")
            return

        try:
            existing_coldhead = (
                self.db_session.query(Coldhead)
                .filter_by(coldhead_serial_number=serial_number)
                .first()
            )
            if existing_coldhead:
                raise DuplicateEntryError(
                    f"Coldhead with Serial Number '{serial_number}' already exists."
                )

            displacer_id = None
            if displacer_serial:
                displacer = (
                    self.db_session.query(Displacer)
                    .filter_by(displacer_serial_number=displacer_serial)
                    .first()
                )
                if not displacer:
                    raise InvalidDataError(
                        f"No Displacer found with Serial Number '{displacer_serial}'."
                    )
                displacer_id = displacer.displacer_id

            new_coldhead = Coldhead(
                coldhead_serial_number=serial_number, displacer_id=displacer_id
            )

            self.db_session.add(new_coldhead)
            self.db_session.commit()
            logger.info(f"Inserted new Coldhead with Serial Number: {serial_number}")
            messagebox.showinfo(
                "Success",
                f"Coldhead inserted successfully with ID: {new_coldhead.coldhead_id}",
            )
            self.window.destroy()
        except DuplicateEntryError as dee:
            logger.error(dee)
            messagebox.showerror("Duplicate Entry", str(dee))
        except InvalidDataError as ide:
            logger.error(ide)
            messagebox.showerror("Invalid Data", str(ide))
        except DatabaseError as db_err:
            logger.error(db_err)
            messagebox.showerror("Database Error", str(db_err))
        except Exception as e:
            self.db_session.rollback()
            logger.exception(f"Unexpected error during Coldhead insertion: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred:\n{e}")
