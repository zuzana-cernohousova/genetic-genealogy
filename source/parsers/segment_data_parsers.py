import csv
import re
from abc import ABC, abstractmethod

from source.databases.databases import CSVMatchDatabase, CSVSegmentDatabase
from source.parsers.formats import FTDNASegmentFormatEnum, ListCSV_GEDmatchSegmentFormatEnum, SegmentSearch_GEDmatchSegmentFormatEnum, SegmentFormatEnum
from source.parsers.match_parsers import Parser


class SegmentParser(Parser, ABC):
	"""Class used for parsing segments. Child classes are used for parsing input from different databases."""

	def __init__(self):
		super().__init__()
		self._unidentified_identifiers = []
		self._new_segments_found = False

	@classmethod
	def _output_format(cls):
		return SegmentFormatEnum

	def parse(self, filename: str) -> None:
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
			if not self._input_format().validate_format(reader.fieldnames):
				raise ValueError("Wrong input format.")

			reader.fieldnames = self._get_enum_fieldnames(reader.fieldnames)

			for record in reader:
				person_id = self._find_person_id(existing_matches, record)
				if person_id is None:
					if record[self._input_format().person_identifier] not in self._unidentified_identifiers:
						self._unidentified_identifiers.append(record[self._input_format().person_identifier])
					continue

				# person exists, create the WHOLE OUTPUT RECORD
				output_segment = {}
				for index in self._output_format():
					output_segment[index] = ""

				# add SOURCE name
				output_segment[self._output_format().source] = self._input_format().format_name()

				# add NAME, ID to result
				output_segment[self._output_format().person_name] = existing_matches.get_record_from_id(person_id)[
					existing_matches.format.person_name]
				output_segment[self._output_format().person_id] = person_id

				# copy all REMAINING existing information = MAPPED FIELDS
				for input_column_name in reader.fieldnames:
					item = record[input_column_name]

					output_column = self._input_format().get_mapped_column_name(input_column_name)
					# output_column is of SegmentFormatEnum type -> is int if is not none

					if output_column is not None:
						output_segment[output_column] = " ".join(item.split())

				# get and add SEGMENT ID
				segment_id = existing_segments.get_id(
					output_segment,
					self._input_format().get_source_id(),
					self._output_format().segment_id
				)

				if segment_id is None:
					# no match found - create new id and add to database
					segment_id = existing_segments.get_new_id()
					output_segment[self._output_format().segment_id] = segment_id

					# take note of newly found segment
					new_segment = True
					existing_segments.add_record(output_segment)

				else:
					output_segment[self._output_format().segment_id] = segment_id

				self._result.append(output_segment)

		if new_segment:
			self._new_segments_found = True
			existing_segments.save()

	@classmethod
	def _get_enum_fieldnames(cls, fieldnames) -> list:
		result = []
		for name in fieldnames:
			for enum_name in cls._input_format():
				if "".join(name.split()).lower() == "".join(enum_name.split()).lower():
					result.append(enum_name)

		return result

	@classmethod
	@abstractmethod
	def _find_person_id(cls, match_database: CSVMatchDatabase, record: dict):
		pass

	@ abstractmethod
	def print_message(self) -> None:
		pass


class FTDNASegmentParser(SegmentParser):
	"""Parses segment data exported from FamilyTreeDNA database."""

	@classmethod
	def _input_format(cls):
		return FTDNASegmentFormatEnum

	@classmethod
	def _find_person_id(cls, match_database: CSVMatchDatabase, record: dict) -> int | None:
		name = cls.__create_name(record)
		person = match_database.get_record_from_match_name(name)

		if person is not None:
			return int(person[match_database.format.person_id])

		return None

	@classmethod
	def __create_name(cls, record: dict) -> str:
		return re.sub(' +', ' ', record[cls._input_format().match_name])

	def print_message(self) -> None:
		"""Prints information if new segments were added to the database.
		Prints names of all the people who were not identified based on their names, if any were not."""
		if self._new_segments_found:
			print("New segments were added to the database.")
		else:
			print("No new segments were added to the database.")

		if len(self._unidentified_identifiers) == 0:
			print("All people were identified in the match database.")
		else:
			print("These names could not be identified:")
			for name in self._unidentified_identifiers:
				print(name)
		# todo print also name if from GEDmatch


class GEDmatchSegmentParser(SegmentParser, ABC):
	@classmethod
	def _find_person_id(cls, match_database: CSVMatchDatabase, record: dict) -> int | None:
		person = match_database.get_record_from_gedmatch_id(" ".join(record[cls._input_format().matched_kit].split()))
		if person is not None:
			return int(person[match_database.format.person_id])

		return None

	def print_message(self) -> None:
		"""Prints information if new segments were added to the database.
		Prints gedmatch identifiers of all the people who were not identified based on their names, if any were not."""
		if self._new_segments_found:
			print("New segments were added to the database.")
		else:
			print("No new segments were added to the database.")

		if len(self._unidentified_identifiers) == 0:
			print("All people were identified in the match database.")
		else:
			print("These kit numbers could not be identified:")
			for kit_number in self._unidentified_identifiers:
				print(kit_number.strip())


class ListCSV_GEDmatchSegmentParser(GEDmatchSegmentParser):
	@classmethod
	def _input_format(cls):
		return ListCSV_GEDmatchSegmentFormatEnum


class SegmentSearch_GEDmatchSegmentParser(GEDmatchSegmentParser):
	@classmethod
	def _input_format(cls):
		return SegmentSearch_GEDmatchSegmentFormatEnum
