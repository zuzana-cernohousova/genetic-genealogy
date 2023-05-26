from abc import abstractmethod, ABC
from source.parsers.headers import SegmentFormatEnum
from source.databases.match_databases import CSVInputOutput, Database


class SegmentDatabase(Database, ABC):
	@property
	def format(self):
		return SegmentFormatEnum

	@property
	def main_id(self):
		return SegmentFormatEnum.segment_id


class CSVSegmentDatabase(SegmentDatabase):

	def __init__(self):
		self.__file_name = "all_segments.csv"

	def load(self):
		self.largest_ID, self.database = CSVInputOutput.load_csv\
				(
					self.__file_name, SegmentFormatEnum,
					SegmentFormatEnum.segment_id
				)

	def save(self):
		CSVInputOutput.save_csv(self.database, self.__file_name, SegmentFormatEnum)
