import csv
from abc import ABC, abstractmethod

from source.parsers.match_parsers import CSVMatchDatabase, FTDNAMatchParser, Parser
from source.parsers.formats import SharedMatchesFormatEnum, FTDNAMatchFormat, MatchFormatEnum


class SharedMatchesParser(Parser, ABC):
	"""Parser used for parsing matches in common with other matches of POI - shared matches."""

	def __init__(self):
		super().__init__()

		# create a dict where paths to the files will be stored under the name of the primary match
		self._primary_matches = {}

	@property
	def _output_format(self):
		return SharedMatchesFormatEnum

	@abstractmethod
	def load_primary_matches(self, config_filename):
		"""Reads the configuration file that determines which persons matches are in which file."""
		pass

	@abstractmethod
	def parse(self, filename):
		"""Parses files, names of these files are given by the configuration loaded
		from configuration file by the load_primary_matches method"""
		pass


class FTDNASharedMatchesParser(SharedMatchesParser):
	"""Parses shared matches data from the FamilyTreeDNA database."""

	def __init__(self):
		super().__init__()

		self.__primary_matches_not_found = []
		self.__secondary_matches_not_found = []
		self.__already_found_pairs = []

	__input_format = FTDNAMatchFormat

	def load_primary_matches(self, csv_config_filename):
		with open(csv_config_filename, 'r', encoding="utf-8-sig") as input_file:
			reader = csv.DictReader(input_file)

			for row in reader:
				ID = row["id"]
				if ID == "":
					ID = None
				name = row["name"]
				if name == "":
					name = None

				# at least one of the identifiers must be given
				if ID is None and name is None:
					raise ValueError("No identifier given for a person.")

				self._primary_matches[(ID, name)] = row["file"]

	def parse(self, filename):

		self.load_primary_matches(filename)

		existing_matches = CSVMatchDatabase()
		existing_matches.load()

		# for each person in primary matches, parse their file
		for key in self._primary_matches:
			primary_match_id = key[0]
			primary_match_name = key[1]

			if primary_match_id is None:
				# if primary_match_id was not filled, try to find it
				primary_match = existing_matches.get_record_from_match_name(primary_match_name)

				# not found --> skip
				if primary_match is None:
					self.__primary_matches_not_found.append(primary_match_name)
					continue

				primary_match_id = primary_match[MatchFormatEnum.person_id]

			if primary_match_name is None:
				# if primary_match_name was not filled, try to find it
				primary_match = existing_matches.get_record_from_id(primary_match_id)

				# not found --> skip
				if primary_match is None:
					self.__primary_matches_not_found.append("id = " + primary_match_id)
					continue

				primary_match_name = primary_match[MatchFormatEnum.person_name]

			# primary person identified --> find their shared matches
			with open(self._primary_matches[key], 'r', encoding="utf-8-sig") as file:
				reader = csv.DictReader(file)

				if not self.__input_format.validate_format(reader.fieldnames):
					raise ValueError("Wrong input format.")

				for row in reader:
					# parse secondary match record, use FTDNAMatchParser
					secondary_match = FTDNAMatchParser.parse_non_id_columns(row)

					# find secondary match id in all matches
					secondary_match_id = existing_matches.get_id(
						secondary_match,
						self.__input_format.get_source_id(),
						MatchFormatEnum.person_id
					)

					# if the person was not found in POIs matches, skip it, but add it to not found names
					if secondary_match_id is None:
						self.__secondary_matches_not_found.append(secondary_match[MatchFormatEnum.person_name])
						continue

					# if the two people are the same, skip the secondary one
					if secondary_match_id == primary_match_id:
						continue

					# if the pair was already identified
					if {primary_match_id, secondary_match_id} in self.__already_found_pairs:
						continue

					# add to already found pairs
					self.__already_found_pairs.append({primary_match_id, secondary_match_id})

					# create output record and add all columns gained from FamilyTreeDNA
					output_row = [''] * len(SharedMatchesFormatEnum)
					output_row[SharedMatchesFormatEnum.id_1] = primary_match_id
					output_row[SharedMatchesFormatEnum.name_1] = primary_match_name
					output_row[SharedMatchesFormatEnum.id_2] = secondary_match_id
					output_row[SharedMatchesFormatEnum.name_2] = secondary_match[MatchFormatEnum.person_name]

					self._result.append(output_row)

	def print_message(self):
		"""Prints which matches were not identified in matches database if any were not."""

		if len(self.__primary_matches_not_found) == 0 and len(self.__secondary_matches_not_found) == 0:
			print("All primary and secondary matches were identified")
			return

		if len(self.__primary_matches_not_found) > 0:
			print("These names of primary matches were not identified")
			for name in self.__primary_matches_not_found:
				print(name)

		if len(self.__secondary_matches_not_found) > 0:
			print("These names of secondary matches were not identified")
			for name in self.__secondary_matches_not_found:
				print(name)
