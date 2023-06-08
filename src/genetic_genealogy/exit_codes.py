from enum import IntEnum


class ExitCodes(IntEnum):
	wrong_input_format = 1
	missing_data = 2
	no_such_file = 3
	io_error = 4
	no_current_project = 5
