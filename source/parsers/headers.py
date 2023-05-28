from enum import IntEnum, Enum
from abc import ABC, abstractmethod


class SourceEnum(Enum):
	GEDMatch= 0
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

		if source == SourceEnum.GEDMatch:
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
	def comparison_key(cls, source: SourceEnum =None):
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


# todo remove
class SegmentIntersectionFormat:
	@property
	def header(self):
		return ['ID 1', 'ID 2', 'Segment 1 ID', 'Segment 2 ID', 'Start', 'End', 'Length']

	def get_index(self, column_name):
		return self.header.index(column_name)


class SegmentIntersectionFormatEnum(FormatEnum):
	"""This class defines the format of segment intersection data."""

	id_1 = 0
	id_2 = 1
	segment_1_id = 2
	segment_2_id = 3
	start = 4
	end = 5
	length_cm = 6


# todo remove
class ClusterFormat:
	@property
	def header(self):
		return [
			'Cluster ID', 'ID', 'Name', 'Source', 'Total cM', 'Largest segment cM', 'mt haplogroup', 'Y haplogroup',
			'X total cM',
			'Kit age', 'Generations', 'Match number', 'Kit ID', 'E-mail', 'GED WikiTree', 'Sex',
			'X largest segment cM', 'GEDmatch source', 'SNPs overlap', 'Match date', 'Relationship range',
			'Linked relationship', 'Ancestral surnames', 'Notes', 'Matching bucket'
		]

	def get_index(self, column_name):
		return self.header.index(column_name)


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

class InputFormat(ABC):
	"""Child classes of this class define formats of input data of this application."""

	@classmethod
	@abstractmethod
	def header(cls) -> list:
		"""Returns the header of the given format."""
		pass

	@classmethod
	@abstractmethod
	def mapping(cls) -> dict:
		"""Represents the mapping between the source format and the corresponding
		final, app defined format."""
		pass

	@classmethod
	def format_name(cls) -> str:
		"""Returns the name of the source database.
		Is used as a text representation of source identification"""

		return cls.get_source_id().name

	@classmethod
	def validate_format(cls, other_header) -> bool:
		"""Compares the given header and the header of this format as sets.
		Lowers all letters and deletes all whitespace characters."""
		if set("".join(item.split()).lower() for item in other_header) != set(
				"".join(item.split()).lower() for item in cls.header()):
			return False

		# todo if the sets are equal but the order is different, change the order of header
		# now it compares as equal but the order might be wrong and it is not accounted for
		return True

	@classmethod
	def get_mapped_column_name(cls, source_column_name):
		"""Gets the corresponding column name defined by this format."""
		if source_column_name in cls.mapping().keys():
			return cls.mapping()[source_column_name]
		else:
			return None

	@classmethod
	def get_index(cls, column_name):
		"""Gets the index of the column defined by the column name."""
		# todo create room for error or don't?
		return cls.header().index(column_name)

	@classmethod
	def get_column_name(cls, index):
		"""Gets the name of the column defined by the index."""
		return cls.header()[index]

	@classmethod
	@abstractmethod
	def get_source_id(cls) -> SourceEnum:
		pass


# region Match formats

class FTDNAMatchFormat(InputFormat):
	"""Describes the format of matches downloaded from FamilyTreeDNA."""

	@classmethod
	def get_source_id(cls):
		return SourceEnum.FamilyTreeDNA

	@classmethod
	def mapping(cls):
		return {
			'Match Date': MatchFormatEnum.match_date,
			'Relationship Range': MatchFormatEnum.relationship_range,
			'Shared DNA': MatchFormatEnum.total_cm,
			'Longest Block': MatchFormatEnum.largest_segment_cm,
			'Linked Relationship': MatchFormatEnum.linked_relationship,
			'Ancestral Surnames': MatchFormatEnum.ancestral_surnames,
			'Y - DNA Haplogroup': MatchFormatEnum.y_haplogroup,
			'mtDNA Haplogroup': MatchFormatEnum.mt_haplogroup,
			'Notes': MatchFormatEnum.notes,
			'Matching Bucket': MatchFormatEnum.matching_bucket,
			'X - Match': MatchFormatEnum.x_total_cm
		}

	@classmethod
	def header(cls):
		return [
			'Full Name', 'First Name', 'Middle Name', 'Last Name', 'Match Date', 'Relationship Range',
			'Shared DNA', 'Longest Block', 'Linked Relationship', 'Ancestral Surnames', 'Y-DNA Haplogroup',
			'mtDNA Haplogroup', 'Notes', 'Matching Bucket', 'X-Match'
		]


# endregion

# region Segment formats


class FTDNASegmentFormat(InputFormat):
	"""Describes the format of segments downloaded from FamilyTreeDNA."""

	@classmethod
	def get_source_id(cls):
		return SourceEnum.FamilyTreeDNA

	@classmethod
	def header(cls):
		return ['Match Name', 'Chromosome', 'Start Location', 'End Location', 'Centimorgans', 'Matching SNPs']

	@classmethod
	def mapping(cls):
		return {
			'Chromosome': SegmentFormatEnum.chromosome_id,
			'Start Location': SegmentFormatEnum.start,
			'End Location': SegmentFormatEnum.end,
			'Centimorgans': SegmentFormatEnum.length_cm,
			'Matching SNPs': SegmentFormatEnum.snps
		}

# endregion
# endregion
