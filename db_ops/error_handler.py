# db_ops/error_handler.py


class DatabaseError(Exception):
    """Base class for all database-related errors."""

    pass


class DuplicateEntryError(DatabaseError):
    """Raised when a duplicate entry violates unique constraints."""

    def __init__(self, field, value):
        self.field = field
        self.value = value
        self.message = f"Duplicate entry for '{field}': '{value}'. Please ensure all serial numbers are unique."
        super().__init__(self.message)


class EmptyUpdateError(DatabaseError):
    """Raised when an update operation has no fields to update."""

    def __init__(self, table):
        self.table = table
        self.message = (
            f"No data provided for updating table '{table}'. Update operation skipped."
        )
        super().__init__(self.message)


class InvalidDataError(DatabaseError):
    """Raised when provided data is invalid or incomplete."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
