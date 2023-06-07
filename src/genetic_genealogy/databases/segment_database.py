from abc import ABC

from genetic_genealogy.config_reader import ConfigReader
from genetic_genealogy.csv_io import CSVHelper
from genetic_genealogy.databases.database import Database
from genetic_genealogy.helper import lower_no_whitespace
from genetic_genealogy.parsers.formats import SegmentFormatEnum, SourceEnum


# region segment databases

class SegmentDatabase(Database, ABC):
	"""Represents database of all segments already parsed within the current gengen project."""

	def __init__(self):
		super().__init__()
		self._segments_by_person_name = None
		self._segments_by_chromosome = None

	@property
	def format(self):
		return SegmentFormatEnum

	def _create_segments_by_chromosome(self) -> None:
		"""Creates a dict where chromosome ids are keys and values are lists of segments.
		Will be used for faster computation"""

		self._segments_by_chromosome = {}

		for segment in self._database:
			chrom_id = segment[self.format.chromosome_id]
			if chrom_id in self._segments_by_chromosome.keys():
				self._segments_by_chromosome[chrom_id].append(segment)
			else:
				self._segments_by_chromosome[chrom_id] = [segment]

	def _create_segments_by_person_name(self) -> None:
		"""Creates a dict where names are keys and values are lists of segments,
		will be used for faster computation. All names are stripped of any spaces and lower cased."""
		self._segments_by_person_name = {}

		for segment in self._database:
			if segment[self.format.source] == SourceEnum.FamilyTreeDNA.name:
				name = lower_no_whitespace(segment[self.format.person_name])

				if name in self._segments_by_person_name.keys():
					self._segments_by_person_name[name].append(segment)
				else:
					self._segments_by_person_name[name] = [segment]

	def get_id(self, parsed_record, source, searched_id_type=SegmentFormatEnum.segment_id) -> int | None:
		if self._segments_by_person_name is None:
			self._create_segments_by_person_name()
		if self._segments_by_chromosome is None:
			self._create_segments_by_chromosome()

		# data from ftdna -> search by person name
		if source == SourceEnum.FamilyTreeDNA:
			name = lower_no_whitespace(parsed_record[self.format.person_name])

			if name in self._segments_by_person_name.keys():
				for segment in self._segments_by_person_name[name]:

					if self.__compare_segments(segment, parsed_record, source, searched_id_type):
						return segment[searched_id_type]

		# data from gedmatch -> only search by chromosome
		if source == SourceEnum.GEDmatch:
			chrom_id = parsed_record[self.format.chromosome_id]

			if chrom_id in self._segments_by_chromosome:
				for segment in self._segments_by_chromosome[chrom_id]:

					if self.__compare_segments(segment, parsed_record, source, searched_id_type):
						return segment[searched_id_type]

		return None

	def __compare_segments(self, segment, parsed_record, source, searched_id_type) -> bool:
		match = True
		for index in self.format.comparison_key(source=source):
			if index == searched_id_type:
				continue

			if str(segment[index]) != str(parsed_record[index]):
				match = False
				break

		return match


class CSVSegmentDatabase(SegmentDatabase):
	"""Represents database of all the segments already parsed within the current project.
	Within this implementation of the SegmentDatabase abstract class, the data is stored in a csv file."""

	def __init__(self):
		super().__init__()
		self.__file_name = ConfigReader.get_segment_database_location()

	def load(self):
		"""Reads the given csv file and stores it. CSV file location is read from project configuration."""

		self._largest_ID, self._database = CSVHelper.load_csv_database(
			self.__file_name,
			self.format,
			self.format.segment_id
		)

	def save(self):
		CSVHelper.save_csv(self._database, self.format, filename=self.__file_name)
