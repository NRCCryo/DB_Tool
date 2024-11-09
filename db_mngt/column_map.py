# db_mngt/column_map.py

COLDHEADS_TABLE_MAPPING = {
    'coldhead_id': 'coldhead_id',
    'serial_number': 'serial_number',
}

DISPLACERS_TABLE_MAPPING = {
    'displacer_serial_number': 'displacer_serial_number',
    'status': 'status',
    'notes': 'notes',
    'initial_open_date': 'initial_open_date',  # Added field
}

WIPS_TABLE_MAPPING = {
    'wip_number': 'wip_number',
    'coldhead_serial_number': 'coldhead_serial_number',
    'displacer_serial_number': 'displacer_serial_number',
    'arrival_date': 'arrival_date',
    'teardown_date': 'teardown_date',
    'status': 'status',
}

TESTS_TABLE_MAPPING = {
    'test_id': 'test_id',
    'wip_number': 'wip_number',
    'coldhead_serial_number': 'coldhead_serial_number',
    'displacer_serial_number': 'displacer_serial_number',
    'test_date': 'test_date',  # Included to allow setting it when available
    'test_attempt': 'test_attempt',
    'pass_fail': 'pass_fail',
    'temps': 'temps',
    'notes': 'notes',
    'mode': 'mode',
    'turns': 'turns',
    'first_stage_heaters': 'first_stage_heaters',
    'second_stage_heater': 'second_stage_heater',
    'first_stage_temp': 'first_stage_temp',
    'second_stage_temp': 'second_stage_temp',
    'efficiency1': 'efficiency1',
    'efficiency2': 'efficiency2',
    # Add any other necessary fields
}

