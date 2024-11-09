# main.py

import tkinter as tk
from db_ops.search import SearchOperator
from db_ops.new_order import NewOrderInserter
from db_ops.mass_import import MassImporter
from db_ops.update_order import UpdateOrder
from gui.main_gui import GUIFace
from logger import logger
from db_ops import Session  # Import Session from db_ops/__init__.py

def main():
    try:
        logger.info("Application started")

        # Create a new SQLAlchemy session
        session = Session()
        logger.info("New SQLAlchemy session created.")

        # Initialize database operation classes
        new_order_inserter = NewOrderInserter(session)
        search_operator = SearchOperator(session)
        mass_importer = MassImporter(session)
        update_order = UpdateOrder(session)
        logger.info("Database operation classes initialized.")

        # Initialize and start the GUI
        root = tk.Tk()
        gui_face = GUIFace(root, session)
        logger.info("GUIFace initialized and main loop started")
        root.mainloop()

    except Exception as e:
        logger.exception(f"Failed to start application: {e}")

if __name__ == "__main__":
    main()
