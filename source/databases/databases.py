import csv
import re
import sys
from abc import ABC, abstractmethod

from source.parsers.formats import MatchFormatEnum, SegmentFormatEnum, SourceEnum
from source.config_reader import ConfigReader


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


class Database(ABC):
	def __init__(self):
		self._database = []
		self._largest_ID = 0

	@abstractmethod
	def load(self):
		"""Loads the database."""
		pass

	@abstractmethod
	def save(self) -> None:
		"""Saves the database."""
		pass

	@property
	@abstractmethod
	def format(self) -> SegmentFormatEnum | MatchFormatEnum :
		"""Represents the format of the database."""
		pass

	def get_id(self, parsed_record, source, searched_id_type) -> int | None:
		""" If the parsed_record already exists,
		finds it and returns the record ID (type of id specified by the searched_id_type
		parameter), else returns None."""
		match_record_id = None

		for old_record in self._database:
			match = True

			# compare all fields except for the id field
			for index in self.format.comparison_key(source=source):
				if index == searched_id_type:
					continue

				if str(old_record[index]) != str(parsed_record[index]):
					match = False
					break

			if match:
				match_record_id = old_record[searched_id_type]
				break

		return match_record_id

	def get_new_id(self) -> int:
		"""Creates a new maximum ID and returns it."""
		self._largest_ID += 1
		return self._largest_ID

	def add_record(self, complete_parsed_record: dict) -> None:
		"""Adds a complete parsed record to the database list."""
		self._database.append(complete_parsed_record)


# region match databases

class MatchDatabase(Database, ABC):
	def __init__(self):
		super().__init__()
		self.records_by_name = None
		self.records_by_id = None
		self.records_by_gedmatch_id = None

	def __create_records_by_name_dict(self) -> None:
		"""Creates a dictionary of person IDs. The keys are person names."""
		result = {}
		for row in self._database:
			result[row[self.format.person_name].lower()] = row

		self.records_by_name = result

	def __create_records_by_id_dict(self) -> None:
		"""Creates a dictionary of person IDs. The keys are person IDs."""
		result = {}
		for row in self._database:
			result[int(row[self.format.person_id])] = row

		self.records_by_id = result

	def __create_records_by_gedmatch_id_dict(self) -> None:
		"""Creates a dictionary of person IDs. The keys are the GEDmatch identificators."""
		result = {}
		for row in self._database:
			result[row[self.format.gedmatch_kit_id]] = row

		self.records_by_gedmatch_id = result

	@property
	def format(self):
		return MatchFormatEnum

	def get_record_from_match_name(self, match_name) -> dict | None:
		"""Finds a record based on name and returns the ID. If no record is found, returns None."""

		if self.records_by_name is None:
			self.__create_records_by_name_dict()

		match_name = re.sub(' +', ' ', match_name).lower()

		if match_name in self.records_by_name.keys():
			return self.records_by_name[match_name]

		return None

	def get_record_from_gedmatch_id(self, match_gedmatch_id) -> dict | None:
		"""Finds a record based on name and returns the ID. If no record is found, returns None."""

		if self.records_by_gedmatch_id is None:
			self.__create_records_by_gedmatch_id_dict()

		if match_gedmatch_id in self.records_by_gedmatch_id.keys():
			return self.records_by_gedmatch_id[match_gedmatch_id]

		return None

	def get_id(self, parsed_record, source, searched_id_type=MatchFormatEnum.person_id) -> int | None:
		"""Gets id of just parsed record using built dictionaries."""
		potential_record = None

		# if data is from FamilyTreeDNA, search for the id in records by name
		if source == SourceEnum.FamilyTreeDNA:
			potential_record = self.get_record_from_match_name(parsed_record[self.format.person_name])

		elif source == SourceEnum.GEDmatch:
			potential_record = self.get_record_from_gedmatch_id(parsed_record[self.format.gedmatch_kit_id])

		if potential_record is not None:
			# compare other key values, all must be the same as in found record
			for key in self.format.comparison_key(source=source):
				if key == searched_id_type:
					continue
				if potential_record[key] != parsed_record[key]:
					return None

			# only return the id if all columns match
			return int(potential_record[searched_id_type])

		return None

	def get_record_from_id(self, record_id) -> dict | None:
		"""Returns a record of given id."""

		if self.records_by_id is None:
			self.__create_records_by_id_dict()

		if record_id in self.records_by_id.keys():
			return self.records_by_id[record_id]

		return None


class CSVMatchDatabase(MatchDatabase):
	"""
	Loads all match data from file and holds it.
	"""

	def __init__(self):
		super().__init__()
		self.__file_name = ""

	def load(self, filename=None):
		"""Reads the given csv file and stores it in the database.
		If filename is specified, the file is used, else path is read from project configuration."""

		if filename:
			self.__file_name = filename
		else:
			self.__file_name = ConfigReader.get_match_database_location()

		self._largest_ID, self._database = CSVInputOutput.load_csv_database(
			self.__file_name,
			self.format,
			self.format.person_id
		)

	def save(self):
		"""Saves the database to the given csv file."""
		# file will be opened or created

		CSVInputOutput.save_csv(self._database, self.format, filename=self.__file_name)


# endregion

# region segment databases

class SegmentDatabase(Database, ABC):
	@property
	def format(self):
		return SegmentFormatEnum


class CSVSegmentDatabase(SegmentDatabase):
	def __init__(self):
		super().__init__()
		self.__file_name = ConfigReader.get_segment_database_location()

	def load(self):
		self._largest_ID, self._database = CSVInputOutput.load_csv_database(
			self.__file_name,
			self.format,
			self.format.segment_id
		)

	def save(self):
		CSVInputOutput.save_csv(self._database, self.format, filename=self.__file_name)

# endregion
