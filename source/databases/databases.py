import csv
import re
import sys
from abc import ABC, abstractmethod

from source.parsers.headers import MatchFormatEnum, SegmentFormatEnum
from source.config_reader import ConfigReader


class CSVInputOutput:
	@staticmethod
	def load_csv_database(filename, database_format, searched_id):
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
	def save_csv(database, database_format, filename=None):
		"""Saves the database to the given csv file or to standard output if no file is given."""

		# no filename given --> write to stdout
		if filename is None:
			CSVInputOutput.__write_to_writer(database, database_format, csv.writer(sys.stdout))

		else:
			# file will be opened or created
			with open(filename, "w", newline='', encoding="utf-8-sig") as output_file:
				CSVInputOutput.__write_to_writer(database, database_format,csv.writer(output_file))

	@staticmethod
	def __write_to_writer(database, database_format, writer):
		writer.writerow(database_format.get_header())

		for row in database:
			if type(row) is dict:
				writer.writerow(row.values())
			else:  # list
				writer.writerow(row)


class Database(ABC):
	@abstractmethod
	def load(self):
		pass

	@abstractmethod
	def save(self):
		pass

	@property
	@abstractmethod
	def format(self):
		pass

	database = []
	largest_ID = 0

	def get_id(self, parsed_record, searched_id_type, source):
		""" If the parsed_record already exists,
		finds it and returns the record ID, else returns None."""
		match_record_id = None

		for old_record in self.database:
			match = True

			# compare all fields except for the id field
			for index in self.format.comparison_key(source= source):
				if index == searched_id_type:
					continue

				if old_record[index] != parsed_record[index]:
					match = False
					break

			if match:
				match_record_id = old_record[searched_id_type]
				break

		return match_record_id

	def get_new_id(self):
		"""Creates a new maximum ID and returns it."""
		self.largest_ID += 1
		return self.largest_ID

	def add_record(self, complete_parsed_record):
		"""Adds a complete parsed record to the database list."""
		self.database.append(complete_parsed_record)

	def get_record_from_id(self, record_id, id_type):
		for record in self.database:
			if record[id_type] == record_id:
				return record

		return None


# region match databases

class MatchDatabase(Database, ABC):
	database = []
	largest_ID = 0

	@property
	def format(self):
		return MatchFormatEnum

	def get_id_from_match_name(self, match_name):
		"""Finds a record based on name and returns the ID. If no record is found, returns None."""
		match_name = re.sub(' +', ' ', match_name).lower()

		for record in self.database:
			if record[self.format.person_name].lower() == match_name:
				return record[MatchFormatEnum.id]

		return None


class CSVMatchDatabase(MatchDatabase):
	"""
	Loads all match data from file and holds it.
	"""

	def __init__(self):
		self.__file_name = ConfigReader.get_match_database_location()
		self.__database = []

	def load(self):
		"""Reads the given csv file and stores it in the database"""

		self.largest_ID, self.database = CSVInputOutput.load_csv_database(self.__file_name, MatchFormatEnum, MatchFormatEnum.id)

	def save(self):
		"""Saves the database to the given csv file."""
		# file will be opened or created

		CSVInputOutput.save_csv(self.database, MatchFormatEnum, filename= self.__file_name)


# endregion
# region segment databases

class SegmentDatabase(Database, ABC):
	@property
	def format(self):
		return SegmentFormatEnum


class CSVSegmentDatabase(SegmentDatabase):

	def __init__(self):
		self.__file_name = ConfigReader.get_segment_database_location()

	def load(self):
		self.largest_ID, self.database = CSVInputOutput.load_csv_database \
				(
				self.__file_name, SegmentFormatEnum,
				SegmentFormatEnum.segment_id
			)

	def save(self):
		CSVInputOutput.save_csv(self.database, SegmentFormatEnum, filename= self.__file_name)

# endregion
