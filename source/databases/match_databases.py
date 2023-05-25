import csv
import re
from abc import ABC, abstractmethod

from source.parsers.headers import MatchFormatEnum


class CSVInputOutput:
	@staticmethod
	def load_csv(filename, database_format, searched_id):
		"""Reads the given csv file, finds the largest id, returns the id and the file as a list of rows (dicts)"""

		result = []
		biggest_id = 0

		try:
			with open(filename, 'r', encoding="utf-8-sig") as input_file:
				reader = csv.DictReader(input_file)
				new_fieldnames = []

				if reader.fieldnames is not None:
					for index in reader.fieldnames:
						for value in database_format:
							if value.name == index:
								new_fieldnames.append(value)
								break

				reader.fieldnames = new_fieldnames

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
	def save_csv(database, filename, database_format):
		"""Saves the database to the given csv file."""
		# file will be opened or created
		with open(filename, "w", newline='', encoding="utf-8-sig") as output_file:
			writer = csv.writer(output_file)

			writer.writerow(database_format.get_header())

			for row in database:
				if type(row) is dict:
					writer.writerow(row.values())
				else:  # list
					writer.writerow(row)


class MatchDatabase(ABC):
	@abstractmethod
	def load(self):
		pass

	@abstractmethod
	def save(self):
		pass

	database = []
	largest_ID = 0

	def get_id(self, parsed_record):
		""" If the parsed_record already exists, finds it and returns the record ID, else returns None."""
		match_record_id = None

		for old_record in self.database:
			match = True

			# compare all fields except for the id field
			for index in MatchFormatEnum:
				if index == MatchFormatEnum.id:
					continue

				if old_record[index] != parsed_record[index]:
					match = False
					break
			if match:
				match_record_id = old_record[MatchFormatEnum.id]
				break

		return match_record_id

	def get_new_id(self):
		"""Creates a new maximum ID and returns it."""
		self.largest_ID += 1
		return self.largest_ID

	def add_record(self, complete_parsed_record):
		"""Adds a complete parsed record to the database list."""
		self.database.append(complete_parsed_record)

	def get_id_from_match_name(self, match_name):
		"""Finds a record based on name and returns the ID. If no record is found, returns None."""
		match_name = re.sub(' +', ' ', match_name)

		for record in self.database:
			if record[MatchFormatEnum.person_name] == match_name:
				return record[MatchFormatEnum.id]

		return None


class CSVMatchDatabase(MatchDatabase):
	"""
	Loads all match data from file and holds it.
	"""

	def __init__(self):
		self.__file_name = "all_matches.csv"
		# todo load file_name from configuration file

		self.__database = []

	def load(self):
		"""Reads the given csv file and stores it in the database"""

		self.largest_ID, self.database = CSVInputOutput.load_csv(self.__file_name, MatchFormatEnum, MatchFormatEnum.id)

	def save(self):
		"""Saves the database to the given csv file."""
		# file will be opened or created

		CSVInputOutput.save_csv(self.database, self.__file_name, MatchFormatEnum)
