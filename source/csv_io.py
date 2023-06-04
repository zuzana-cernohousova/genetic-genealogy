import csv
import sys


class CSVInputOutput:
	@staticmethod
	def load_csv_database(filename, database_format, searched_id) -> (int, list):
		"""Reads the given csv file, finds the largest id,
		returns the id and the file as a list of rows (dicts)"""

		result = []
		biggest_id = 0

		try:
			with open(filename, 'r', encoding="utf-8-sig") as input_file:
				reader = csv.DictReader(input_file)
				reader.fieldnames = CSVInputOutput.__get_new_fieldnames(reader.fieldnames, database_format)

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
		"""Simply loads a csv file, returns it as a list of dictionaries,
		where keys are replaced with input_format_enum values."""
		result = []
		with open(filename, 'r', encoding="utf-8-sig") as input_file:
			reader = csv.DictReader(input_file)
			reader.fieldnames = CSVInputOutput.__get_new_fieldnames(reader, input_format_enum)

			for record in reader:
				result.append(record)
		return result

	@staticmethod
	def __get_new_fieldnames(fieldnames, input_format_enum) -> list:
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
	def save_csv(database, database_format, filename=None) -> None:
		"""Saves the database to the given csv file or to standard output if no file is given."""

		# no filename given --> write to stdout
		if filename is None:
			CSVInputOutput.__write_to_writer(database, database_format, csv.writer(sys.stdout))

		else:
			# file will be opened or created
			with open(filename, "w", newline='', encoding="utf-8-sig") as output_file:
				CSVInputOutput.__write_to_writer(database, database_format, csv.writer(output_file))

	@staticmethod
	def __write_to_writer(database, database_format, writer) -> None:
		writer.writerow(database_format.get_header())

		for row in database:
			if type(row) is dict:
				writer.writerow(row.values())
			else:  # list
				writer.writerow(row)
