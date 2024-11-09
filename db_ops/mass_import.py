# db_ops/mass_import.py

import pandas as pd
from sqlalchemy.orm import Session
from db_ops.new_order import NewOrderInserter
from logger import logger
from typing import Dict, Any, Optional, List  # Import Optional and List


class MassImporter:
    def __init__(self, db_session: Session):
        """
        Initialize MassImporter with a SQLAlchemy session.

        :param db_session: SQLAlchemy session object.
        """
        self.db_session = db_session
        self.new_order_inserter = NewOrderInserter(db_session)
        logger.info("MassImporter initialized with SQLAlchemy session")

    def mass_insert_from_excel(self, excel_path: str) -> None:
        """
        Imports data from an Excel file and inserts it into the database.

        :param excel_path: Path to the Excel file.
        """
        try:
            # Load the Excel file
            df = pd.read_excel(excel_path)
            logger.info(f"Loaded Excel file from {excel_path}")

            # Ensure the required columns are present in the DataFrame
            required_columns = {
                "Arrival_Date",
                "Coldhead_Serial_Number",
                "WIP",
                "Displacer_Serial_Number",
                "Initial_Open_Date",
            }
            if not required_columns.issubset(df.columns):
                error_msg = (
                    f"Excel file must contain columns: {', '.join(required_columns)}"
                )
                logger.error(error_msg)
                raise ValueError(error_msg)

            # Identify test columns (assuming Test1_PassFail, Test1_Mode, etc.)
            test_columns: Dict[str, Dict[str, str]] = {}
            for col in df.columns:
                if "Test" in col and ("PassFail" in col or "Mode" in col):
                    test_num = "".join(filter(str.isdigit, col))
                    if test_num:
                        if test_num not in test_columns:
                            test_columns[test_num] = {}
                        if "PassFail" in col:
                            test_columns[test_num]["PassFail"] = col
                        elif "Mode" in col:
                            test_columns[test_num]["Mode"] = col

            # Iterate over the DataFrame and insert each record
            for _, row in df.iterrows():
                coldhead_serial = None  # Initialize before try block
                try:
                    # Extract WIP and related data
                    arrival_date = row["Arrival_Date"]
                    coldhead_serial = row["Coldhead_Serial_Number"]
                    wip_number = row["WIP"]
                    displacer_serial = row.get("Displacer_Serial_Number", None)
                    initial_open_date = row.get("Initial_Open_Date", None)

                    coldhead_data: Dict[str, Any] = {
                        "serial_number": coldhead_serial,
                        # Add other Coldhead fields if necessary
                    }

                    wip_data: Dict[str, Any] = {
                        "wip_number": wip_number if pd.notnull(wip_number) else None,
                        "arrival_date": arrival_date
                        if pd.notnull(arrival_date)
                        else None,
                        # Add other WIP fields if necessary
                    }

                    # Handle Displacer data
                    displacer_data: Optional[Dict[str, Any]] = None
                    if pd.notnull(displacer_serial) or pd.notnull(initial_open_date):
                        displacer_data = {
                            "displacer_serial_number": displacer_serial
                            if pd.notnull(displacer_serial)
                            else None,
                            "initial_open_date": initial_open_date
                            if pd.notnull(initial_open_date)
                            else None,
                            # Add other Displacer fields if necessary
                        }

                    # Handle tests
                    test_data_list: Optional[List[Dict[str, Any]]] = []
                    for test_num, cols in test_columns.items():
                        pass_fail = row.get(cols.get("PassFail"), None)
                        mode = row.get(cols.get("Mode"), None)
                        if pd.notnull(pass_fail) or pd.notnull(mode):
                            test_data = {
                                "pass_fail": pass_fail
                                if pd.notnull(pass_fail)
                                else "Pending",
                                "notes": "",  # Populate if available
                                "mode": mode if pd.notnull(mode) else "",
                                "turns": 0,  # Default or extract if available
                                "first_stage_heaters": 0.0,  # Default or extract if available
                                "second_stage_heater": 0.0,  # Default or extract if available
                                "first_stage_temp": 0.0,  # Default or extract if available
                                "second_stage_temp": 0.0,  # Default or extract if available
                                "efficiency1": 0.0,  # Default or extract if available
                                "efficiency2": 0.0,  # Default or extract if available
                                "test_attempt": 1,  # Default or extract if available
                                "test_date": None,  # Can be set to current date if desired
                                # 'wip_number' will be set in inserter
                            }
                            test_data_list.append(test_data)

                    # Use the NewOrderInserter to insert the new order
                    self.new_order_inserter.insert_new_order(
                        coldhead_data=coldhead_data,
                        wip_data=wip_data,
                        displacer_data=displacer_data,
                        test_data_list=test_data_list if test_data_list else None,
                    )
                except Exception as e:
                    # Safeguard to check if 'coldhead_serial' is defined
                    if coldhead_serial:
                        logger.exception(
                            f"Error inserting record for Coldhead Serial Number {coldhead_serial}: {e}"
                        )
                    else:
                        logger.exception(
                            f"Error inserting record: Coldhead Serial Number is undefined. Error: {e}"
                        )
                    continue  # Skip to the next record
        except FileNotFoundError as fnfe:
            logger.exception(f"Excel file not found: {fnfe}")
            raise
        except pd.errors.EmptyDataError as ede:
            logger.exception(f"Excel file is empty: {ede}")
            raise
        except Exception as e:
            logger.exception(f"Error loading or processing the Excel file: {e}")
            raise
