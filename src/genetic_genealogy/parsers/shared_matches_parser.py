import csv
import sys
from abc import ABC, abstractmethod

from genetic_genealogy.csv_io import CSVHelper
from genetic_genealogy.helper import one_space
from genetic_genealogy.parsers.match_parsers import CSVMatchDatabase, FTDNAMatchParser, Parser
from genetic_genealogy.parsers.formats import SharedMatchesFormatEnum, FTDNAMatchFormatEnum, MatchFormatEnum, \
	PrimaryMatchesEnum, \
	GEDmatchMatchFormatEnum


class SharedMatchesParser(Parser, ABC):
	"""Parser used for parsing matches in common with other matches of POI - shared matches."""

	def __init__(self):
		super().__init__()

		# create a dict where paths to the files will be stored under the name of the primary match
		self._primary_matches = {}

		self._primary_matches_not_found = []
		self._files_not_parsed = []
		self._secondary_matches_not_found = []
		self._already_found_pairs = []

	@classmethod
	def _output_format(cls):
		return SharedMatchesFormatEnum

	_primary_match_format = PrimaryMatchesEnum

	def _load_primary_matches(self, csv_config_filename=None):
		"""This method will load primary matches ids and corresponding filepaths from configuration file.
		If the csv_config_filename is None, data will be read from standard input."""

		try:
			if csv_config_filename is None:
				input_file = sys.stdin.read().splitlines()
				self._load_pm_from_dict_reader(csv.DictReader(input_file))

			else:
				with open(csv_config_filename, 'r', encoding="utf-8-sig") as input_file:
					self._load_pm_from_dict_reader(csv.DictReader(input_file))

		except IOError:
			print("File could not be parsed.")
			exit(1)
		# todo exit code

	def _load_pm_from_dict_reader(self, reader):
		for row in reader:
			ID = row[self._primary_match_format.person_id]
			if ID is None:
				raise ValueError("Primary match must be identified by person_id.")
			# todo print message and exit code

			self._primary_matches[ID] = row[self._primary_match_format.path]

	def parse(self, configuration_file=None):
		"""Parses input data from files - paths to these files are specified by the configuration file given as
		a parameter to this method.
		The configuration file, which is a csv file, determines the ids of primary matches and the paths to the
		files corresponding to them. In those files, there are regular match data in source specific format.
		Matches from those files are referred to as secondary matches and
		they are matches in common with the POI and the given primary match.

		The header of the configuration csv file should be 'person_id,path'."""

		self._load_primary_matches(configuration_file)

		existing_matches = CSVMatchDatabase()
		existing_matches.load()

		# for each person in primary matches, parse their file
		for primary_match_id in self._primary_matches:
			primary_match = existing_matches.get_record_from_id(int(primary_match_id))

			if primary_match is None:
				self._primary_matches_not_found.append(primary_match_id)
				continue

			primary_match_name = primary_match[MatchFormatEnum.person_name]

			try:
				with open(self._primary_matches[primary_match_id], 'r', encoding="utf-8-sig") as file:
					reader = csv.DictReader(file)

					reader.fieldnames = CSVHelper.get_enum_fieldnames(self._input_format(), reader.fieldnames)

					if not self._input_format().validate_format(reader.fieldnames):
						raise ValueError("Wrong input format.")

					for row in reader:
						# parse secondary match record - only part that is genetic_genealogy dependant
						secondary_match_id, secondary_match_name = self._get_secondary_match_id_and_name(
							existing_matches,
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

			except IOError:
				self._files_not_parsed.append(primary_match_id)

	@abstractmethod
	def _get_secondary_match_id_and_name(self, existing_matches, input_row) -> (int, str):
		"""Gets secondary match information from match database (existing_matches).
		Is source database specific."""
		pass

	@abstractmethod
	def _fill_in_match_statistics(self, input_row, output_row) -> None:
		"""Gets match statistics from input row. Is source database specific."""
		pass

	def print_message(self) -> None:
		"""Prints which matches were not identified in matches database if any were not."""

		if len(self._primary_matches_not_found) == 0 and len(self._secondary_matches_not_found) == 0 and len(
				self._files_not_parsed) == 0:
			print("All primary and secondary matches were identified")
			return

		if len(self._primary_matches_not_found) > 0:
			print("These ids of primary matches were not identified")
			for person_id in self._primary_matches_not_found:
				print(person_id)

		if len(self._files_not_parsed) > 0:
			print("These files were not parsed.")
			for person_id in self._files_not_parsed:
				print(person_id)

		if len(self._secondary_matches_not_found) > 0:
			print("These names of secondary matches were not identified")
			for name in self._secondary_matches_not_found:
				print(name)


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
		kit_id = one_space(input_row[self._input_format().matched_kit])
		name = one_space(input_row[self._input_format().matched_name])

		match = existing_matches.get_record_from_gedmatch_id(kit_id)
		if match is not None:
			return match[MatchFormatEnum.person_id], name

		return None, name

	def _fill_in_match_statistics(self, input_row, output_row) -> None:
		mapping = self._input_format().shared_matches_mapping()
		for index in self._input_format():
			if index in mapping:
				output_row[mapping[index]] = one_space(input_row[index])
