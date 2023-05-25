import csv

from abc import abstractmethod, ABC
from parsers.headers import SegmentFormatEnum
from databases.match_databases import CSVInputOutput


class SegmentDatabase(ABC):
	@abstractmethod
	def load(self):
		pass

	@abstractmethod
	def save(self):
		pass

	database = []
	largest_ID = 0

	def get_segment_id(self, parsed_segment):
		segment_id = None

		for old_segment in self.database:
			match = True

			# compare all fields except for the id field
			for index in SegmentFormatEnum:
				if index == SegmentFormatEnum.segment_id:
					continue

				if old_segment[index] != parsed_segment[index]:
					match = False
					break
			if match:
				segment_id = old_segment[SegmentFormatEnum.segment_id]
				break

		return segment_id

	def get_new_segment_id(self):
		self.largest_ID += 1
		return self.largest_ID

	def add_segment(self, complete_parsed_segment):
		self.database.append(complete_parsed_segment)


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
