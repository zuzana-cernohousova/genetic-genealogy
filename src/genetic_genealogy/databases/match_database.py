import re
from abc import ABC

from genetic_genealogy.csv_io import CSVHelper
from genetic_genealogy.databases.database import Database
from genetic_genealogy.helper import lower_one_space
from genetic_genealogy.parsers.formats import MatchFormatEnum, SourceEnum
from genetic_genealogy.config_reader import ConfigReader


class MatchDatabase(Database, ABC):
	"""Represents database of all matches already parsed within the current gengen project."""

	def __init__(self):
		super().__init__()
		self.records_by_name = None
		self.records_by_id = None
		self.records_by_gedmatch_id = None

	def __create_records_by_name_dict(self) -> None:
		"""Creates a dictionary of records. The keys are person names."""
		result = {}
		for row in self._database:
			result[row[self.format.person_name].lower()] = row

		self.records_by_name = result

	def __create_records_by_id_dict(self) -> None:
		"""Creates a dictionary of records. The keys are person IDs."""
		result = {}
		for row in self._database:
			result[int(row[self.format.person_id])] = row

		self.records_by_id = result

	def __create_records_by_gedmatch_id_dict(self) -> None:
		"""Creates a dictionary of records. The keys are the GEDmatch identificators."""
		result = {}
		for row in self._database:
			result[row[self.format.gedmatch_kit_id]] = row

		self.records_by_gedmatch_id = result

	@property
	def format(self):
		return MatchFormatEnum

	def get_record_from_match_name(self, match_name):
		"""Finds a record based on name and returns it. If no record is found, returns None."""

		if self.records_by_name is None:
			self.__create_records_by_name_dict()

		match_name = lower_one_space(match_name)

		if match_name in self.records_by_name.keys():
			return self.records_by_name[match_name]

		return None

	def get_record_from_gedmatch_id(self, match_gedmatch_id):
		"""Finds a record based on gedmatch kit id and returns it. If no record is found, returns None."""

		if self.records_by_gedmatch_id is None:
			self.__create_records_by_gedmatch_id_dict()

		if match_gedmatch_id in self.records_by_gedmatch_id.keys():
			return self.records_by_gedmatch_id[match_gedmatch_id]

		return None

	def get_id(self, parsed_record, source, searched_id_type=MatchFormatEnum.person_id):
		"""Returns id of just parsed record. Depending on source database,
		different fields are used to speed up the process."""

		potential_record = None

		# if data is from FamilyTreeDNA, search for the id in records by name
		if source == SourceEnum.FamilyTreeDNA:
			potential_record = self.get_record_from_match_name(parsed_record[self.format.person_name])

		elif source == SourceEnum.GEDmatch:
			potential_record = self.get_record_from_gedmatch_id(parsed_record[self.format.gedmatch_kit_id])

		if potential_record is not None:
			# compare other key values if there are more, all must be the same as in found record

			for key in self.format.comparison_key(source=source):
				if key == searched_id_type:
					continue
				if potential_record[key] != parsed_record[key]:
					return None

			# only return the id if all columns match
			return int(potential_record[searched_id_type])

		return None

	def get_record_from_id(self, record_id: int):
		"""Returns a record of given id. record_id must be int."""

		if self.records_by_id is None:
			self.__create_records_by_id_dict()

		if int(record_id) in self.records_by_id.keys():
			return self.records_by_id[record_id]

		return None


class CSVMatchDatabase(MatchDatabase):
	"""Represents database of all the matches already parsed within the current project.
	Within this implementation of the MatchDatabase abstract class, the data is stored in a csv file."""

	def __init__(self):
		super().__init__()
		self.__file_name = ConfigReader.get_match_database_location()

	def load(self):
		"""Reads the given csv file and stores it. CSV file location is read from project configuration."""
		self._largest_ID, self._database = CSVHelper.load_csv_database(
			self.__file_name,
			self.format,
			self.format.person_id
		)

	def save(self):
		"""Saves the database to the given csv file."""
		CSVHelper.save_csv(self._database, self.format, filename=self.__file_name)

# endregion
