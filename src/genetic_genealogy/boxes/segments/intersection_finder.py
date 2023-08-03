from abc import ABC, abstractmethod

from genetic_genealogy.project.config_helper import ConfigHelper
from genetic_genealogy.csv_io import CSVHelper
from genetic_genealogy.exit_codes import ExitCodes
from genetic_genealogy.parsers.formats import SegmentIntersectionFormatEnum, SegmentFormatEnum


class IntersectionFinder(ABC):
	@abstractmethod
	def load_segments(self, source, from_database=False) -> None:
		"""Loads segments. Intersections of these loaded segments will later be found."""
		pass

	@abstractmethod
	def save_intersections(self, result, output_destination) -> None:
		"""Saves found segments to the output_destination."""
		pass

	@abstractmethod
	def find_intersections_of_segment(self, segment_id) -> list:
		"""Finds all segments that intersect a specified segment,
		finds the intersection start- and end-points."""

	@abstractmethod
	def find_intersections_of_person(self, person_id) -> list:
		"""Finds all intersections of all segments shared with a given person."""

	@abstractmethod
	def find_all_intersections(self) -> list:
		"""Finds all intersections of all segments loaded."""


class CSVIntersectionFinder(IntersectionFinder):
	def __init__(self):
		super(CSVIntersectionFinder, self).__init__()
		self._segments = []

		self._segments_by_int_id = {}
		self._segments_by_chromosome = {}

	__segment_format = SegmentFormatEnum
	__output_format = SegmentIntersectionFormatEnum

	def load_segments(self, segments_filename=None, from_database=False):
		"""
		Loads segments. Intersections of these loaded segments will later be found.

		Loads segments from CSV file. If filename is not specified, segment database specified in
		project configuration is used.
		Build a dictionary of segments over ids and over chromosomes."""

		if from_database:
			segments_filename = ConfigHelper.get_segment_database_location()

		try:
			self._segments = CSVHelper.load_csv(segments_filename, self.__segment_format)

		except FileNotFoundError:
			print("The source file was not found.")
			exit(ExitCodes.no_such_file)
		except IOError:
			print("The source file could not be loaded.")
			exit(ExitCodes.io_error)

		self._create_segments_by_id()
		self._create_segments_by_chromosome()

	def save_intersections(self, result, output_filename=None):
		"""Saves the found intersections to file or to standard output if output_filename is None."""

		CSVHelper.save_csv(result, SegmentIntersectionFormatEnum, output_filename)

	def _create_segments_by_id(self) -> None:
		for segment in self._segments:
			# create a dict where ids are keys
			self._segments_by_int_id[int(segment[self.__segment_format.segment_id])] = segment

	def _create_segments_by_chromosome(self) -> None:
		# create a dict where chromosome ids are keys and values are lists of segments
		# will be used for faster computation
		for segment in self._segments:
			chrom_id = segment[self.__segment_format.chromosome_id]
			if chrom_id in self._segments_by_chromosome.keys():
				self._segments_by_chromosome[chrom_id].append(segment)
			else:
				self._segments_by_chromosome[chrom_id] = [segment]

	def find_intersections_of_segment(self, segment_id) -> list:
		"""Finds all segments that intersect a specified segment,
		finds the intersection start- and end-points."""

		if int(segment_id) not in self._segments_by_int_id.keys():
			# if segment is not known, cannot find anything
			return []

		sf = self.__segment_format

		segment = self._segments_by_int_id[int(segment_id)]
		chromosome_id = segment[sf.chromosome_id]
		if chromosome_id not in self._segments_by_chromosome.keys():
			return []

		result = []
		chromosome = self._segments_by_chromosome[chromosome_id]

		for s in chromosome:
			# for every other segment on the same chromosome
			if int(s[sf.segment_id]) == int(segment_id):
				# it is the same segment, skip it
				continue

			intersection = self.__check_and_get_intersection(s, segment)

			if intersection is not None:
				output_row = self.__create_and_fill_output_row(s, segment, intersection)
				result.append(output_row)

		return result

	def find_intersections_of_person(self, person_id) -> list:
		"""Finds all intersections of all segments shared with a given person."""
		result = []
		for segment in self.__get_segments_of_person(person_id):
			result.extend(self.find_intersections_of_segment(segment[self.__segment_format.segment_id]))

		return result

	def __get_segments_of_person(self, person_id) -> list:
		result = []

		for segment in self._segments:
			if int(segment[self.__segment_format.person_id]) == int(person_id):
				result.append(segment)

		return result

	def find_all_intersections(self) -> list:
		"""Finds all intersections of all segments loaded."""
		sf = self.__segment_format
		result = []

		for chrom_id in self._segments_by_chromosome:
			chromosome = self._segments_by_chromosome[chrom_id]

			# sort all segments on one chromosome by start
			chromosome.sort(key=lambda x: int(x[self.__segment_format.start]))

			# go from the start and keep track of which segments have not yet ended
			open_segments = []
			for segment in chromosome:
				current_position = segment[self.__segment_format.start]

				for o in open_segments:
					if int(o[sf.end]) < int(current_position):
						# close ended segment
						open_segments.remove(o)
						continue

					# if segment has not ended yet, there is an intersection
					intersection = self.__check_and_get_intersection(segment, o)

					output_row = self.__create_and_fill_output_row(segment, o, intersection)
					result.append(output_row)

				# open_segments current segment
				open_segments.append(segment)

		return result

	@staticmethod
	def __check_and_get_intersection(segment_s, segment_r):
		"""Checks if the two given segments intersect.
		If yes, it returns the start and the end of the intersecting region as a tuple."""
		sf = CSVIntersectionFinder.__segment_format
		coords = [
			(
				(segment_s[sf.start], segment_s[sf.end]),
				(segment_r[sf.start], segment_r[sf.end])
			),
			(
				(segment_r[sf.start], segment_r[sf.end]),
				(segment_s[sf.start], segment_s[sf.end])
			)
		]

		for cs in coords:
			s_s = int(cs[0][0])
			s_e = int(cs[0][1])
			r_s = int(cs[1][0])
			r_e = int(cs[1][1])

			if s_s <= r_s <= s_e:
				if r_e <= s_e:
					return r_s, r_e
				else:
					return r_s, s_e

			if s_s <= r_e <= s_e:
				return s_s, r_e

		return None

	def __create_and_fill_output_row(self, s1, s2, intersection) -> list:
		sf = self.__segment_format
		of = self.__output_format

		row = ['' for _ in of]

		row[of.person_id_1] = s1[sf.person_id]
		row[of.person_id_2] = s2[sf.person_id]

		row[of.segment_1_id] = s1[sf.segment_id]
		row[of.segment_2_id] = s2[sf.segment_id]

		row[of.start] = intersection[0]
		row[of.end] = intersection[1]
		row[of.length_snp] = intersection[1] - intersection[0] + 1

		return row
