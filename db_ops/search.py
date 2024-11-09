# db_ops/search.py

from sqlalchemy.orm import Session
from db_ops.error_handler import DatabaseError
from db_ops.models import WIP, Test, Coldhead, Displacer
from logger import logger


class SearchOperator:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        logger.info("SearchOperator initialized with SQLAlchemy session.")

    def flexible_search(
            self, coldhead_serial=None, wip_number=None, displacer_serial=None, test_id=None
    ):
        logger.debug(
            f"Starting flexible_search with parameters - "
            f"Coldhead Serial: '{coldhead_serial}', "
            f"WIP Number: '{wip_number}', "
            f"Displacer Serial: '{displacer_serial}', "
            f"Test ID: '{test_id}'."
        )
        try:
            filters = []
            if coldhead_serial:
                filters.append(Coldhead.serial_number == coldhead_serial)
                logger.debug(f"Added filter for Coldhead Serial Number: '{coldhead_serial}'.")
            if wip_number:
                filters.append(WIP.wip_number == wip_number)
                logger.debug(f"Added filter for WIP Number: '{wip_number}'.")
            if displacer_serial:
                filters.append(Displacer.displacer_serial_number == displacer_serial)
                logger.debug(f"Added filter for Displacer Serial Number: '{displacer_serial}'.")
            if test_id:
                filters.append(Test.test_id == test_id)
                logger.debug(f"Added filter for Test ID: '{test_id}'.")

            # Build the query using relationship attributes directly
            query = (
                self.db_session.query(WIP)
                .outerjoin(WIP.tests)  # Join on tests relationship directly
                .outerjoin(WIP.coldhead)  # Join on coldhead relationship directly
                .outerjoin(WIP.displacer)  # Join on displacer relationship directly
                .filter(*filters)
            )

            logger.debug("Built query with necessary joins.")
            results = query.all()
            logger.debug(f"Query executed. Retrieved {len(results)} result(s).")

            search_results = {}
            for wip in results:
                search_results[wip.wip_number] = {
                    "wip_number": wip.wip_number,
                    "coldhead_id": wip.coldhead_id,
                    "coldhead_serial_number": wip.coldhead.serial_number if wip.coldhead else None,
                    "displacer_serial_number": wip.displacer.displacer_serial_number if wip.displacer else None,
                    "arrival_date": wip.arrival_date,
                    "teardown_date": wip.teardown_date,
                    "wip_status": wip.status,
                    "displacer_status": wip.displacer.status if wip.displacer else None,
                    "displacer_notes": wip.displacer.notes if wip.displacer else None,
                    "initial_open_date": wip.displacer.initial_open_date if wip.displacer else None,
                    "tests": [
                        {
                            "test_id": test.test_id,
                            "test_type": test.name
                        }
                        for test in wip.tests  # Iterate over related tests
                    ],
                }
                logger.debug(f"Processed WIP '{wip.wip_number}' with test data.")

            logger.info(f"Flexible search completed with {len(search_results)} result(s).")
            return search_results

        except Exception as e:
            logger.error(f"Error during flexible_search: {e}", exc_info=True)
            raise DatabaseError(f"Error during flexible_search: {e}")

    def fetch_tests(self, wip_number):
        logger.debug(f"Fetching tests for WIP Number: '{wip_number}'.")
        try:
            wip = self.db_session.query(WIP).filter_by(wip_number=wip_number).first()
            if not wip:
                logger.warning(f"No WIP found with number '{wip_number}' for fetching tests.")
                return []
            tests = wip.tests
            logger.debug(f"Fetched {len(tests)} test(s) for WIP '{wip_number}'.")
            return tests
        except Exception as e:
            logger.error(f"Error during fetch_tests: {e}", exc_info=True)
            raise DatabaseError(f"Error during fetch_tests: {e}")
