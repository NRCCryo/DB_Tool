# gui/add_test_window.py

import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox

from sqlalchemy.orm import Session

from db_ops.error_handler import EmptyUpdateError, InvalidDataError, DatabaseError
from db_ops.models import Test, WIP, Coldhead
from logger import logger


class AddTestWindow:
    def __init__(self, parent: tk.Tk, db_session: Session):
        """
        Initialize the AddTestWindow.

        :param parent: The parent Tkinter window.
        :param db_session: SQLAlchemy session object.
        """
        self.parent = parent
        self.db_session = db_session
        self.window = tk.Toplevel(parent)
        self.window.title("Add New Test")
        self.window.geometry("500x600")
        self.window.configure(padx=10, pady=10)

        # Initialize instance attributes
        self.frame = None
        self.test_id_label = None  # Typically auto-generated, so no input
        self.wip_number_label = None
        self.wip_number_input = None
        self.coldhead_serial_label = None
        self.coldhead_serial_input = None
        # Add other test-related fields
        self.pass_fail_label = None
        self.pass_fail_input = None
        self.notes_label = None
        self.notes_entry = None
        self.mode_label = None
        self.mode_entry = None
        # ... other fields
        self.test_date_label = None
        self.test_date_entry = None
        self.insert_button = None

        self.create_widgets()

    def create_widgets(self):
        """
        Create widgets for the Test insertion form.
        """
        self.frame = ttk.Frame(self.window)
        self.frame.pack(fill="both", expand=True, pady=20)

        # WIP Number
        self.wip_number_label = ttk.Label(self.frame, text="WIP Number:")
        self.wip_number_label.pack(pady=5)
        self.wip_number_input = ttk.Entry(self.frame, width=40)
        self.wip_number_input.pack(pady=5)

        # Optional Coldhead Serial Number
        self.coldhead_serial_label = ttk.Label(
            self.frame, text="Coldhead Serial Number (Optional):"
        )
        self.coldhead_serial_label.pack(pady=5)
        self.coldhead_serial_input = ttk.Entry(self.frame, width=40)
        self.coldhead_serial_input.pack(pady=5)

        # Pass/Fail
        self.pass_fail_label = ttk.Label(self.frame, text="Pass/Fail:")
        self.pass_fail_label.pack(pady=5)
        self.pass_fail_input = ttk.Combobox(
            self.frame, values=["Pass", "Fail", "Pending"], state="readonly"
        )
        self.pass_fail_input.current(2)  # Default to 'Pending'
        self.pass_fail_input.pack(pady=5)

        # Notes (Optional)
        self.notes_label = ttk.Label(self.frame, text="Notes (Optional):")
        self.notes_label.pack(pady=5)
        self.notes_entry = ttk.Entry(self.frame, width=40)
        self.notes_entry.pack(pady=5)

        # Mode
        self.mode_label = ttk.Label(self.frame, text="Mode:")
        self.mode_label.pack(pady=5)
        self.mode_entry = ttk.Entry(self.frame, width=40)
        self.mode_entry.pack(pady=5)

        # Test Date (Optional)
        self.test_date_label = ttk.Label(
            self.frame, text="Test Date (Optional, YYYY-MM-DD):"
        )
        self.test_date_label.pack(pady=5)
        self.test_date_entry = ttk.Entry(self.frame, width=40)
        self.test_date_entry.pack(pady=5)

        # Insert Button
        self.insert_button = ttk.Button(
            self.frame,
            text="Add Test",
            command=self.insert_test,
            style="Insert.TButton",
        )
        self.insert_button.pack(pady=20)

        # Configure style for Insert button
        style = ttk.Style()
        style.configure("Insert.TButton", background="#4CAF50", foreground="white")

    def insert_test(self):
        """
        Insert a new Test into the database.
        """
        wip_number = self.wip_number_input.get().strip()
        coldhead_serial = self.coldhead_serial_input.get().strip() or None
        pass_fail = self.pass_fail_input.get().strip()
        notes = self.notes_entry.get().strip() or None
        mode = self.mode_entry.get().strip()
        test_date_str = self.test_date_entry.get().strip() or None

        # Validate required fields
        if not wip_number:
            messagebox.showerror("Input Error", "WIP Number is required.")
            return

        if not mode:
            messagebox.showerror("Input Error", "Mode is required.")
            return

        # Validate date format if provided
        test_date = None
        if test_date_str:
            try:
                test_date = datetime.strptime(test_date_str, "%Y-%m-%d").date()
            except ValueError:
                messagebox.showerror(
                    "Input Error", "Test Date must be in YYYY-MM-DD format."
                )
                return

        try:
            # Check if WIP exists
            wip = self.db_session.query(WIP).filter_by(wip_number=wip_number).first()
            if not wip:
                raise InvalidDataError(f"No WIP found with number '{wip_number}'.")

            # Handle Coldhead Serial Number if provided
            coldhead_id = None
            if coldhead_serial:
                coldhead = (
                    self.db_session.query(Coldhead)
                    .filter_by(coldhead_serial_number=coldhead_serial)
                    .first()
                )
                if not coldhead:
                    raise InvalidDataError(
                        f"No Coldhead found with Serial Number '{coldhead_serial}'."
                    )
                coldhead_id = coldhead.coldhead_id

            # Create new Test instance
            new_test = Test(
                wip_number=wip_number,
                coldhead_id=coldhead_id
                if coldhead_id
                else wip.coldhead_id,  # Fallback to WIP's coldhead_id
                pass_fail=pass_fail,
                notes=notes,
                mode=mode,
                test_date=test_date
                # Add other fields as necessary
            )

            self.db_session.add(new_test)
            self.db_session.commit()
            logger.info(f"Inserted new Test for WIP: {wip_number}")
            messagebox.showinfo(
                "Success",
                f"Test added successfully with ID: {new_test.test_id}",
            )
            self.window.destroy()
        except InvalidDataError as ide:
            logger.error(ide)
            messagebox.showerror("Invalid Data", str(ide))
        except (EmptyUpdateError, DatabaseError) as e:
            logger.error(e)
            messagebox.showerror("Error", str(e))
        except Exception as e:
            self.db_session.rollback()
            logger.exception(f"Unexpected error during Test insertion: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred:\n{e}")
