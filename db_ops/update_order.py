# db_ops/update_order.py

from sqlalchemy.orm import Session

from db_ops.error_handler import InvalidDataError
from db_ops.models import WIP, Coldhead, Test
from logger import logger


class UpdateOrder:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def update_wip(self, wip_data: dict):
        try:
            wip = (
                self.db_session.query(WIP)
                .filter_by(wip_number=wip_data["wip_number"])
                .first()
            )
            if not wip:
                raise InvalidDataError(
                    f"WIP with number '{wip_data['wip_number']}' does not exist."
                )

            # Update fields
            wip.coldhead_id = wip_data["coldhead_id"]
            wip.displacer_serial_number = wip_data["displacer_serial_number"]
            wip.arrival_date = wip_data["arrival_date"]
            wip.teardown_date = wip_data["teardown_date"]
            wip.wip_status = wip_data["wip_status"]
            # Update other fields as necessary

            # Handle Coldhead Serial Number
            if (
                "coldhead_serial_number" in wip_data
                and wip_data["coldhead_serial_number"]
            ):
                coldhead = (
                    self.db_session.query(Coldhead)
                    .filter_by(
                        coldhead_serial_number=wip_data["coldhead_serial_number"]
                    )
                    .first()
                )
                if coldhead:
                    wip.coldhead_id = coldhead.coldhead_id
                else:
                    # Create a new Coldhead if it doesn't exist
                    new_coldhead = Coldhead(
                        coldhead_serial_number=wip_data["coldhead_serial_number"]
                    )
                    self.db_session.add(new_coldhead)
                    self.db_session.commit()
                    wip.coldhead_id = new_coldhead.coldhead_id

            self.db_session.commit()
            logger.info(f"WIP '{wip_data['wip_number']}' updated successfully.")
        except Exception as e:
            logger.exception(
                f"Error updating WIP '{wip_data.get('wip_number', 'N/A')}': {e}"
            )
            raise

    def update_test(self, test_data: dict):
        try:
            test = (
                self.db_session.query(Test)
                .filter_by(test_id=test_data["test_id"])
                .first()
            )
            if not test:
                raise InvalidDataError(
                    f"Test with ID '{test_data['test_id']}' does not exist."
                )

            # Update fields
            test.pass_fail = test_data["pass_fail"]
            test.notes = test_data["notes"]
            test.mode = test_data["mode"]
            test.turns = test_data["turns"]
            test.first_stage_heaters = test_data["first_stage_heaters"]
            test.second_stage_heater = test_data["second_stage_heater"]
            test.first_stage_temp = test_data["first_stage_temp"]
            test.second_stage_temp = test_data["second_stage_temp"]
            test.efficiency1 = test_data["efficiency1"]
            test.efficiency2 = test_data["efficiency2"]
            test.test_attempt = test_data["test_attempt"]
            test.test_date = test_data["test_date"]
            # Update other fields as necessary

            self.db_session.commit()
            logger.info(f"Test '{test_data['test_id']}' updated successfully.")
        except Exception as e:
            logger.exception(
                f"Error updating Test '{test_data.get('test_id', 'N/A')}': {e}"
            )
            raise
