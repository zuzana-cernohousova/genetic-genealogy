import csv
import re
from abc import ABC, abstractmethod

from source.databases.databases import CSVMatchDatabase, CSVInputOutput
from source.parsers.formats import FTDNAMatchFormatEnum, MatchFormatEnum, GEDmatchMatchFormatEnum


class Parser(ABC):
	def __init__(self):
		self._result = []

	@classmethod
	@abstractmethod
	def _input_format(cls):
		pass

	@classmethod
	@abstractmethod
	def _output_format(cls):
		"""Defines the format of the parsed data."""
		pass

	def save_to_file(self, output_filename) -> None:
		"""Saves the result of parsing to the given file."""
		CSVInputOutput.save_csv(self._result, self._output_format(), filename=output_filename)


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

	def parse(self, filename: str) -> None:
		"""Reads the file under filename and parses the records into
		the format specified by MatchFormatEnum."""

		# create and load database
		existing_records = CSVMatchDatabase()
		existing_records.load()

		new_records_found = False

		# read file
		with open(filename, 'r', encoding="utf-8-sig") as input_file:
			# create csv DictReader
			reader = csv.DictReader(input_file)

			# check if the file is in the correct format
			if not self._input_format().validate_format(reader.fieldnames):
				raise ValueError("Wrong input format.")

			reader.fieldnames = self.__get_enum_fieldnames(reader.fieldnames)

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
					new_records_found = True
					existing_records.add_record(output_record)

					self._new_matches.append(output_record)

				# id was found, match does exist
				else:
					output_record[MatchFormatEnum.person_id] = record_id

				# add the record to the result list
				self._result.append(output_record)

		# if new records were found during parsing, save the database
		if new_records_found:
			existing_records.save()
			# todo save updates

	@classmethod
	def __get_enum_fieldnames(cls, fieldnames) -> list:
		result = []
		for name in fieldnames:
			for enum_name in cls._input_format():
				if "".join(name.split()).lower() == "".join(enum_name.split()).lower():
					result.append(enum_name)

		return result

	def print_message(self) -> None:
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
		return re.sub(' +', ' ', " ".join(name))

	@classmethod
	def parse_non_id_columns(cls, record: dict) -> dict:
		i_f = cls._input_format()

		output_record = {}
		for index in cls._output_format():
			output_record[index] = ""

		# add source name
		output_record[cls._output_format().source] = i_f.format_name()

		# create name and add it into result row
		output_record[cls._output_format().person_name] = cls.__create_name(record)

		# copy all relevant existing items from record to output record
		for input_column_name in i_f:
			item = record[input_column_name]

			output_column = i_f.get_mapped_column_name(input_column_name)
			# output_column is of MatchFormatEnum type -> is int if is not none

			if output_column is not None:
				output_record[output_column] = item

		return output_record


class GEDmatchMatchParser(MatchParser):
	@classmethod
	def _input_format(cls):
		return GEDmatchMatchFormatEnum

	@classmethod
	def parse_non_id_columns(cls, record) -> dict:
		i_f = cls._input_format()

		output_record = {}
		for index in MatchFormatEnum:
			output_record[index] = ""

		# add source name
		output_record[MatchFormatEnum.source] = i_f.format_name()

		# copy all relevant existing items from record to output record
		for input_column_name in i_f:
			item = record[input_column_name]

			output_column = i_f.get_mapped_column_name(input_column_name)
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
