import csv
import re
from abc import ABC, abstractmethod

from parsers.headers import MatchFormatEnum


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

		return -1 # todo change to None


class CSVMatchDatabase(MatchDatabase):
	"""
	Loads all match data from file and holds it.
	"""

	def __init__(self):
		self.__file_name = "all_matches.csv"
		# todo load file_name from configuration file

		self.__database = []

	def load(self):
		"""Reads the given csv file and stores it in the database"""

		result = []
		biggest_id = 0

		try:
			with open(self.__file_name, 'r', encoding="utf-8-sig") as input_file:
				reader = csv.DictReader(input_file)
				new_fieldnames = []

				if reader.fieldnames is not None:
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
		self.database = result

	def save(self):
		"""Saves the database to the given csv file."""
		# file will be opened or created
		with open(self.__file_name, "w", newline='', encoding="utf-8-sig") as output_file:
			writer = csv.writer(output_file)

			writer.writerow(MatchFormatEnum.get_header())

			for row in self.database:
				if type(row) is dict:
					writer.writerow(row.values())
				else:  # list
					writer.writerow(row)
