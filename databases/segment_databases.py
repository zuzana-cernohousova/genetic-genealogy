import csv

from abc import abstractmethod, ABC
from parsers.headers import SegmentFormat


class SegmentDatabase:
	__format = SegmentFormat()
	__file_name = "all_segments.csv"

	def __init__(self):
		self.__database = self.__load_from_file()

	def get_segment_id(self, parsed_segment):
		person_id_index = self.__format.get_index('ID')

		for raw_segment in self.__database:
			if raw_segment[person_id_index] == parsed_segment[person_id_index]:
				if raw_segment[2:] == parsed_segment[2:]:  # all other columns must match
					# todo rewrite so that id does not have to be in the first position
					return raw_segment[self.__format.get_index("Segment ID")]

		# if match not found, segment is new
		return None

	def get_new_segment_id(self):
		self.__biggest_segment_ID += 1
		return self.__biggest_segment_ID

	def add_segment(self, complete_parsed_segment):
		self.__database.append(complete_parsed_segment)

	def __load_from_file(self):
		segments = []

		biggest_id = 0
		segment_id_index = self.__format.get_index("Segment ID")

		try:
			with open(self.__file_name, 'r', encoding="utf-8-sig") as input_file:
				reader = csv.reader(input_file)

				# skip header
				for _ in reader:
					break

				for segment in reader:
					record_id = int(segment[segment_id_index])
					if record_id > biggest_id:
						biggest_id = record_id

					segments.append(segment)

		except IOError:
			pass

		self.__biggest_segment_ID = biggest_id
		return segments

	def save_to_file(self):
		with open(self.__file_name, "w", newline='', encoding="utf-8-sig") as output_file:
			writer = csv.writer(output_file)
			writer.writerow(self.__format.header)
			for row in self.__database:
				writer.writerow(row)
