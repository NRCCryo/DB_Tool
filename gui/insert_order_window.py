# gui/insert_order_window.py

import tkinter as tk
from tkinter import ttk, messagebox
from db_ops.models import Coldhead, Displacer, WIP
from logger import logger
from sqlalchemy.orm import Session
import datetime

class InsertOrderWindow(tk.Toplevel):
    def __init__(self, parent, session: Session):
        super().__init__(parent)
        self.session = session
        self.title("Insert New Order")
        self.geometry("400x400")
        self.setup_ui()
        logger.info("InsertOrderWindow initialized.")

    def setup_ui(self):
        # Define all necessary widgets
        ttk.Label(self, text="WIP Number:").pack(pady=5)
        self.wip_number_input = ttk.Entry(self)
        self.wip_number_input.pack(pady=5)

        ttk.Label(self, text="Coldhead Serial Number:").pack(pady=5)
        self.coldhead_serial_input = ttk.Entry(self)
        self.coldhead_serial_input.pack(pady=5)

        ttk.Label(self, text="Displacer Serial Number:").pack(pady=5)
        self.displacer_serial_input = ttk.Entry(self)
        self.displacer_serial_input.pack(pady=5)

        ttk.Label(self, text="Arrival Date (YYYY-MM-DD):").pack(pady=5)
        self.arrival_date_input = ttk.Entry(self)
        self.arrival_date_input.pack(pady=5)

        ttk.Label(self, text="Teardown Date (YYYY-MM-DD):").pack(pady=5)
        self.teardown_date_input = ttk.Entry(self)
        self.teardown_date_input.pack(pady=5)

        ttk.Label(self, text="Test ID:").pack(pady=5)
        self.test_id_input = ttk.Entry(self)
        self.test_id_input.pack(pady=5)

        submit_button = ttk.Button(self, text="Submit", command=self.create_order)
        submit_button.pack(pady=10)

    def create_order(self):
        try:
            wip_number = self.wip_number_input.get().strip()
            coldhead_serial = self.coldhead_serial_input.get().strip()
            displacer_serial = self.displacer_serial_input.get().strip()
            arrival_date = self.arrival_date_input.get().strip()  # Optional
            teardown_date = self.teardown_date_input.get().strip()  # Optional
            test_id = self.test_id_input.get().strip()  # Optional

            # Only validate required fields
            if not all([wip_number, coldhead_serial, displacer_serial]):
                raise ValueError("Please fill in all required fields.")

            # Remaining code for creating coldhead, displacer, and WIP entries remains the same
            # Create Coldhead entry
            coldhead = self.session.query(Coldhead).filter_by(serial_number=coldhead_serial).first()
            if not coldhead:
                coldhead = Coldhead(serial_number=coldhead_serial)
                self.session.add(coldhead)
                self.session.commit()
                logger.info(
                    f"Created new Coldhead with Serial Number '{coldhead_serial}' and ID {coldhead.coldhead_id}.")

            # Create Displacer entry
            displacer = self.session.query(Displacer).filter_by(displacer_serial_number=displacer_serial).first()
            if not displacer:
                displacer = Displacer(displacer_serial_number=displacer_serial)
                self.session.add(displacer)
                self.session.commit()
                logger.info(
                    f"Created new Displacer with Serial Number '{displacer_serial}' and ID {displacer.displacer_id}.")

            # Create WIP entry
            new_wip = WIP(
                test_id=int(test_id) if test_id else None,
                coldhead_id=coldhead.coldhead_id,
                displacer_id=displacer.displacer_id,
                wip_number=wip_number,
                arrival_date=arrival_date if arrival_date else None,
                teardown_date=teardown_date if teardown_date else None
            )
            self.session.add(new_wip)
            self.session.commit()
            logger.info(f"Inserted new WIP with WIP Number '{wip_number}'.")

            messagebox.showinfo("Success", "New order inserted successfully.")
            self.destroy()

        except ValueError as ve:
            logger.error(f"Value error: {ve}")
            messagebox.showerror("Input Error", str(ve))
        except Exception as e:
            logger.error(f"Unexpected error during order creation: {e}")
            messagebox.showerror("Error", f"Failed to insert order:\n{e}")

    def create_order_with_data(self, wip_number, coldhead_serial, displacer_serial, arrival_date, teardown_date,
                               test_id):
        try:
            if not all([wip_number, coldhead_serial, displacer_serial, arrival_date, test_id]):
                raise ValueError("Please fill in all required fields.")

            # Convert arrival_date string to datetime.date object
            try:
                arrival_date_obj = datetime.datetime.strptime(arrival_date, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError("Arrival Date must be in YYYY-MM-DD format.")

            # Convert teardown_date string to datetime.date object if provided
            if teardown_date:
                try:
                    teardown_date_obj = datetime.datetime.strptime(teardown_date, "%Y-%m-%d").date()
                except ValueError:
                    raise ValueError("Teardown Date must be in YYYY-MM-DD format.")
            else:
                teardown_date_obj = None

            # Fetch or create Coldhead
            coldhead = self.session.query(Coldhead).filter_by(serial_number=coldhead_serial).first()
            if not coldhead:
                coldhead = Coldhead(serial_number=coldhead_serial)
                self.session.add(coldhead)
                self.session.commit()
                logger.info(
                    f"Created new Coldhead with Serial Number '{coldhead_serial}' and ID {coldhead.coldhead_id}."
                )

            # Fetch or create Displacer
            displacer = self.session.query(Displacer).filter_by(displacer_serial_number=displacer_serial).first()
            if not displacer:
                displacer = Displacer(displacer_serial_number=displacer_serial)
                self.session.add(displacer)
                self.session.commit()
                logger.info(
                    f"Created new Displacer with Serial Number '{displacer_serial}' and ID {displacer.displacer_id}."
                )

            # Create WIP
            new_wip = WIP(
                test_id=int(test_id),
                coldhead_id=coldhead.coldhead_id,
                displacer_id=displacer.displacer_id,
                wip_number=wip_number,
                arrival_date=arrival_date_obj,
                teardown_date=teardown_date_obj
            )
            self.session.add(new_wip)
            self.session.commit()
            logger.info(f"Inserted new WIP with WIP Number '{wip_number}'.")

        except ValueError as ve:
            logger.error(f"Value error: {ve}")
            raise ve
        except Exception as e:
            logger.error(f"Unexpected error during order creation: {e}")
            raise e