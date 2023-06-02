from enum import Enum, IntEnum, StrEnum
from abc import ABC, ABCMeta, abstractmethod


class SourceEnum(Enum):
	GEDmatch = 0
	FamilyTreeDNA = 1


# region Application defined formats
# defined by this application


class FormatEnum(IntEnum):
	"""Child classes of this class define formats of data parsed by this application.
	Name of a csv column is represented by the value name,
	preferred location of the column is defined by the value.
	This class is a child class of IntEnum, so all the values can be used as int values,
	especially as list indexes."""

	@classmethod
	def get_header(cls):
		"""Returns the names of all the enum values in a list ordered by their values."""
		return [item.name for item in cls]

	@classmethod
	def comparison_key(cls, source: SourceEnum = None):
		"""Returns all the values in this enum class that
		should be taken into consideration while comparing two records of this format."""
		return [key for key in cls]


class MatchFormatEnum(FormatEnum):
	"""This class defines the format of parsed match data."""

	@classmethod
	def comparison_key(cls, source: SourceEnum = None):
		"""If source is stated, returns source specific identification
		(gedmatch_kit_id if GEDmatch or person_name if FTDNA)
		 else returns id."""

		if source == SourceEnum.GEDmatch:
			return [cls.gedmatch_kit_id]
		elif source == SourceEnum.FamilyTreeDNA:
			return [cls.person_name]

		return [cls.id]

	id = 0
	person_name = 1
	source = 2
	total_cm = 3
	largest_segment_cm = 4
	mt_haplogroup = 5
	y_haplogroup = 6
	x_total_cm = 7
	kit_age = 8
	generations = 9
	match_number = 10
	gedmatch_kit_id = 11
	e_mail = 12
	ged_wiki_tree = 13
	sex = 14
	x_largest_segment_cm = 15
	ged_match_source = 16
	snps_overlap = 17
	match_date = 18
	relationship_range = 19
	linked_relationship = 20
	ancestral_surnames = 21
	notes = 22
	matching_bucket = 23


class SegmentFormatEnum(FormatEnum):
	"""This class defines the format of parsed segment data."""

	@classmethod
	def comparison_key(cls, source: SourceEnum = None):
		return [
			cls.segment_id,
			cls.id,
			cls.person_name,
			cls.chromosome_id,
			cls.start,
			cls.end
		]

	segment_id = 0
	id = 1
	person_name = 2
	source = 3
	chromosome_id = 4
	start = 5
	end = 6
	length_cm = 7
	snps = 8
	density = 9


class SharedMatchesFormatEnum(FormatEnum):
	"""This class defines the format of parsed shared matches data."""

	id_1 = 0
	name_1 = 1
	id_2 = 2
	name_2 = 3
	total_cm = 4


class SegmentIntersectionFormatEnum(FormatEnum):
	"""This class defines the format of segment intersection data."""

	id_1 = 0
	id_2 = 1
	segment_1_id = 2
	segment_2_id = 3
	start = 4
	end = 5
	length_snp = 6


class ClusterFormatEnum(FormatEnum):
	"""This class defines the format of clusters data."""

	cluster_id = 0
	id = 1
	person_name = 2


# todo all columns?
# source = 3
# total_cm = 4
# largest_segment_cm = 5
# mt_haplogroup = 6
# y_haplogroup = 7
# x_total_cm = 8
# kit_age = 9
# generations = 10
# match_number = 11
# kit_id = 12
# e_mail = 13
# ged_wiki_tree = 14
# sex = 15
# x_largest_segment_cm = 16
# ged_match_source = 17
# snps_overlap = 18
# match_date = 19
# relationship_range = 20
# linked_relationship = 21
# ancestral_surnames = 22
# notes = 23
# matching_bucket = 24


# endregion


# region Source formats

class InputFormat(StrEnum):
	"""Child classes of this class define formats of input data of this application."""

	@classmethod
	def get_header(cls) -> list:
		"""Returns the header of the given format."""
		return [item for item in cls]

	@classmethod
	def mapping(cls) -> dict:
		"""Represents the mapping between the source format and the corresponding
		final, app defined format."""
		raise NotImplementedError()
		# should not use the abstractmethod decorator, when metaclass is not ABCMeta --> must be overriden or will be error

	@classmethod
	def format_name(cls) -> str:
		"""Returns the name of the source database.
		Is used as a text representation of source identification"""

		return cls.get_source_id().name

	@classmethod
	def validate_format(cls, other_header):
		"""Check if header contains all columns, if not or contains a wrong column, return False.
		If order is different, create a mapping with the right order."""
		# todo implement in child classes and check only if necessary columns are there

		lowercase_nowhitespace_header = ["".join(item.split()).lower() for item in cls]

		if len(other_header) != len(cls):
			return False

		for item in other_header:
			item = "".join(item.split()).lower()

			# todo store wrong column name

			if item not in lowercase_nowhitespace_header:
				return False

		return True

	@classmethod
	def get_mapped_column_name(cls, source_column_name):
		"""Gets the corresponding column name defined by this format."""
		if source_column_name in cls.mapping().keys():
			return cls.mapping()[source_column_name]
		else:
			return None

	@classmethod
	def get_source_id(cls) -> SourceEnum:
		raise NotImplementedError()
		# same as get_header()


