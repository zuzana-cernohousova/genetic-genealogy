import csv
import re
from abc import ABC, abstractmethod

from parsers.headers import FTDNAMatchFormat, Databases, MatchFormatEnum


class MatchDatabase(ABC):
	@abstractmethod
	def load(self):
		pass

	@abstractmethod
	def save(self):
		pass

	database = []
	largest_ID = 0

	def get_id(self, parsed_record):
		""" If the parsed_record already exists, finds it and returns the record ID, else returns None."""
		match_record_id = None

		for old_record in self.database:
			match = True

			# compare all fields except for the id field
			for index in MatchFormatEnum:
				if index == MatchFormatEnum.id:
					continue

				if old_record[index] != parsed_record[index]:
					match = False
					break
			if match:
				match_record_id = old_record[MatchFormatEnum.id]
				break

		return match_record_id

	def get_new_id(self):
		"""Creates a new maximum ID and returns it."""
		self.largest_ID += 1
		return self.largest_ID

	def add_record(self, complete_parsed_record):
		"""Adds a complete parsed record to the database list."""
		self.database.append(complete_parsed_record)

	def get_id_from_match_name(self, match_name):
		"""Finds a record based on name and returns the ID. If no record is found, returns None."""
		match_name = re.sub(' +', ' ', match_name)

		for record in self.database:
			if record[MatchFormatEnum.person_name] == match_name:
				return record[MatchFormatEnum.id]

		return -1


class CSVMatchDatabase(MatchDatabase):
	"""
	Loads all match data from file and holds it.
	"""

	def __init__(self):
		self.__file_name = "all_matches.csv"
		self.__database = []

	def load(self):
		"""Reads the given csv file and stores it in the database"""

		result = []
		biggest_id = 0

		try:
			with open(self.__file_name, 'r', encoding="utf-8-sig") as input_file:
				reader = csv.DictReader(input_file)
				new_fieldnames = []

				for index in reader.fieldnames:
					for value in MatchFormatEnum:
						if value.name == index:
							new_fieldnames.append(value)
							break

				reader.fieldnames = new_fieldnames

				for record in reader:
					# print(record)
					record_id = int(record[MatchFormatEnum.id])
					if record_id > biggest_id:
						biggest_id = record_id

						result.append(record)

		except IOError:
			# if the file does not exist or cannot be read, do nothing
			pass

		self.largest_ID = biggest_id
		return result

	def save(self):
		"""Saves the database to the given csv file."""
		# file will be opened or created
		with open(self.__file_name, "w", newline='', encoding="utf-8-sig") as output_file:
			writer = csv.writer(output_file)

			writer.writerow(MatchFormatEnum.get_header())

			for row in self.__database:
				if type(row) is dict:
					writer.writerow(row.values())
				else:  # list
					writer.writerow(row)


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
