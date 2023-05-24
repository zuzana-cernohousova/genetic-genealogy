import csv
import re

from parsers.headers import MatchFormat, FTDNAMatchFormat, GEDMatchMatchFormat, Databases


class MatchDatabase:
	"""
	Loads all match data from file and holds it.
	"""

	__format = MatchFormat()
	__file_name = "all_matches.csv"

	def __init__(self):
		self.__database = self.__load_from_file()

	def get_id(self, parsed_record):
		""" If the parsed_record already exists, finds it and returns the record ID, else returns -2."""

		name_index = self.__format.get_index('Name')
		source_index = self.__format.get_index('Source')

		for old_record in self.__database:
			if old_record[name_index] == parsed_record[name_index]:
				if old_record[source_index] == parsed_record[source_index]:
					if old_record[1:] == parsed_record[1:]:  # todo rewrite so that id does not have to be in the first position
						return old_record[self.__format.get_index('ID')]

		return None

	def get_new_id(self):
		self.__biggest_ID += 1
		return self.__biggest_ID

	def add_record(self, complete_parsed_record):
		self.__database.append(complete_parsed_record)

	def get_id_from_match_name(self, match_name):
		match_name = re.sub(' +', ' ', match_name)

		for record in self.__database:
			if record[self.__format.get_index('Name')] == match_name:
				return record[self.__format.get_index('ID')]

		return -1

	def __load_from_file(self):
		result = []

		biggest_id = 0
		id_index = self.__format.get_index('ID')

		try:
			with open(self.__file_name, 'r', encoding="utf-8-sig") as input_file:
				reader = csv.reader(input_file)

				# skip header
				for _ in reader:
					break

				for record in reader:
					record_id = int(record[id_index])
					if record_id > biggest_id:
						biggest_id = record_id

						result.append(record)

		except IOError:
			# if the file does not exist or cannot be read, do nothing
			pass

		self.__biggest_ID = biggest_id
		return result

	def save_to_file(self):
		# file will be opened or created
		with open(self.__file_name, "w", newline='', encoding="utf-8-sig") as output_file:
			writer = csv.writer(output_file)
			writer.writerow(self.__format.header)
			for row in self.__database:
				writer.writerow(row)


class MatchParser:

	def __init__(self, input_database):

		if input_database == Databases.FTDNA:
			self.__input_format = FTDNAMatchFormat()
		elif input_database == Databases.GEDMATCH:
			raise NotImplementedError()

		self.__final_format = MatchFormat()
		self.__result = [self.__final_format.header()]

	def parse_file(self, filename):
		"""Reads the file under filename and parses the records into
		the format specified by self.__final_format."""

		existing_records = MatchDatabase()

		# read file
		with open(filename, 'r', encoding="utf-8-sig") as input_file:
			# create csv reader
			reader = csv.reader(input_file)

			# pass the first line containing the Header
			_ = self.__pass_header(reader)

			# for every record in the reader, parse it into the correct format and store it in the self.result list
			for record in reader:
				output_record = [''] * len(self.__final_format.header)

				# add source of information
				output_record[self.__final_format.get_index('Source')] = self.__input_format.get_format_name()

				# create name and add it into result row
				output_record[self.__final_format.get_index('Name')] = self.__create_name(record)

				# copy all relevant existing items from record to output record
				for input_index in range(0, len(record)):
					item = record[input_index]

					output_column_name = self.__input_format.get_mapped_column_name(self.__input_format.get_column_name(input_index))
					if output_column_name is not None:
						new_index = self.__final_format.get_index(output_column_name)
						output_record[new_index] = item

				# get ID or create a new one
				id_index = self.__final_format.get_index('ID')

				record_id = existing_records.get_id(output_record)
				if record_id is None:
					record_id = existing_records.get_new_id()
					output_record[id_index] = record_id

					existing_records.add_record(output_record)
				else:
					output_record[id_index] = record_id
				self.__result.append(output_record)

		existing_records.save_to_file()

	def __create_name(self, row):
		name = [
			row[self.__input_format.get_index("First Name")],
			row[self.__input_format.get_index("Middle Name")],
			row[self.__input_format.get_index("Last Name")]
		]

		return re.sub(' +', ' ', " ".join(name))

	def save_to_file(self, output_filename):
		with open(output_filename, "w", newline='', encoding="utf-8-sig") as output_file:
			writer = csv.writer(output_file)

			for row in self.__result:
				writer.writerow(row)

	@staticmethod
	def __pass_header(reader):
		for header in reader:
			return header