# region Match formats

class FTDNAMatchFormat(InputFormat):
	"""Describes the format of matches downloaded from FamilyTreeDNA."""

	@classmethod
	def get_source_id(cls):
		return SourceEnum.FamilyTreeDNA

	@classmethod
	def mapping(cls):
		return {
			cls.match_date: MatchFormatEnum.match_date,
			cls.relationship_range: MatchFormatEnum.relationship_range,
			cls.shared_DNA: MatchFormatEnum.total_cm,
			cls.longest_block: MatchFormatEnum.largest_segment_cm,
			cls.linked_realtionship: MatchFormatEnum.linked_relationship,
			cls.ancestral_surnames: MatchFormatEnum.ancestral_surnames,
			cls.y_hapogroup: MatchFormatEnum.y_haplogroup,
			cls.mt_haplogroup: MatchFormatEnum.mt_haplogroup,
			cls.notes: MatchFormatEnum.notes,
			cls.matching_bucket: MatchFormatEnum.matching_bucket,
			cls.x_match: MatchFormatEnum.x_total_cm
		}

	full_name = 'Full Name'
	first_name = 'First Name'
	middle_name = 'Middle Name'
	last_name = 'Last Name'
	match_date = 'Match Date'
	relationship_range = 'Relationship Range'
	shared_DNA = 'Shared DNA'
	longest_block = 'Longest Block'
	linked_realtionship = 'Linked Relationship'
	ancestral_surnames = 'Ancestral Surnames'
	y_hapogroup = 'Y-DNA Haplogroup'
	mt_haplogroup = 'mtDNA Haplogroup'
	notes = 'Notes'
	matching_bucket = 'Matching Bucket'
	x_match = 'X-Match'


class GEDmatchMatchFormat(InputFormat):
	"""Describes the format of matches downloaded from GEDmatch."""

	@classmethod
	def get_source_id(cls):
		return SourceEnum.GEDmatch

	@classmethod
	def mapping(cls):
		return {
			cls.matched_kit: MatchFormatEnum.gedmatch_kit_id,
			cls.matched_name: MatchFormatEnum.name,
			cls.matched_email: MatchFormatEnum.e_mail,
			cls.largest_segment: MatchFormatEnum.largest_segment_cm,
			cls.total_cm: MatchFormatEnum.total_cm,
			cls.generations: MatchFormatEnum.generations,
			cls.x_largest_segment_cm: MatchFormatEnum.x_largest_segment_cm,
			cls.total_x_cm: MatchFormatEnum.x_total_cm,
			cls.overlap: MatchFormatEnum.snps_overlap,
			cls.created_date: MatchFormatEnum.match_date,
			cls.test_company: MatchFormatEnum.ged_match_source
		}

	primary_kit = "PrimaryKit"
	primary_name = "PrimaryName"
	primary_email = "PrimaryEmail"
	matched_kit = "MatchedKit"
	matched_name = "MatchedName"
	matched_email = "MatchedEmail"
	largest_segment = "LargestSeg"
	total_cm = "TotalCM"
	generations = "Gen"
	x_largest_segment_cm = "LargestXSeg"
	total_x_cm = "TotalXCM"
	overlap = "Overlap"
	created_date = "CreatedDate"
	test_company = "TestCompany"


# endregion

# region Segment formats


class FTDNASegmentFormat(InputFormat):
	"""Describes the format of segments downloaded from FamilyTreeDNA."""

	@classmethod
	def get_source_id(cls):
		return SourceEnum.FamilyTreeDNA

	@classmethod
	def mapping(cls):
		return {
			cls.chromosome: SegmentFormatEnum.chromosome_id,
			cls.start_location: SegmentFormatEnum.start,
			cls.end_location: SegmentFormatEnum.end,
			cls.centimorgans: SegmentFormatEnum.length_cm,
			cls.matching_snps: SegmentFormatEnum.snps
		}

	match_name = 'Match Name'
	chromosome = 'Chromosome'
	start_location = 'Start Location'
	end_location = 'End Location'
	centimorgans = 'Centimorgans'
	matching_snps = 'Matching SNPs'

# endregion
# endregion
