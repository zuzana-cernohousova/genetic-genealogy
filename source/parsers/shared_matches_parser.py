import csv
from abc import ABC, abstractmethod

from source.databases.databases import CSVInputOutput
from source.parsers.match_parsers import CSVMatchDatabase, FTDNAMatchParser
from source.parsers.headers import SharedMatchesFormatEnum, FTDNAMatchFormat, MatchFormatEnum


class SharedMatchesParser(ABC):
	def __init__(self):
		self.result = []
		self.primary_matches = {}

	@abstractmethod
	def load_primary_matches(self, config_filename):
		"""Reads the configuration file that determines which persons matches are in which file."""
		pass

	@abstractmethod
	def parse_files(self):
		"""Parses files, names of these files are given by the configuration loaded
		from configuration file by the load_primary_matches method"""
		pass

	def save_to_file(self, output_filename):
		"""Saves the output to the given file."""

		CSVInputOutput.save_csv(self.result, output_filename, SharedMatchesFormatEnum)


class FTDNASharedMatchesParser(SharedMatchesParser):

	def __init__(self):
		super().__init__()

		self.__primary_names_not_found = []
		self.__secondary_names_not_found = []
		self.__already_found_pairs = {}
		self.__ID_not_matched = False

	__input_file = FTDNAMatchFormat()

	def load_primary_matches(self, csv_config_filename):
		with open(csv_config_filename, 'r', encoding="utf-8-sig") as input_file:
			reader = csv.DictReader(input_file)

			for row in reader:
				ID = row["id"]
				if ID == "":
					ID = None

				self.primary_matches[(ID, row["name"])] = row["file"]

	def parse_files(self):
		existing_matches = CSVMatchDatabase()
		existing_matches.load()

		for key in self.primary_matches:
			primary_match_id = key[0]
			primary_match_name = key[1]

			if primary_match_id is None:
				# if primary_match_id was not filled, try to find it
				primary_match_id = existing_matches.get_id_from_match_name(primary_match_name)
				if primary_match_id is None:
					self.__primary_names_not_found.append(primary_match_name)
					continue

			with open(self.primary_matches[key], 'r', encoding="utf-8-sig") as file:
				reader = csv.DictReader(file)

				self.__input_file.validate_format(reader.fieldnames)

				for row in reader:
					# parse secondary match record
					secondary_match = FTDNAMatchParser.parse_non_id_columns(row)

					# find secondary match id in all matches
					secondary_match_id = existing_matches.get_id(secondary_match)

					# if the person was not found in POIs matches, skip it, but add it to not found names
					if secondary_match_id is None:
						self.__secondary_names_not_found.append(secondary_match[MatchFormatEnum.person_name])
						continue

					# if the two people are the same, skip the secondary one
					if secondary_match_id == primary_match_id:
						continue

					# if the pair was already identified
					if primary_match_id in self.__already_found_pairs[secondary_match_id] or secondary_match in \
							self.__already_found_pairs[primary_match_id]:
						continue

					output_row = [''] * len(SharedMatchesFormatEnum)
					output_row[SharedMatchesFormatEnum.id_1] = primary_match_id
					output_row[SharedMatchesFormatEnum.name_1] = primary_match_name
					output_row[SharedMatchesFormatEnum.id_2] = secondary_match_id
					output_row[SharedMatchesFormatEnum.name_2] = secondary_match[MatchFormatEnum.person_name]

	def __add_to_already_found(self, key_id, value_id):

		if key_id in self.__already_found_pairs.keys():
			self.__already_found_pairs[key_id].append(value_id)
		else:
			self.__already_found_pairs[key_id] = [value_id]

	def print_message(self):
		if len(self.__primary_names_not_found) == 0 and len(self.__secondary_names_not_found) == 0:
			print("All primary and secondary matches were identified")
			return
		if len(self.__primary_names_not_found) > 0:
			print("These names of primary matches were not identified")
			for name in self.__primary_names_not_found:
				print(name)

		if len(self.__secondary_names_not_found) > 0:
			print("These names of secondary matches were not identified")
			for name in self.__secondary_names_not_found:
				print(name)
