import csv
import sys

from genetic_genealogy.helper import lower_no_whitespace


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
		where keys are replaced with input_format_enum values."""

		try:
			if filename is None:
				input_file = sys.stdin.read().splitlines()
				return CSVHelper.__load_from_reader(csv.DictReader(input_file), input_format_enum)

			with open(filename, 'r', encoding="utf-8-sig") as input_file:
				reader = csv.DictReader(input_file)
				return CSVHelper.__load_from_reader(reader, input_format_enum)

		except IOError:
			print("Segments could not be loaded")
			exit(1)

	# todo exit code

	@staticmethod
	def __get_list_from_reader(reader: csv.DictReader) -> list:
		result = []
		for row in reader:
			result.append(row)

		return result

	@staticmethod
	def __get_intenum_fieldnames(fieldnames, input_format_enum) -> list:
		new_fieldnames = []

		# replace fieldnames with enum values
		if fieldnames is not None:
			for index in fieldnames:
				for value in input_format_enum:
					if value.name == index:
						new_fieldnames.append(value)
						break

		return new_fieldnames

	@staticmethod
	def __load_from_reader(reader, input_format_intenum) -> list:
		reader.fieldnames = CSVHelper.__get_intenum_fieldnames(reader.fieldnames, input_format_intenum)
		return CSVHelper.__get_list_from_reader(reader)

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
