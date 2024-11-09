# db_mngt/fetch_data.py

from db_mngt.mngt_singletons import RepTrackerSing
from logger import logger  # Import the logger


class DataFetcher:
    def __init__(self):
        self.rep_sing = RepTrackerSing.get_instance()
        logger.info("DataFetcher initialized")

    def fetch_reptracker(self, tables, columns, conditions=None, or_conditions=None, join_conditions=None):
        """
        Fetch data from the database with flexible conditions and joins.
        """
        try:
            # Build the SELECT clause
            select_clause = f"SELECT {', '.join(columns)}"

            # Build the FROM clause
            from_clause = f"FROM {tables[0]}"

            # Build the JOIN clauses
            join_clauses = ''
            if join_conditions:
                for join in join_conditions:
                    join_type = join.get('type', 'LEFT')
                    table = join['table']
                    on_condition = join['on']
                    join_clauses += f" {join_type} JOIN {table} ON {on_condition}"

            # Build the WHERE clause
            where_clause = ''
            params = []
            if conditions or or_conditions:
                where_parts = []
                if conditions:
                    for key, value in conditions.items():
                        where_parts.append(f"{key} = ?")
                        params.append(value)
                if or_conditions:
                    or_parts = [f"{key} = ?" for key, value in or_conditions]
                    params.extend([value for _, value in or_conditions])
                    where_parts.append('(' + ' OR '.join(or_parts) + ')')
                where_clause = 'WHERE ' + ' AND '.join(where_parts)

            # Combine all clauses into the final query
            query = f"{select_clause} {from_clause} {join_clauses} {where_clause};"

            logger.debug(f"Final query: {query}")
            logger.debug(f"Parameters: {params}")

            # Execute the query
            return self.rep_sing.execute_query(query, params)
        except Exception as e:
            logger.exception(f"Error in fetch_reptracker: {e}")
            return None
