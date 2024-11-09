# db_ops/new_order.py

from typing import List, Optional, Type

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db_ops.models import WIP, Test, Coldhead, Displacer
from logger import logger


class NewOrderInserter:
    def __init__(self, db_session: Session):
        """
        Initialize NewOrderInserter with a SQLAlchemy session.

        :param db_session: SQLAlchemy session object.
        """
        self.db_session = db_session
        logger.info("NewOrderInserter initialized with SQLAlchemy session")

    def generate_wip_placeholder(self) -> WIP:
        """
        Generates and inserts a new placeholder WIP record.

        :return: The newly created WIP object.
        """
        try:
            new_wip_number = self._get_next_wip_number()
            placeholder_wip = WIP(
                wip_number=new_wip_number,
                coldhead_serial_number=None,
                displacer_serial_number=None,
                arrival_date=None,
                teardown_date=None,
                wip_status="Placeholder",
                is_active=True,  # Soft delete flag
                # Initialize other fields as necessary
            )
            self.db_session.add(placeholder_wip)
            self.db_session.commit()
            logger.info(f"Generated and inserted new placeholder WIP: {new_wip_number}")
            return placeholder_wip
        except Exception as e:
            self.db_session.rollback()
            logger.exception(f"Error generating WIP placeholder: {e}")
            raise

    def _get_next_wip_number(self) -> str:
        """
        Determines the next WIP number based on existing records.

        :return: New WIP number as a string.
        """
        last_wip = self.db_session.query(WIP).order_by(WIP.wip_number.desc()).first()
        if last_wip and last_wip.wip_number.startswith("WIP"):
            last_number = int(last_wip.wip_number[3:])
            new_number = last_number + 1
        else:
            new_number = 1
        new_wip_number = f"WIP{new_number}"
        return new_wip_number

    def generate_displacer_placeholder(self) -> Displacer:
        """
        Generates and inserts a new placeholder Displacer record.

        :return: The newly created Displacer object.
        """
        try:
            new_displacer_serial = self._get_next_displacer_serial()
            placeholder_displacer = Displacer(
                displacer_serial_number=new_displacer_serial,
                status="Placeholder",
                notes=None,
                initial_open_date=None,
                is_active=True,  # Soft delete flag
                # Initialize other fields as necessary
            )
            self.db_session.add(placeholder_displacer)
            self.db_session.commit()
            logger.info(
                f"Generated and inserted new placeholder Displacer: {new_displacer_serial}"
            )
            return placeholder_displacer
        except Exception as e:
            self.db_session.rollback()
            logger.exception(f"Error generating Displacer placeholder: {e}")
            raise

    def _get_next_displacer_serial(self) -> str:
        """
        Determines the next Displacer serial number based on existing records.

        :return: New Displacer serial number as a string.
        """
        last_displacer = (
            self.db_session.query(Displacer)
            .order_by(Displacer.displacer_serial_number.desc())
            .first()
        )
        if last_displacer and last_displacer.displacer_serial_number.startswith("D"):
            last_number = int(last_displacer.displacer_serial_number[1:])
            new_number = last_number + 1
        else:
            new_number = 1
        new_displacer_serial = f"D{new_number}"
        return new_displacer_serial

    def insert_coldhead(self, coldhead_data: dict) -> Type[Coldhead] | Coldhead:
        """
        Inserts a new Coldhead record. If associated WIP is not provided,
        creates a placeholder WIP.

        :param coldhead_data: Dictionary containing Coldhead data.
                              Must include 'serial_number' and 'coldhead_id'.
        :return: The newly created Coldhead object.
        """
        try:
            # Check if Coldhead already exists
            existing_coldhead = (
                self.db_session.query(Coldhead)
                .filter_by(serial_number=coldhead_data["serial_number"])
                .first()
            )
            if existing_coldhead:
                logger.info(
                    f"Coldhead already exists: {existing_coldhead.serial_number}"
                )
                return existing_coldhead

            # Determine if WIP is provided
            wip_number = coldhead_data.get("wip_number")
            if not wip_number:
                # Reuse an existing inactive placeholder if available
                placeholder_wip = self._get_inactive_wip_placeholder()
                if placeholder_wip:
                    logger.info(
                        f"Reusing inactive placeholder WIP: {placeholder_wip.wip_number}"
                    )
                    placeholder_wip.is_active = True
                else:
                    placeholder_wip = self.generate_wip_placeholder()
                coldhead_data["wip_number"] = placeholder_wip.wip_number

            # Create and insert Coldhead
            coldhead = Coldhead(**coldhead_data)
            self.db_session.add(coldhead)
            self.db_session.commit()
            logger.info(
                f"Inserted new Coldhead: {coldhead.serial_number} associated with WIP: {coldhead.wip_number}"
            )
            return coldhead
        except IntegrityError as ie:
            self.db_session.rollback()
            logger.error(f"Integrity error during insert_coldhead: {ie}")
            raise
        except Exception as e:
            self.db_session.rollback()
            logger.exception(f"Error inserting Coldhead: {e}")
            raise

    def insert_displacer(self, displacer_data: dict) -> Type[Displacer] | Displacer:
        """
        Inserts a new Displacer record. If associated WIP is not provided,
        creates a placeholder WIP.

        :param displacer_data: Dictionary containing Displacer data.
                                Must include 'displacer_serial_number'.
        :return: The newly created Displacer object.
        """
        try:
            # Check if Displacer already exists
            existing_displacer = (
                self.db_session.query(Displacer)
                .filter_by(
                    displacer_serial_number=displacer_data["displacer_serial_number"]
                )
                .first()
            )
            if existing_displacer:
                logger.info(
                    f"Displacer already exists: {existing_displacer.displacer_serial_number}"
                )
                return existing_displacer

            # Determine if WIP is provided
            wip_number = displacer_data.get("wip_number")
            if not wip_number:
                # Reuse an existing inactive placeholder if available
                placeholder_wip = self._get_inactive_wip_placeholder()
                if placeholder_wip:
                    logger.info(
                        f"Reusing inactive placeholder WIP: {placeholder_wip.wip_number}"
                    )
                    placeholder_wip.is_active = True
                else:
                    placeholder_wip = self.generate_wip_placeholder()
                displacer_data["wip_number"] = placeholder_wip.wip_number

            # Create and insert Displacer
            displacer = Displacer(**displacer_data)
            self.db_session.add(displacer)
            self.db_session.commit()
            logger.info(
                f"Inserted new Displacer: {displacer.displacer_serial_number} associated with WIP: {displacer.wip_number}"
            )
            return displacer
        except IntegrityError as ie:
            self.db_session.rollback()
            logger.error(f"Integrity error during insert_displacer: {ie}")
            raise
        except Exception as e:
            self.db_session.rollback()
            logger.exception(f"Error inserting Displacer: {e}")
            raise

    def insert_wip(self, wip_data: dict) -> Type[WIP] | WIP:
        """
        Inserts a new WIP record independently.

        :param wip_data: Dictionary containing WIP data.
                         Must include 'wip_number' and other necessary fields.
        :return: The newly created WIP object.
        """
        try:
            # Check if WIP already exists
            existing_wip = (
                self.db_session.query(WIP)
                .filter_by(wip_number=wip_data["wip_number"])
                .first()
            )
            if existing_wip:
                logger.info(f"WIP already exists: {existing_wip.wip_number}")
                return existing_wip

            # Create and insert WIP
            wip = WIP(**wip_data)
            self.db_session.add(wip)
            self.db_session.commit()
            logger.info(f"Inserted new WIP: {wip.wip_number}")
            return wip
        except IntegrityError as ie:
            self.db_session.rollback()
            logger.error(f"Integrity error during insert_wip: {ie}")
            raise
        except Exception as e:
            self.db_session.rollback()
            logger.exception(f"Error inserting WIP: {e}")
            raise

    def insert_test(self, test_data: dict) -> Test:
        """
        Inserts a new Test record associated with a WIP.

        :param test_data: Dictionary containing Test data.
                          Must include 'test_id' (optional if auto-increment),
                          and 'wip_number'.
        :return: The newly created Test object.
        """
        try:
            # Ensure WIP exists
            wip_number = test_data.get("wip_number")
            if not wip_number:
                error_msg = "Test must be associated with a WIP number."
                logger.error(error_msg)
                raise ValueError(error_msg)

            existing_wip = (
                self.db_session.query(WIP).filter_by(wip_number=wip_number).first()
            )
            if not existing_wip:
                error_msg = f"WIP number {wip_number} does not exist."
                logger.error(error_msg)
                raise ValueError(error_msg)

            # Create and insert Test
            test = Test(**test_data)
            self.db_session.add(test)
            self.db_session.commit()
            logger.info(
                f"Inserted new Test: {test.test_id} associated with WIP: {test.wip_number}"
            )
            return test
        except IntegrityError as ie:
            self.db_session.rollback()
            logger.error(f"Integrity error during insert_test: {ie}")
            raise
        except Exception as e:
            self.db_session.rollback()
            logger.exception(f"Error inserting Test: {e}")
            raise

    def update_wip(self, wip_number: str, update_data: dict) -> Type[WIP]:
        """
        Updates an existing WIP record with new data.

        :param wip_number: The WIP number to update.
        :param update_data: Dictionary containing fields to update.
        :return: The updated WIP object.
        """
        try:
            wip = self.db_session.query(WIP).filter_by(wip_number=wip_number).first()
            if not wip:
                error_msg = f"WIP number {wip_number} does not exist."
                logger.error(error_msg)
                raise ValueError(error_msg)

            for key, value in update_data.items():
                setattr(wip, key, value)

            self.db_session.commit()
            logger.info(f"Updated WIP: {wip_number} with data: {update_data}")
            return wip
        except IntegrityError as ie:
            self.db_session.rollback()
            logger.error(f"Integrity error during update_wip: {ie}")
            raise
        except Exception as e:
            self.db_session.rollback()
            logger.exception(f"Error updating WIP: {e}")
            raise

    def update_coldhead(self, serial_number: str, update_data: dict) -> Type[Coldhead]:
        """
        Updates an existing Coldhead record with new data.

        :param serial_number: The Coldhead serial number to update.
        :param update_data: Dictionary containing fields to update.
        :return: The updated Coldhead object.
        """
        try:
            coldhead = (
                self.db_session.query(Coldhead)
                .filter_by(serial_number=serial_number)
                .first()
            )
            if not coldhead:
                error_msg = f"Coldhead serial number {serial_number} does not exist."
                logger.error(error_msg)
                raise ValueError(error_msg)

            for key, value in update_data.items():
                setattr(coldhead, key, value)

            self.db_session.commit()
            logger.info(f"Updated Coldhead: {serial_number} with data: {update_data}")
            return coldhead
        except IntegrityError as ie:
            self.db_session.rollback()
            logger.error(f"Integrity error during update_coldhead: {ie}")
            raise
        except Exception as e:
            self.db_session.rollback()
            logger.exception(f"Error updating Coldhead: {e}")
            raise

    def update_displacer(
        self, serial_number: str, update_data: dict
    ) -> Type[Displacer]:
        """
        Updates an existing Displacer record with new data.

        :param serial_number: The Displacer serial number to update.
        :param update_data: Dictionary containing fields to update.
        :return: The updated Displacer object.
        """
        try:
            displacer = (
                self.db_session.query(Displacer)
                .filter_by(displacer_serial_number=serial_number)
                .first()
            )
            if not displacer:
                error_msg = f"Displacer serial number {serial_number} does not exist."
                logger.error(error_msg)
                raise ValueError(error_msg)

            for key, value in update_data.items():
                setattr(displacer, key, value)

            self.db_session.commit()
            logger.info(f"Updated Displacer: {serial_number} with data: {update_data}")
            return displacer
        except IntegrityError as ie:
            self.db_session.rollback()
            logger.error(f"Integrity error during update_displacer: {ie}")
            raise
        except Exception as e:
            self.db_session.rollback()
            logger.exception(f"Error updating Displacer: {e}")
            raise

    def insert_new_order(
        self,
        coldhead_data: dict,
        wip_data: dict,
        displacer_data: Optional[dict] = None,
        test_data_list: Optional[List[dict]] = None,
    ) -> None:
        """
        Inserts a new order with Coldhead, WIP, Displacer, and Tests.

        :param coldhead_data: Dictionary containing Coldhead data.
        :param wip_data: Dictionary containing WIP data.
        :param displacer_data: Optional dictionary containing Displacer data.
        :param test_data_list: Optional list of dictionaries containing Test data.
        """
        try:
            # Insert WIP first
            wip = self.insert_wip(wip_data)

            # Insert Coldhead associated with WIP
            coldhead_data["wip_number"] = wip.wip_number
            self.insert_coldhead(coldhead_data)

            # Insert Displacer if data provided
            if displacer_data:
                displacer_data["wip_number"] = wip.wip_number
                self.insert_displacer(displacer_data)

            # Insert Tests if data provided
            if test_data_list:
                for test_data in test_data_list:
                    test_data["wip_number"] = wip.wip_number
                    self.insert_test(test_data)

            logger.info("New order inserted successfully.")
        except Exception as e:
            self.db_session.rollback()
            logger.exception(f"Error inserting new order: {e}")
            raise

    def _get_inactive_wip_placeholder(self) -> Optional[WIP]:
        """
        Retrieves an inactive placeholder WIP record if available.

        :return: An inactive WIP object or None.
        """
        try:
            inactive_wip = (
                self.db_session.query(WIP)
                .filter_by(wip_status="Placeholder", is_active=False)
                .first()
            )
            return inactive_wip
        except Exception as e:
            logger.exception(f"Error retrieving inactive WIP placeholder: {e}")
            return None
