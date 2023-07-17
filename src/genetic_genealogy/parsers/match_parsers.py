import csv
import io
import sys
from abc import ABC, abstractmethod

from genetic_genealogy.databases.match_database import CSVMatchDatabase, CSVHelper
from genetic_genealogy.exit_codes import ExitCodes
from genetic_genealogy.parsers.formats import FTDNAMatchFormatEnum, MatchFormatEnum, GEDmatchMatchFormatEnum
from genetic_genealogy.helper import one_space


class Parser(ABC):
	def __init__(self):
		self._result = []

	@classmethod
	@abstractmethod
	def _input_format(cls):
		"""Defines the format of the input data."""
		pass

	@classmethod
	@abstractmethod
	def _output_format(cls):
		"""Defines the final format of the parsed data."""
		pass

	def save_to_file(self, output_filename) -> None:
		"""Saves the result of parsing to the given file."""
		CSVHelper.save_csv(self._result, self._output_format(), filename=output_filename)

	@abstractmethod
	def parse(self, filename: str) -> None:
		"""Reads the file under filename and parses the records into
		the format specified by _output_format.
		If filename is not specified, data is read from standard input."""
		pass


class MatchParser(Parser, ABC):

	def __init__(self):
		super().__init__()
		self._new_matches = []

	@classmethod
	def _output_format(cls):
		return MatchFormatEnum

	@classmethod
	@abstractmethod
	def parse_non_id_columns(cls, record) -> dict:
		"""Parses all columns that are not defined by this application (all except for id)
		and therefore does not require database access."""
		pass

	def parse(self, filename: str = None) -> None:
		"""Parses records in the given filename.
		If filename is not given, reads from standard input.
		Checks for the correct format."""

		# create and load the database
		existing_records = CSVMatchDatabase()
		existing_records.load()

		self._new_matches = []

		# read file or standard input
		try:
			if filename is None:
				input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8-sig')
				self._parse_from_dict_reader(csv.DictReader(input_stream), existing_records)

			else:
				with open(filename, 'r', encoding="utf-8-sig") as input_file:
					self._parse_from_dict_reader(csv.DictReader(input_file), existing_records)

		except FileNotFoundError:
			print("The source file was not found.")
			exit(ExitCodes.no_such_file)
		except IOError:
			print("File could not be parsed.")
			exit(ExitCodes.io_error)

		# if new records were found during parsing, save the database
		if len(self._new_matches) > 0:
			existing_records.save()

	def _parse_from_dict_reader(self, reader, existing_records):
		"""Parses every record in the given reader,
		compares it to the existing_records database.
		Check if the reader is of the correct format."""

		# check if the file is in the correct format
		if not self._input_format().validate_format(reader.fieldnames):
			print("Wrong matches file format.")
			exit(ExitCodes.wrong_input_format)

		# replace string fieldnames with enum
		reader.fieldnames = CSVHelper.get_strenum_fieldnames(self._input_format(), reader.fieldnames)

		# for every record in the reader, parse it into the correct format and store it in the self.__result list
		for record in reader:
			# create a new dict for the record and fill it with non-id columns
			output_record = self.parse_non_id_columns(record)

			# get ID or create a new one
			record_id = existing_records.get_id(output_record, self._input_format().get_source_id())

			# id was not found, match does not yet exist in our database
			if record_id is None:
				record_id = existing_records.get_new_id()
				output_record[MatchFormatEnum.person_id] = record_id

				# add new record to the existing ones
				existing_records.add_record(output_record)
				self._new_matches.append(output_record)

			# id was found, match does exist
			else:
				output_record[MatchFormatEnum.person_id] = record_id

			# add the record to the result list
			self._result.append(output_record)

	def print_message(self) -> None:
		"""Prints message about the results of the parsing."""

		if len(self._new_matches) == 0:
			print("No new matches found.")
		else:
			print("These new matches were found:")
			for new_match in self._new_matches:
				print("id= " + str(new_match[self._output_format().person_id]) + ", name= " + new_match[
					self._output_format().person_name])


class FTDNAMatchParser(MatchParser):
	"""Parses data exported from FamilyTreeDNA."""

	@classmethod
	def _input_format(cls):
		return FTDNAMatchFormatEnum

	@classmethod
	def __create_name(cls, row: dict) -> str:
		"""Create unified name from name columns."""

		# these values will be used for creating name
		name = [
			row[cls._input_format().first_name],
			row[cls._input_format().middle_name],
			row[cls._input_format().last_name]
		]

		# delete additional spaces and return
		return one_space(" ".join(name))

	@classmethod
	def parse_non_id_columns(cls, record: dict) -> dict:

		output_record = {}
		for index in cls._output_format():
			output_record[index] = ""

		# add genetic_genealogy name
		output_record[cls._output_format().source] = cls._input_format().format_name()

		# create name and add it into result row
		output_record[cls._output_format().person_name] = cls.__create_name(record)

		# copy all relevant existing items from record to output record
		for input_column_name in record.keys():
			# not all columns of input format must be present
			item = record[input_column_name]

			output_column = cls._input_format().get_mapped_column_name(input_column_name)
			# output_column is of MatchFormatEnum type -> is int if is not none

			if output_column is not None:
				output_record[output_column] = item

		return output_record


class GEDmatchMatchParser(MatchParser):
	"""Classed used for parsing match data exported from GEDmatch."""
	@classmethod
	def _input_format(cls):
		return GEDmatchMatchFormatEnum

	@classmethod
	def parse_non_id_columns(cls, record) -> dict:
		output_record = {}
		for index in MatchFormatEnum:
			output_record[index] = ""

		# add genetic_genealogy name
		output_record[MatchFormatEnum.source] = cls._input_format().format_name()

		# copy all relevant existing items from record to output record
		for input_column_name in record.keys():
			item = record[input_column_name]

			output_column = cls._input_format().get_mapped_column_name(input_column_name)
			# output_column is of MatchFormatEnum type -> is int if is not none

			if output_column is not None:
				output_record[output_column] = " ".join(item.split())

		return output_record

	def print_message(self) -> None:
		if len(self._new_matches) == 0:
			print("No new matches found.")
		else:
			print("These new matches were found:")
			for new_match in self._new_matches:
				print("id= " + str(new_match[self._output_format().person_id]) + ", name= " + new_match[
					self._output_format().person_name] + ", gedmatch_id= "
					+ new_match[self._output_format().gedmatch_kit_id])
