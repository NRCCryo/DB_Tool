# test_insert_order_window.py

import unittest
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker
from db_ops.models import Base, Coldhead, Displacer, WIP, Test
from gui.insert_order_window import InsertOrderWindow
import tkinter as tk

class TestInsertOrderWindow(unittest.TestCase):
    def setUp(self):
        # Set up in-memory SQLite database without "foreign_keys": 1
        self.engine = create_engine('sqlite:///:memory:', echo=False, connect_args={"check_same_thread": False})

        # Enable foreign key constraints
        @event.listens_for(self.engine, "connect")
        def enable_foreign_keys(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        # Create all tables
        Base.metadata.create_all(self.engine)

        # Create a configured "Session" class
        Session = sessionmaker(bind=self.engine)

        # Create a Session
        self.session = Session()

        # Pre-populate the Test table
        test_entries = [Test(test_id=i, name=f"Test {i}") for i in range(1, 13)]
        self.session.add_all(test_entries)
        self.session.commit()

        # Initialize Tkinter root (without displaying the GUI)
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the main window

        # Initialize InsertOrderWindow with mocked parent and session
        self.window = InsertOrderWindow(parent=self.root, session=self.session)

    def tearDown(self):
        # Destroy the Tkinter root after tests
        self.window.destroy()
        self.root.destroy()
        self.session.close()
        self.engine.dispose()

    def test_insert_wips(self):
        # Define the test data (unique wip_numbers)
        test_data = [
            {'wip_number': '398517', 'coldhead_serial': 'J03636', 'displacer_serial': 'R6650/R6071', 'test_id': '1', 'arrival_date': '2023-10-03', 'teardown_date': ''},
            {'wip_number': '415481', 'coldhead_serial': 'J01205', 'displacer_serial': 'R4002/R4128', 'test_id': '2', 'arrival_date': '2023-11-01', 'teardown_date': ''},
            {'wip_number': '000001', 'coldhead_serial': 'J01710', 'displacer_serial': 'RXXXX/RXXXX', 'test_id': '3', 'arrival_date': '2023-11-01', 'teardown_date': ''},  # Unique WIP
            {'wip_number': '428523', 'coldhead_serial': 'SJ01800', 'displacer_serial': 'E662/A361', 'test_id': '4', 'arrival_date': '2023-11-02', 'teardown_date': ''},
            {'wip_number': '409513', 'coldhead_serial': 'J03817', 'displacer_serial': 'RYYYY/RYYYY', 'test_id': '5', 'arrival_date': '2023-11-02', 'teardown_date': ''},  # Unique WIP
            {'wip_number': '415482', 'coldhead_serial': 'J01205', 'displacer_serial': 'R6647/R6069', 'test_id': '6', 'arrival_date': '2023-12-04', 'teardown_date': ''},
            {'wip_number': '401479', 'coldhead_serial': 'J03154', 'displacer_serial': 'R6650/R6071', 'test_id': '7', 'arrival_date': '2023-12-04', 'teardown_date': ''},
            {'wip_number': '338480', 'coldhead_serial': 'J02115', 'displacer_serial': 'R4002/R4128', 'test_id': '8', 'arrival_date': '2023-12-05', 'teardown_date': ''},
            {'wip_number': '398518', 'coldhead_serial': 'J03636', 'displacer_serial': 'R6653/R6064', 'test_id': '9', 'arrival_date': '2023-12-05', 'teardown_date': ''},
            {'wip_number': '406529', 'coldhead_serial': 'J03528', 'displacer_serial': 'R6101/R3705', 'test_id': '10', 'arrival_date': '2023-12-07', 'teardown_date': ''},
            {'wip_number': '406526', 'coldhead_serial': 'J03372', 'displacer_serial': 'R6627/R6067', 'test_id': '11', 'arrival_date': '2023-12-07', 'teardown_date': ''},
            {'wip_number': '437648', 'coldhead_serial': 'J02818', 'displacer_serial': 'R9207/R9276', 'test_id': '12', 'arrival_date': '2023-12-13', 'teardown_date': ''},
        ]

        for data in test_data:
            if not data['wip_number'] or not data['displacer_serial']:
                with self.assertRaises(ValueError):
                    self.window.create_order_with_data(
                        wip_number=data['wip_number'],
                        coldhead_serial=data['coldhead_serial'],
                        displacer_serial=data['displacer_serial'],
                        arrival_date=data['arrival_date'],
                        teardown_date=data['teardown_date'],
                        test_id=data['test_id']
                    )
            else:
                # Call the method to insert data programmatically
                self.window.create_order_with_data(
                    wip_number=data['wip_number'],
                    coldhead_serial=data['coldhead_serial'],
                    displacer_serial=data['displacer_serial'],
                    arrival_date=data['arrival_date'],
                    teardown_date=data['teardown_date'],
                    test_id=data['test_id']
                )

        # Verify that valid WIPs are inserted
        inserted_wips = self.session.query(WIP).all()
        expected_valid_entries = len([d for d in test_data if d['wip_number'] and d['displacer_serial']])
        self.assertEqual(len(inserted_wips), expected_valid_entries)

        # Verify specific entries
        for data in test_data:
            if data['wip_number'] and data['displacer_serial']:
                wip = self.session.query(WIP).filter_by(wip_number=data['wip_number']).first()
                self.assertIsNotNone(wip)
                self.assertEqual(wip.coldhead.serial_number, data['coldhead_serial'])
                self.assertEqual(wip.displacer.displacer_serial_number, data['displacer_serial'])
                self.assertEqual(str(wip.arrival_date), data['arrival_date'])
                if data['teardown_date']:
                    self.assertEqual(str(wip.teardown_date), data['teardown_date'])

if __name__ == '__main__':
    unittest.main()
