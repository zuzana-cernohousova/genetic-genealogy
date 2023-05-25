import csv
import re
from abc import ABC, abstractmethod

from databases.match_databases import CSVMatchDatabase, CSVInputOutput
from databases.segment_databases import CSVSegmentDatabase
from parsers.headers import FTDNASegmentFormat, SegmentFormatEnum


class SegmentParser(ABC):
	def __init__(self):
		self.result = []

	@property
	@abstractmethod
	def input_format(self):
		pass

	@abstractmethod
	def parse_file(self, filename):
		pass

	def save_to_file(self, output_filename):
		"""Saves the output to the given file."""

		CSVInputOutput.save_csv(self.result, output_filename, SegmentFormatEnum)


class FTDNASegmentParser(SegmentParser):

	def __init__(self):
		super().__init__()

	@property
	def input_format(self):
		return FTDNASegmentFormat()

	def parse_file(self, filename):
		existing_matches = CSVMatchDatabase()
		existing_matches.load()

		existing_segments = CSVSegmentDatabase()
		existing_segments.load()

		new_segment = False
		person_id_not_matched = False

		with open(filename, "r", encoding="utf-8-sig") as input_file:
			reader = csv.DictReader(input_file)

			# check if the file is in the correct format
			self.input_format.validate_format(reader.fieldnames)

			for record in reader:
				output_segment = {}
				for index in SegmentFormatEnum:
					output_segment[index] = ""

				# add SOURCE name
				output_segment[SegmentFormatEnum.source] = self.input_format.format_name

				# create NAME and add it to result
				name = self.__create_name(record)
				output_segment[SegmentFormatEnum.person_name] = name

				# extract PERSON ID from name and add it to result
				person_id = existing_matches.get_id_from_match_name(name)

				if person_id is None:  # no matching person found
					person_id_not_matched = True
					person_id = -1 	# change id to special value

				output_segment[SegmentFormatEnum.id] = person_id

				# copy all REMAINING existing information = MAPPED FIELDS
				for input_column_name in reader.fieldnames:
					item = record[input_column_name]

					output_column = self.input_format.get_mapped_column_name(input_column_name)
					# output_column is of SegmentFormatEnum type -> is int if is not none

					if output_column is not None:
						output_segment[output_column] = item

				# get and add SEGMENT ID
				segment_id = existing_segments.get_segment_id(output_segment)

				if segment_id is None:
					# no match found - create new id and add to database
					segment_id = existing_segments.get_new_segment_id()
					output_segment[SegmentFormatEnum.segment_id] = segment_id

					new_segment = True
					existing_segments.add_segment(output_segment)

				else:
					output_segment[segment_id] = segment_id

				self.result.append(output_segment)

		if new_segment:
			existing_segments.save()

		if person_id_not_matched:
			self.__print_message()

	@staticmethod
	def __print_message():
		print("""AT LEAST ONE id DID NOT MATCH
	please check that all files are current
		if not, please rerun the procedure with current information
		if yes, please correct the files manually
		""")

	@staticmethod
	def __create_name(record):
		return re.sub(' +', ' ', record['Match Name'])
