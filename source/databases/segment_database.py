from abc import ABC

from source.config_reader import ConfigReader
from source.csv_io import CSVInputOutput
from source.databases.database import Database
from source.parsers.formats import SegmentFormatEnum


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
