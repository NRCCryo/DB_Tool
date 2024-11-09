# db_ops/search.py

from db_mngt.fetch_data import DataFetcher
from logger import logger  # Import the logger


class SearchOperator:
    def __init__(self):
        self.data_fetcher = DataFetcher()
        logger.info("SearchOperator initialized")

    def flexible_search(
        self,
        coldhead_serial=None,
        wip_number=None,
        displacer_serial=None,
        test_id=None,
        serial_number=None,
    ):
        """
        Flexible search function that accepts multiple optional arguments.
        Returns aggregated results from related tables.
        """
        # Build conditions based on input
        conditions = {}
        or_conditions = []

        if coldhead_serial:
            conditions[
                self.data_fetcher.rep_sing.map_column("coldheads.serial_number")
            ] = coldhead_serial
        if wip_number:
            conditions[
                self.data_fetcher.rep_sing.map_column("wips.wip_number")
            ] = wip_number
        if displacer_serial:
            conditions[
                self.data_fetcher.rep_sing.map_column(
                    "displacers.displacer_serial_number"
                )
            ] = displacer_serial
        if test_id:
            conditions[self.data_fetcher.rep_sing.map_column("tests.test_id")] = test_id
        if serial_number:
            # serial_number can refer to either coldheads.serial_number or displacers.displacer_serial_number
            or_conditions.append(
                (
                    self.data_fetcher.rep_sing.map_column("coldheads.serial_number"),
                    serial_number,
                )
            )
            or_conditions.append(
                (
                    self.data_fetcher.rep_sing.map_column(
                        "displacers.displacer_serial_number"
                    ),
                    serial_number,
                )
            )

        # Adjusted join conditions
        join_conditions = [
            {
                "type": "LEFT",
                "table": "coldheads",
                "on": self.data_fetcher.rep_sing.map_column(
                    "wips.coldhead_serial_number"
                )
                + " = "
                + self.data_fetcher.rep_sing.map_column("coldheads.serial_number"),
            },
            {
                "type": "LEFT",
                "table": "displacers",
                "on": self.data_fetcher.rep_sing.map_column(
                    "wips.displacer_serial_number"
                )
                + " = "
                + self.data_fetcher.rep_sing.map_column(
                    "displacers.displacer_serial_number"
                ),
            },
            {
                "type": "LEFT",
                "table": "tests",
                "on": self.data_fetcher.rep_sing.map_column("wips.wip_number")
                + " = "
                + self.data_fetcher.rep_sing.map_column("tests.wip_number"),
            },
        ]

        # Select desired columns using logical names
        columns = [
            "wips.wip_number",
            "coldheads.coldhead_id",
            "coldheads.serial_number AS coldhead_serial_number",
            "displacers.displacer_serial_number",
            "wips.arrival_date",
            "wips.teardown_date",
            "wips.status AS wip_status",
            "displacers.status AS displacer_status",
            "displacers.notes AS displacer_notes",
            "displacers.initial_open_date",
            "tests.test_id",
            "tests.pass_fail",
            "tests.notes AS test_notes",
            "tests.mode",
            "tests.turns",
            "tests.first_stage_heaters",
            "tests.second_stage_heater",
            "tests.first_stage_temp",
            "tests.second_stage_temp",
            "tests.efficiency1",
            "tests.efficiency2",
            "tests.test_attempt",
            "tests.test_date"
            # Add other columns as necessary
        ]

        # Map columns
        mapped_columns = [self.data_fetcher.rep_sing.map_column(col) for col in columns]

        try:
            logger.info(f"Initiating flexible_search with conditions: {conditions}")
            # Fetch data using joins
            results = self.data_fetcher.fetch_reptracker(
                tables=["wips"],
                columns=mapped_columns,
                conditions=conditions,
                or_conditions=or_conditions,
                join_conditions=join_conditions,
            )

            if not results:
                logger.info("No results returned from the query.")
                return {}

            # Aggregate results: Map WIP to its tests
            aggregated_results = {}
            for row in results:
                wip_number = row["wip_number"]
                if wip_number not in aggregated_results:
                    aggregated_results[wip_number] = {
                        "wip_number": wip_number,
                        "coldhead_id": row["coldhead_id"],
                        "coldhead_serial_number": row["coldhead_serial_number"],
                        "displacer_serial_number": row["displacer_serial_number"],
                        "arrival_date": row["arrival_date"],
                        "teardown_date": row["teardown_date"],
                        "wip_status": row["wip_status"],
                        "displacer_status": row["displacer_status"],
                        "displacer_notes": row["displacer_notes"],
                        "initial_open_date": row["initial_open_date"],
                        "tests": [],
                    }

                # Append test data if available
                if row["test_id"] is not None:
                    test_data = {
                        "test_id": row["test_id"],
                        "pass_fail": row["pass_fail"],
                        "notes": row["test_notes"],
                        "mode": row["mode"],
                        "turns": row["turns"],
                        "first_stage_heaters": row["first_stage_heaters"],
                        "second_stage_heater": row["second_stage_heater"],
                        "first_stage_temp": row["first_stage_temp"],
                        "second_stage_temp": row["second_stage_temp"],
                        "efficiency1": row["efficiency1"],
                        "efficiency2": row["efficiency2"],
                        "test_attempt": row["test_attempt"],
                        "test_date": row["test_date"]
                        # Add any other necessary fields
                    }
                    aggregated_results[wip_number]["tests"].append(test_data)

            logger.info(f"Flexible search returned {len(aggregated_results)} WIPs")
            return aggregated_results
        except Exception as e:
            logger.exception(f"Error during flexible_search: {e}")
            return {}
