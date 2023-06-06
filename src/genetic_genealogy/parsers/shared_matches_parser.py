import csv
from abc import ABC, abstractmethod

from genetic_genealogy.parsers.match_parsers import CSVMatchDatabase, FTDNAMatchParser, Parser
from genetic_genealogy.parsers.formats import SharedMatchesFormatEnum, FTDNAMatchFormatEnum, MatchFormatEnum, PrimaryMatchesEnum, \
	GEDmatchMatchFormatEnum


class SharedMatchesParser(Parser, ABC):
	"""Parser used for parsing matches in common with other matches of POI - shared matches."""

	def __init__(self):
		super().__init__()

		# create a dict where paths to the files will be stored under the name of the primary match
		self._primary_matches = {}

		self._primary_matches_not_found = []
		self._secondary_matches_not_found = []
		self._already_found_pairs = []

	@classmethod
	def _output_format(cls):
		return SharedMatchesFormatEnum

	_primary_match_format = PrimaryMatchesEnum

	def load_primary_matches(self, csv_config_filename):
		with open(csv_config_filename, 'r', encoding="utf-8-sig") as input_file:
			reader = csv.DictReader(input_file)

			for row in reader:
				ID = row[self._primary_match_format.person_id]
				if ID == "":
					ID = None
				name = row[self._primary_match_format.person_name]
				if name == "":
					name = None

				# at least one of the identifiers must be given
				if ID is None and name is None:
					raise ValueError("No identifier given for a person.")

				self._primary_matches[(ID, name)] = row[self._primary_match_format.path]

	def parse(self, filename):
		"""Parses files, names of these files are given by the configuration loaded
		from configuration file by the load_primary_matches method"""

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
					self._primary_matches_not_found.append(primary_match_name)
					continue

				primary_match_id = primary_match[MatchFormatEnum.person_id]

			if primary_match_name is None:
				# if primary_match_name was not filled, try to find it
				primary_match = existing_matches.get_record_from_id(int(primary_match_id))

				# not found --> skip
				if primary_match is None:
					self._primary_matches_not_found.append("id = " + primary_match_id)
					continue

				primary_match_name = primary_match[MatchFormatEnum.person_name]

			# primary person identified --> find their shared matches
			with open(self._primary_matches[key], 'r', encoding="utf-8-sig") as file:
				reader = csv.DictReader(file)

				reader.fieldnames = self._get_enum_fieldnames(reader.fieldnames)

				if not self._input_format().validate_format(reader.fieldnames):
					raise ValueError("Wrong input format.")

				for row in reader:
					# parse secondary match record - only part that is genetic_genealogy dependant
					secondary_match_id, secondary_match_name = self._get_secondary_match_id_and_name(existing_matches,
																									 row)

					# if the person was not found in POIs matches, skip it, but add it to not found names
					if secondary_match_id is None:
						self._secondary_matches_not_found.append(row[self._input_format().person_identifier])
						continue

					# if the two people are the same, skip the secondary one
					if secondary_match_id == primary_match_id:
						continue

					# if the pair was already identified
					if {primary_match_id, secondary_match_id} in self._already_found_pairs:
						continue

					# add to already found pairs
					self._already_found_pairs.append({primary_match_id, secondary_match_id})

					# create output record and add all columns gained from FamilyTreeDNA
					output_row = [''] * len(SharedMatchesFormatEnum)
					output_row[self._output_format().id_1] = primary_match_id
					output_row[self._output_format().name_1] = primary_match_name
					output_row[self._output_format().id_2] = secondary_match_id
					output_row[self._output_format().name_2] = secondary_match_name

					# genetic_genealogy specific - we do not have match statistics from FTDNA
					self._fill_in_match_statistics(row, output_row)

					self._result.append(output_row)

	@abstractmethod
	def _get_secondary_match_id_and_name(self, existing_matches, input_row) -> (int, str):
		pass

	@abstractmethod
	def _fill_in_match_statistics(self, input_row, output_row) -> None:
		pass

	def print_message(self) -> None:
		"""Prints which matches were not identified in matches database if any were not."""

		if len(self._primary_matches_not_found) == 0 and len(self._secondary_matches_not_found) == 0:
			print("All primary and secondary matches were identified")
			return

		if len(self._primary_matches_not_found) > 0:
			print("These names of primary matches were not identified")
			for name in self._primary_matches_not_found:
				print(name)

		if len(self._secondary_matches_not_found) > 0:
			print("These names of secondary matches were not identified")
			for name in self._secondary_matches_not_found:
				print(name)

	@classmethod
	def _get_enum_fieldnames(cls, fieldnames) -> list:
		result = []
		for name in fieldnames:
			for enum_name in cls._input_format():
				if "".join(name.split()).lower() == "".join(enum_name.split()).lower():
					result.append(enum_name)

		return result


class FTDNASharedMatchesParser(SharedMatchesParser):
	"""Parses shared matches data from the FamilyTreeDNA database."""

	@classmethod
	def _input_format(cls):
		return FTDNAMatchFormatEnum

	def _get_secondary_match_id_and_name(self, existing_matches, input_row) -> (int | None, str):
		match = FTDNAMatchParser.parse_non_id_columns(input_row)
		name = match[MatchFormatEnum.person_name]

		secondary_match = existing_matches.get_record_from_match_name(name)
		if secondary_match is not None:
			return secondary_match[MatchFormatEnum.person_id], name

		return None, name

	def _fill_in_match_statistics(self, input_row, output_row) -> None:
		# when data is from FamilyTreeDNA, we do not get information
		# about shared centimorgans between the two other matches
		return None


class GEDmatchSharedMatchesParser(SharedMatchesParser):
	"""Parses shared matches data from the GEDmatch database."""

	@classmethod
	def _input_format(cls):
		return GEDmatchMatchFormatEnum

	def _get_secondary_match_id_and_name(self, existing_matches, input_row) -> (int | None, str):
		kit_id = self.__strip(input_row[self._input_format().matched_kit])
		name = self.__strip(input_row[self._input_format().matched_name])

		match = existing_matches.get_record_from_gedmatch_id(kit_id)
		if match is not None:
			return match[MatchFormatEnum.person_id], name

		return None, name

	def _fill_in_match_statistics(self, input_row, output_row) -> None:
		mapping = self._input_format().shared_matches_mapping()
		for index in self._input_format():
			if index in mapping:
				output_row[mapping[index]] = self.__strip(input_row[index])

	@classmethod
	def __strip(cls, item):
		return " ".join(item.split())
