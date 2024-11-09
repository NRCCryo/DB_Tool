# gui/detail_window.py

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List
from sqlalchemy.orm import Session
from db_ops.search import SearchOperator
from db_ops.update_order import UpdateOrder
from db_ops.error_handler import (
    DuplicateEntryError,
    EmptyUpdateError,
    InvalidDataError,
    DatabaseError,
)
from logger import logger


class DetailWindow:
    def __init__(
        self,
        parent: tk.Tk,
        wip_details: dict,
        test_list: List[dict],
        db_session: Session,
    ):
        """
        Initialize the DetailWindow.

        :param parent: The parent Tkinter window.
        :param wip_details: Dictionary containing WIP details.
        :param test_list: List of dictionaries containing test details.
        :param db_session: SQLAlchemy session object.
        """
        self.parent = parent
        self.db_session = db_session
        self.search_operator = SearchOperator(db_session)
        self.update_order = UpdateOrder(db_session)
        self.window = tk.Toplevel(parent)
        self.window.title(f"WIP Details - {wip_details.get('wip_number', 'N/A')}")
        self.window.geometry("1000x700")
        self.window.configure(padx=10, pady=10)

        self.wip_details = wip_details
        self.test_list = test_list
        self.save_button = None  # Declare instance attribute

        # Initialize instance attributes to None
        self.wip_frame = None
        self.tests_frame = None
        self.notebook = None

        # Entry fields for WIP details
        self.wip_number_entry = None
        self.coldhead_id_entry = None
        self.coldhead_serial_number_entry = None
        self.displacer_serial_number_entry = None
        self.arrival_date_entry = None
        self.teardown_date_entry = None
        self.wip_status_entry = None

        self.create_detail_fields()
        self.create_tests_tabs()
        self.create_save_button()

    def create_detail_fields(self):
        """
        Create and populate WIP detail fields.
        """
        # Frame for WIP details
        self.wip_frame = ttk.LabelFrame(
            self.window, text="WIP Details", padding=(10, 10)
        )
        self.wip_frame.pack(fill="x", expand=False, pady=10)

        # Expected keys in wip_details
        expected_keys = [
            "wip_number",
            "coldhead_id",
            "coldhead_serial_number",
            "displacer_serial_number",
            "arrival_date",
            "teardown_date",
            "wip_status"
            # Add other WIP fields as necessary
        ]

        for key in expected_keys:
            row = ttk.Frame(self.wip_frame)
            row.pack(fill="x", pady=2)

            label_key = ttk.Label(
                row, text=f"{key.replace('_', ' ').title()}:", width=25, anchor="w"
            )
            label_key.pack(side="left")

            entry = ttk.Entry(row, width=50)
            entry.insert(0, self.wip_details.get(key, ""))
            entry.pack(side="left", padx=10)

            # Assign to the correct instance attribute
            if key == "wip_number":
                self.wip_number_entry = entry
            elif key == "coldhead_id":
                self.coldhead_id_entry = entry
            elif key == "coldhead_serial_number":
                self.coldhead_serial_number_entry = entry
            elif key == "displacer_serial_number":
                self.displacer_serial_number_entry = entry
            elif key == "arrival_date":
                self.arrival_date_entry = entry
            elif key == "teardown_date":
                self.teardown_date_entry = entry
            elif key == "wip_status":
                self.wip_status_entry = entry
            # Add other fields as necessary

    def create_tests_tabs(self):
        """
        Create tabs for each associated test.
        """
        # Frame for Tests
        self.tests_frame = ttk.LabelFrame(
            self.window, text="Associated Tests", padding=(10, 10)
        )
        self.tests_frame.pack(fill="both", expand=True, pady=10)

        # Notebook for Test Tabs
        self.notebook = ttk.Notebook(self.tests_frame)
        self.notebook.pack(fill="both", expand=True)

        # Create up to three test tabs
        for i in range(1, 4):
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=f"Test {i}")

            # Check if the test exists
            if len(self.test_list) >= i:
                test_data = self.test_list[i - 1]
                self.populate_test_tab(tab, test_data)
            else:
                # Grey out the tab if no test exists
                self.disable_tab(i - 1)

    def populate_test_tab(self, tab: ttk.Frame, test_data: dict):
        """
        Populate a test tab with test data.

        :param tab: The tab to populate.
        :param test_data: Dictionary containing test details.
        """
        # Display Test details
        fields = [
            "test_id",
            "pass_fail",
            "notes",
            "mode",
            "turns",
            "first_stage_heaters",
            "second_stage_heater",
            "first_stage_temp",
            "second_stage_temp",
            "efficiency1",
            "efficiency2",
            "test_attempt",
            "test_date",
        ]

        # Initialize entry fields as instance attributes for easy access
        for idx, field in enumerate(fields):
            label = ttk.Label(tab, text=f"{field.replace('_', ' ').title()}:")
            label.grid(row=idx, column=0, sticky="w", pady=5, padx=5)
            entry = ttk.Entry(tab, width=50)
            entry.insert(0, test_data.get(field, "N/A"))
            entry.grid(row=idx, column=1, padx=10, pady=5)
            setattr(tab, f"{field}_entry", entry)  # Dynamically create attributes

        # Add a "Save Test" button
        save_test_button = ttk.Button(
            tab,
            text="Save Test",
            command=lambda t=tab: self.save_test(t),
            width=15,
            style="SaveTest.TButton",
        )
        save_test_button.grid(row=len(fields), column=0, columnspan=2, pady=10)

        # Configure style for Save Test button
        style = ttk.Style()
        style.configure("SaveTest.TButton", background="#4CAF50", foreground="white")

    def disable_tab(self, tab_index: int):
        """
        Disable a tab if no test exists.

        :param tab_index: Index of the tab to disable.
        """
        self.notebook.tab(tab_index, state="disabled")

    def create_save_button(self):
        """
        Create the Save All Changes button.
        """
        self.save_button = ttk.Button(
            self.window,
            text="Save All Changes",
            command=self.save_all_changes,
            width=25,
            style="SaveAll.TButton",
        )
        self.save_button.pack(pady=20)

        # Configure style for Save All button
        style = ttk.Style()
        style.configure("SaveAll.TButton", background="#4CAF50", foreground="white")

    def save_test(self, tab: ttk.Frame):
        """
        Save changes made to a specific test.

        :param tab: The test tab containing updated data.
        """
        try:
            # Collect updated Test data from the specific tab
            test_id = getattr(tab, "test_id_entry").get().strip()
            if not test_id or test_id == "N/A":
                messagebox.showerror(
                    "Input Error", "Test ID is required to save changes."
                )
                logger.warning("Test ID missing in save_test.")
                return

            test_data = {
                "test_id": int(getattr(tab, "test_id_entry").get().strip()),
                "pass_fail": getattr(tab, "pass_fail_entry").get().strip() or "Pending",
                "notes": getattr(tab, "notes_entry").get().strip(),
                "mode": getattr(tab, "mode_entry").get().strip(),
                "turns": int(getattr(tab, "turns_entry").get().strip() or 0),
                "first_stage_heaters": float(
                    getattr(tab, "first_stage_heaters_entry").get().strip() or 0.0
                ),
                "second_stage_heater": float(
                    getattr(tab, "second_stage_heater_entry").get().strip() or 0.0
                ),
                "first_stage_temp": float(
                    getattr(tab, "first_stage_temp_entry").get().strip() or 0.0
                ),
                "second_stage_temp": float(
                    getattr(tab, "second_stage_temp_entry").get().strip() or 0.0
                ),
                "efficiency1": float(
                    getattr(tab, "efficiency1_entry").get().strip() or 0.0
                ),
                "efficiency2": float(
                    getattr(tab, "efficiency2_entry").get().strip() or 0.0
                ),
                "test_attempt": int(
                    getattr(tab, "test_attempt_entry").get().strip() or 1
                ),
                "test_date": getattr(tab, "test_date_entry").get().strip() or None,
                "wip_number": self.wip_number_entry.get().strip(),
                "coldhead_serial_number": self.coldhead_serial_number_entry.get().strip(),
                "displacer_serial_number": self.displacer_serial_number_entry.get().strip(),
            }

            # Perform the update
            self.update_order.update_test(test_data)
            messagebox.showinfo("Success", "Test updated successfully.")
            logger.info(f"Test '{test_data['test_id']}' updated successfully.")
            # Optionally, refresh the treeview or other components if needed
        except ValueError as ve:
            logger.error(f"Data type conversion error: {ve}")
            messagebox.showerror("Data Error", f"Invalid data type: {ve}")
        except (
            DuplicateEntryError,
            EmptyUpdateError,
            InvalidDataError,
            DatabaseError,
        ) as e:
            logger.error(f"Error during save_test: {e}")
            messagebox.showerror("Error", str(e))
        except Exception as e:
            logger.exception(f"Error during save_test: {e}")
            messagebox.showerror(
                "Error", f"An unexpected error occurred while saving the test:\n{e}"
            )

    def save_all_changes(self):
        """
        Save all changes made to the WIP details and associated tests.
        """
        try:
            # Collect updated WIP data
            updated_wip = {
                "wip_number": self.wip_number_entry.get().strip(),
                "coldhead_id": self.coldhead_id_entry.get().strip(),
                "coldhead_serial_number": self.coldhead_serial_number_entry.get().strip(),
                "displacer_serial_number": self.displacer_serial_number_entry.get().strip(),
                "arrival_date": self.arrival_date_entry.get().strip() or None,
                "teardown_date": self.teardown_date_entry.get().strip() or None,
                "wip_status": self.wip_status_entry.get().strip(),
                # Add other WIP fields if necessary
            }

            # Validate required fields
            required_fields = [
                "wip_number",
                "coldhead_id",
                "coldhead_serial_number",
                "displacer_serial_number",
            ]
            for field in required_fields:
                if not updated_wip.get(field):
                    messagebox.showerror(
                        "Input Error", f"{field.replace('_', ' ').title()} is required."
                    )
                    logger.warning(f"{field} missing in save_all_changes.")
                    return

            # Collect updated Test data
            updated_tests = []
            for i in range(1, 4):
                tab = self.notebook.tabs()[i - 1]
                tab_widget = self.notebook.nametowidget(tab)
                # Check if the tab is enabled
                tab_state = self.notebook.tab(tab, "state")
                if tab_state == "disabled":
                    continue  # Skip disabled tabs

                # Ensure the tab has 'test_id_entry' attribute
                if hasattr(tab_widget, "test_id_entry"):
                    test_id = getattr(tab_widget, "test_id_entry").get().strip()
                    if test_id and test_id != "N/A":
                        test_data = {
                            "test_id": int(
                                getattr(tab_widget, "test_id_entry").get().strip()
                            ),
                            "pass_fail": getattr(tab_widget, "pass_fail_entry")
                            .get()
                            .strip()
                            or "Pending",
                            "notes": getattr(tab_widget, "notes_entry").get().strip(),
                            "mode": getattr(tab_widget, "mode_entry").get().strip(),
                            "turns": int(
                                getattr(tab_widget, "turns_entry").get().strip() or 0
                            ),
                            "first_stage_heaters": float(
                                getattr(tab_widget, "first_stage_heaters_entry")
                                .get()
                                .strip()
                                or 0.0
                            ),
                            "second_stage_heater": float(
                                getattr(tab_widget, "second_stage_heater_entry")
                                .get()
                                .strip()
                                or 0.0
                            ),
                            "first_stage_temp": float(
                                getattr(tab_widget, "first_stage_temp_entry")
                                .get()
                                .strip()
                                or 0.0
                            ),
                            "second_stage_temp": float(
                                getattr(tab_widget, "second_stage_temp_entry")
                                .get()
                                .strip()
                                or 0.0
                            ),
                            "efficiency1": float(
                                getattr(tab_widget, "efficiency1_entry").get().strip()
                                or 0.0
                            ),
                            "efficiency2": float(
                                getattr(tab_widget, "efficiency2_entry").get().strip()
                                or 0.0
                            ),
                            "test_attempt": int(
                                getattr(tab_widget, "test_attempt_entry").get().strip()
                                or 1
                            ),
                            "test_date": getattr(tab_widget, "test_date_entry")
                            .get()
                            .strip()
                            or None,
                            "wip_number": updated_wip["wip_number"],
                            "coldhead_serial_number": updated_wip[
                                "coldhead_serial_number"
                            ],
                            "displacer_serial_number": updated_wip[
                                "displacer_serial_number"
                            ],
                        }
                        updated_tests.append(test_data)

            # Perform the updates
            self.update_order.update_wip(updated_wip)
            logger.info(f"WIP '{updated_wip['wip_number']}' updated successfully.")
            for test_data in updated_tests:
                self.update_order.update_test(test_data)
                logger.info(f"Test '{test_data['test_id']}' updated successfully.")

            messagebox.showinfo("Success", "All changes saved successfully.")
            logger.info("All changes saved successfully.")
            self.window.destroy()
        except ValueError as ve:
            logger.error(f"Data type conversion error: {ve}")
            messagebox.showerror("Data Error", f"Invalid data type: {ve}")
        except (
            DuplicateEntryError,
            EmptyUpdateError,
            InvalidDataError,
            DatabaseError,
        ) as e:
            logger.error(f"Error during save_all_changes: {e}")
            messagebox.showerror("Error", str(e))
        except Exception as e:
            logger.exception(f"Error during save_all_changes: {e}")
            messagebox.showerror(
                "Error", f"An unexpected error occurred while saving changes:\n{e}"
            )
