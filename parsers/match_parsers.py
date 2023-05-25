import csv
import re

from databases.match_databases import CSVMatchDatabase
from parsers.headers import FTDNAMatchFormat, Databases, MatchFormatEnum


class MatchParser:

	def __init__(self, input_database):

		if input_database == Databases.FTDNA:
			self.__input_format = FTDNAMatchFormat()
		elif input_database == Databases.GEDMATCH:
			raise NotImplementedError("Cannot parse data from GEDMATCH")

		self.__result = []

	def parse_file(self, filename):
		"""Reads the file under filename and parses the records into
		the format specified by MatchFormatEnum."""

		existing_records = CSVMatchDatabase()
		existing_records.load()

		new_records_found = False

		# read file
		with open(filename, 'r', encoding="utf-8-sig") as input_file:
			# create csv DictReader
			reader = csv.DictReader(input_file)

			# for every record in the reader, parse it into the correct format and store it in the self.__result list
			for record in reader:
				output_record = {}
				for index in MatchFormatEnum:
					output_record[index] = ""

				# add source name
				output_record[MatchFormatEnum.source] = self.__input_format.format_name

				# create name and add it into result row
				output_record[MatchFormatEnum.person_name] = self.__create_name(record)

				# copy all relevant existing items from record to output record
				for input_column_name in reader.fieldnames:
					item = record[input_column_name]

					output_column = self.__input_format.get_mapped_column_name(input_column_name)
					# output_column is of MatchFormatEnum type -> is int if is not none

					if output_column is not None:
						output_record[output_column] = item

				# get ID or create a new one
				record_id = existing_records.get_id(output_record)

				# id was not found, match does not yet exist in our database
				if record_id is None:
					record_id = existing_records.get_new_id()
					output_record[MatchFormatEnum.id] = record_id

					# add new record to the existing ones
					new_records_found = True
					existing_records.add_record(output_record)

				# id was found, match does exist
				else:
					output_record[MatchFormatEnum.id] = record_id

				# add the record to the result list
				self.__result.append(output_record)

		if new_records_found:
			existing_records.save()

	def save_to_file(self, output_filename):
		"""Saves the output to the given file."""
		with open(output_filename, "w", newline='', encoding="utf-8-sig") as output_file:
			writer = csv.writer(output_file)
			writer.writerow(MatchFormatEnum.get_header())

			for row in self.__result:
				writer.writerow(row.values())

	@staticmethod
	def __create_name(row):
		name = [
			row["First Name"],
			row["Middle Name"],
			row["Last Name"]
		]

		return re.sub(' +', ' ', " ".join(name))
