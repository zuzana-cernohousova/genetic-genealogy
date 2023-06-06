from abc import ABC

from genetic_genealogy.config_reader import ConfigReader
from genetic_genealogy.csv_io import CSVInputOutput
from genetic_genealogy.databases.database import Database
from genetic_genealogy.parsers.formats import SegmentFormatEnum, SourceEnum


# region segment databases

class SegmentDatabase(Database, ABC):
	def __init__(self):
		super().__init__()
		self._segments_by_person_name = None
		self._segments_by_chromosome = None

	@property
	def format(self):
		return SegmentFormatEnum

	def _create_segments_by_chromosome(self) -> None:
		# create a dict where chromosome ids are keys and values are lists of segments
		# will be used for faster computation
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
				name = "".join(segment[self.format.person_name].split()).lower()

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
			name = "".join(parsed_record[self.format.person_name].split()).lower()

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
