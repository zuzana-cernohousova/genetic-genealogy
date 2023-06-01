import csv
import re
from abc import ABC, abstractmethod

from source.databases.databases import CSVMatchDatabase, CSVInputOutput
from source.parsers.headers import FTDNAMatchFormat, MatchFormatEnum, FormatEnum, SourceEnum


class Parser(ABC):
	def __init__(self):
		self.result = []

	@abstractmethod
	def parse(self, filename):
		"""Parse data in file defined by filename."""
		pass

	@property
	@abstractmethod
	def _output_format(self):
		"""Defines the format of the parsed data."""
		pass

	def save_to_file(self, output_filename):
		"""Saves the result of parsing to the given file."""
		CSVInputOutput.save_csv(self.result, self._output_format, filename=output_filename)


class MatchParser(Parser, ABC):
	@property
	def _output_format(self):
		return MatchFormatEnum


class FTDNAMatchParser(MatchParser):

	def __init__(self):
		super().__init__()
		self.__new_matches = []

	__input_format = FTDNAMatchFormat

	def parse(self, filename:str):
		"""Reads the file under filename and parses the records into
		the format specified by MatchFormatEnum."""

		existing_records = CSVMatchDatabase()
		existing_records.load()

		new_records_found = False

		# read file
		with open(filename, 'r', encoding="utf-8-sig") as input_file:
			# create csv DictReader
			reader = csv.DictReader(input_file)

			# check if the file is in the correct format
			if not self.__input_format.validate_format(reader.fieldnames):
				raise ValueError("Wrong input format.")

			# for every record in the reader, parse it into the correct format and store it in the self.__result list
			for record in reader:
				# create a new dict for the record and fill it with non-id columns
				output_record = self.parse_non_id_columns(record)

				# get ID or create a new one
				record_id = existing_records.get_id(output_record, self.__input_format.get_source_id())

				# id was not found, match does not yet exist in our database
				if record_id is None:
					record_id = existing_records.get_new_id()
					output_record[MatchFormatEnum.id] = record_id

					# add new record to the existing ones
					new_records_found = True
					existing_records.add_record(output_record)

					self.__new_matches.append(output_record)

				# id was found, match does exist
				else:
					output_record[MatchFormatEnum.id] = record_id

				# add the record to the result list
				self.result.append(output_record)

		# if new records were found during parsing, save the database
		if new_records_found:
			existing_records.save()

	def print_message(self):
		if len(self.__new_matches) == 0:
			print("No new matches found.")
		else:
			print("These new matches were found:")
			for new_match in self.__new_matches:
				print("id= " + str(new_match[self._output_format.id]) + ", name= " + new_match[
					self._output_format.person_name])

	@staticmethod
	def __create_name(row: dict):
		"""Create unified name from """

		# these values will be used for creating name
		name = [
			row["First Name"],
			row["Middle Name"],
			row["Last Name"]
		]

		# delete additional spaces and return
		return re.sub(' +', ' ', " ".join(name))

	@staticmethod
	def parse_non_id_columns(record: dict) -> dict:
		"""Parses all columns that are not defined by this application (all except for id)
		and therefore does not require database access."""

		i_f = FTDNAMatchParser.__input_format

		output_record = {}
		for index in MatchFormatEnum:
			output_record[index] = ""

		# add source name
		output_record[MatchFormatEnum.source] = i_f.format_name()

		# create name and add it into result row
		output_record[MatchFormatEnum.person_name] = FTDNAMatchParser.__create_name(record)

		# copy all relevant existing items from record to output record
		for input_column_name in i_f.get_header():
			item = record[input_column_name]

			output_column = i_f.get_mapped_column_name(input_column_name)
			# output_column is of MatchFormatEnum type -> is int if is not none

			if output_column is not None:
				output_record[output_column] = item

		return output_record
