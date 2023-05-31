import csv
import re
from abc import ABC

from source.databases.databases import CSVMatchDatabase, CSVSegmentDatabase
from source.parsers.headers import FTDNASegmentFormat, SegmentFormatEnum, MatchFormatEnum
from source.parsers.match_parsers import Parser


class SegmentParser(Parser, ABC):
	"""Class used for parsing segments. Child classes are used for parsing input from different databases."""

	@property
	def output_format(self):
		return SegmentFormatEnum


class FTDNASegmentParser(SegmentParser):
	"""Parses segments from FamilyTreeDNA database."""

	def __init__(self):
		super().__init__()
		self.__unidentified_names = []
		self.__new_segments_found = False

	__input_format = FTDNASegmentFormat

	def parse(self, filename):
		# create and load databases
		existing_matches = CSVMatchDatabase()
		existing_matches.load()

		existing_segments = CSVSegmentDatabase()
		existing_segments.load()

		new_segment = False

		with open(filename, "r", encoding="utf-8-sig") as input_file:
			# read this file with csv reader, read as dictionaries
			reader = csv.DictReader(input_file)

			# check if the file is in the correct format
			self.__input_format.validate_format(reader.fieldnames)

			for record in reader:
				# get person NAME
				name = self.__create_name(record)

				# if name was already marked as unidentified, don't try to extract id
				if name in self.__unidentified_names:
					continue

				# extract PERSON ID from name
				person_record = existing_matches.get_record_from_match_name(name)

				# does person exist?
				if person_record is None:  # no matching person found
					self.__unidentified_names.append(name)
					continue
				person_id = person_record[MatchFormatEnum.id]

				# person exists, create the WHOLE OUTPUT RECORD

				output_segment = {}
				for index in self.output_format:
					output_segment[index] = ""

				# add SOURCE name
				output_segment[self.output_format.source] = self.__input_format.format_name()

				# add NAME, ID to result
				output_segment[self.output_format.person_name] = name
				output_segment[self.output_format.id] = person_id

				# copy all REMAINING existing information = MAPPED FIELDS
				for input_column_name in reader.fieldnames:
					item = record[input_column_name]

					output_column = self.__input_format.get_mapped_column_name(input_column_name)
					# output_column is of SegmentFormatEnum type -> is int if is not none

					if output_column is not None:
						output_segment[output_column] = item

				# get and add SEGMENT ID
				segment_id = existing_segments.get_id(output_segment,
													  self.__input_format.get_source_id(),
													  self.output_format.segment_id)

				if segment_id is None:
					# no match found - create new id and add to database
					segment_id = existing_segments.get_new_id()
					output_segment[self.output_format.segment_id] = segment_id

					# take note of newly found segment
					new_segment = True
					existing_segments.add_record(output_segment)

				else:
					output_segment[self.output_format.segment_id] = segment_id

				self.result.append(output_segment)

		if new_segment:
			self.__new_segments_found = True
			existing_segments.save()

	def print_message(self):
		"""Prints information if new segments were added to the database.
		Prints names of all the people who were not identified based on their names, if any were not."""

		if self.__new_segments_found:
			print("New segments were added to the database.")
		else:
			print("No new segments were added to the database.")

		print()

		if len(self.__unidentified_names) == 0:
			print("All names were identified.")
		else:
			print("These names could not be identified:")
			for name in self.__unidentified_names:
				print(name)

	@staticmethod
	def __create_name(record):
		return re.sub(' +', ' ', record['Match Name'])
