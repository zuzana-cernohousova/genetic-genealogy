import csv
import io
import sys

from genetic_genealogy.helper import lower_no_whitespace
from genetic_genealogy.exit_codes import ExitCodes


class CSVHelper:
	@staticmethod
	def load_csv_database(filename, database_format, searched_id) -> (int, list):
		"""Reads the given csv file, finds the largest id (of given type specified by searched_id parameter),
		returns the id and the file as a list of rows (dicts)."""

		result = []
		biggest_id = 0

		try:
			with open(filename, 'r', encoding="utf-8-sig") as input_file:
				reader = csv.DictReader(input_file)
				reader.fieldnames = CSVHelper.__get_intenum_fieldnames(reader.fieldnames, database_format)

				if reader.fieldnames is None:
					print("Wrong CSV database format.")
					exit(ExitCodes.wrong_input_format)

				for record in reader:
					record_id = int(record[searched_id])
					if record_id > biggest_id:
						biggest_id = record_id

					result.append(record)

		except IOError:
			# if the file does not exist or cannot be read, do nothing
			pass

		return biggest_id, result

	@staticmethod
	def load_csv(filename, input_format_enum) -> list:
		"""Simply loads a csv file using a DictReader, returns it as a list of dictionaries,
		where keys are replaced with input_format_enum values.
		Checks it the format of the file is valid, given the input_format_enum."""

		if filename is None:
			input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8-sig')
			return CSVHelper.__load_from_reader(csv.DictReader(input_stream), input_format_enum)

		with open(filename, 'r', encoding="utf-8-sig") as input_file:
			reader = csv.DictReader(input_file)
			return CSVHelper.__load_from_reader(reader, input_format_enum)

	@staticmethod
	def __get_intenum_fieldnames(fieldnames, input_format_enum) -> list:
		"""Returns list of input_format_enum values corresponding to names of columns
		in fieldnames in the same order.
		If the formats do not match, returns None."""
		new_fieldnames = []

		if not input_format_enum.validate_format(fieldnames):
			return None

		# replace fieldnames with enum values
		if fieldnames is not None:
			for index in fieldnames:
				for value in input_format_enum:
					if lower_no_whitespace(value.name) == lower_no_whitespace(index):
						new_fieldnames.append(value)
						break

		return new_fieldnames

	@staticmethod
	def __load_from_reader(reader, input_format_intenum) -> list:
		"""Returns a list of dictionaries corresponding to rows of reader.
		Checks if the format is correct."""
		reader.fieldnames = CSVHelper.__get_intenum_fieldnames(reader.fieldnames, input_format_intenum)

		if reader.fieldnames is None:
			print("Wrong input format.")
			exit(ExitCodes.wrong_input_format)

		return [row for row in reader]

	@staticmethod
	def save_csv(database: list, database_format, filename=None) -> None:
		"""Saves the list of dictionaries of a given format
		to the given csv file. If no filename is None, standard output is used."""

		# no filename given --> write to stdout
		if filename is None:
			CSVHelper.__write_to_writer(database, database_format, csv.writer(sys.stdout))

		else:
			# file will be opened or created
			with open(filename, 'w', newline='', encoding="utf-8-sig") as output_file:
				CSVHelper.__write_to_writer(database, database_format, csv.writer(output_file))

	@staticmethod
	def __write_to_writer(database, database_format, writer) -> None:
		"""Writes the database (list of rows) to the given writer."""
		writer.writerow(database_format.get_header())

		for row in database:
			if type(row) is dict:
				writer.writerow(row.values())
			else:  # list
				writer.writerow(row)

	@staticmethod
	def get_strenum_fieldnames(input_format, fieldnames) -> list:
		"""Creates a list of values of given input_format (that is a strenum) in the same order as are the corresponding
		strings in current fieldnames."""

		result = []
		for name in fieldnames:
			for enum_name in input_format:
				if lower_no_whitespace(name) == lower_no_whitespace(enum_name):
					result.append(enum_name)

		return result
