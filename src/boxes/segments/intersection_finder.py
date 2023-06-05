from abc import ABC, abstractmethod

from src.project.config_reader import ConfigReader
from src.databases.match_database import CSVInputOutput
from src.parsers.formats import SegmentIntersectionFormatEnum, SegmentFormatEnum


class IntersectionFinder(ABC):
	@abstractmethod
	def load_segments(self, source) -> None:
		pass

	@abstractmethod
	def save_intersections(self, result, output_destination) -> None:
		pass

	def __init__(self):
		self._segments = []

		self._segments_by_id = {}
		self._segments_by_chromosome = {}

	__segment_format = SegmentFormatEnum
	__output_format = SegmentIntersectionFormatEnum

	def _create_segments_by_id(self)  -> None:
		for segment in self._segments:
			# create a dict where ids are keys
			self._segments_by_id[segment[self.__segment_format.segment_id]] = segment

	def _create_segments_by_chromosome(self) -> None:
		# create a dict where chromosome ids are keys and values are lists of segments
		# will be used for faster computation
		for segment in self._segments:
			chrom_id = segment[self.__segment_format.chromosome_id]
			if chrom_id in self._segments_by_chromosome.keys():
				self._segments_by_chromosome[chrom_id].append(segment)
			else:
				self._segments_by_chromosome[chrom_id] = [segment]

	def find_intersections_of_segment(self, segment_id) -> list | None:
		"""Finds all segments that intersect specified segment,
		finds the intersection endpoints."""
		result = []
		if segment_id not in self._segments_by_id.keys():
			return None

		sf = self.__segment_format

		segment = self._segments_by_id[segment_id]
		chromosome_id = segment[sf.chromosome_id]
		if chromosome_id not in self._segments_by_chromosome.keys():
			return None

		chromosome = self._segments_by_chromosome[chromosome_id]

		for s in chromosome:
			if s[sf.segment_id] == segment_id:
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
			if segment[self.__segment_format.person_id] == person_id:
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

					if intersection is None:
						print("meow")

					output_row = self.__create_and_fill_output_row(segment, o, intersection)
					result.append(output_row)

				# open_segments current segment
				open_segments.append(segment)

		return result

	@staticmethod
	def __check_and_get_intersection(segment_s, segment_r):
		sf = IntersectionFinder.__segment_format
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


class CSVIntersectionFinder(IntersectionFinder):
	def __init__(self):
		super(CSVIntersectionFinder, self).__init__()

	__segment_format = SegmentFormatEnum

	def load_segments(self, segments_filename=None):
		"""Loads segments from CSV file. If filename is not specified, segment database specified in
		project configuration is used.
		Build a dictionary of segments over ids and over chromosomes."""
		if segments_filename is None:
			segments_filename = ConfigReader.get_segment_database_location()

		self._segments = CSVInputOutput.load_csv(segments_filename, self.__segment_format)
		self._create_segments_by_id()
		self._create_segments_by_chromosome()

	def save_intersections(self, result, output_filename=None):
		CSVInputOutput.save_csv(result, SegmentIntersectionFormatEnum, output_filename)
