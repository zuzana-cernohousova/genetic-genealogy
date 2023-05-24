from enum import IntEnum, Enum
from abc import ABC, abstractmethod


class Databases(Enum):
	FTDNA = 0
	GEDMATCH = 1


# region Parent classes


class InputFormat(ABC):
	@property
	@abstractmethod
	def header(self):
		"""Represents the header of the given format."""
		pass

	@property
	@abstractmethod
	def mapping(self):
		"""Represents the mapping between the source format and the final format."""
		pass

	@property
	@abstractmethod
	def format_name(self):
		"""Represents the name of the source database."""
		pass

	def validate_format(self, other_header):
		"""Compares the given header and the header of this format as sets."""
		if set("".join(item.split()).lower() for item in other_header) != set("".join(item.split()).lower() for item in self.header):
			return False
		return True

	def get_mapped_column_name(self, source_column_name):
		"""Gets the corresponding column name defined by this format."""
		if source_column_name in self.mapping.keys():
			return self.mapping[source_column_name]
		else:
			return None

	def get_index(self, column_name):
		"""Gets the index of the column defined by the column name."""
		return self.header.index(column_name)

	def get_column_name(self, index):
		"""Gets the name of the column defined by the index."""
		return self.header[index]


class FormatEnum(IntEnum):
	@classmethod
	def get_header(cls):
		"""Returns the names of all the enum values in a list ordered by their values."""
		return [item.name for item in cls]


# endregion


# region Application formats
# defined by this application


class MatchFormatEnum(FormatEnum):
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
	kit_id = 11
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


# todo remove
class SegmentFormat:
	@property
	def header(self):
		return ['Segment ID', 'ID', 'Name', 'Source', 'Chromosome ID',
				'Start', 'End', 'Length cM', 'SNPs', 'Density']

	def get_index(self, column_name):
		return self.header.index(column_name)


class SegmentFormatEnum(FormatEnum):
	segment_id = 0
	id = 1
	name = 2
	chromosome_id = 3
	start = 4
	end = 5
	length_cm = 6
	snps = 7
	density = 8


# todo remove
class SharedMatchesFormat:
	@property
	def header(self):
		return ["ID 1", "Name 1", "ID 2", "Name 2", "Total cM"]

	def get_index(self, column_name):
		return self.header.index(column_name)


class SharedMatchesFormatEnum(FormatEnum):
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
	cluster_id = 0
	id = 1
	name = 2
	source = 3
	total_cm = 4
	largest_segment_cm = 5
	mt_haplogroup = 6
	y_haplogroup = 7
	x_total_cm = 8
	kit_age = 9
	generations = 10
	match_number = 11
	kit_id = 12
	e_mail = 13
	ged_wiki_tree = 14
	sex = 15
	x_largest_segment_cm = 16
	ged_match_source = 17
	snps_overlap = 18
	match_date = 19
	relationship_range = 20
	linked_relationship = 21
	ancestral_surnames = 22
	notes = 23
	matching_bucket = 24

# endregion


# region Source formats
# region Match formats

class FTDNAMatchFormat(InputFormat):
	"""Describes the format of matches downloaded from FamilyTreeDNA."""
	@property
	def format_name(self):
		return "FamilyTreeDNA"

	@property
	def mapping(self):
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

	@property
	def header(self):
		return [
			'Full Name', 'First Name', 'Middle Name', 'Last Name', 'Match Date', 'Relationship Range',
			'Shared DNA', 'Longest Block', 'Linked Relationship', 'Ancestral Surnames', 'Y-DNA Haplogroup',
			'mtDNA Haplogroup', 'Notes', 'Matching Bucket', 'X-Match'
		]


# endregion

# region Segment formats


class FTDNASegmentFormat(InputFormat):
	"""Describes the format of segments downloaded from FamilyTreeDNA"""
	@property
	def format_name(self):
		return "FamilyTreeDNA"

	@property
	def header(self):
		return ['Match Name', 'Chromosome', 'Start Location', 'End Location', 'Centimorgans', 'Matching SNPs']

	@property
	def mapping(self):
		return {
			'Match Name': SegmentFormatEnum.name,
			'Chromosome': SegmentFormatEnum.chromosome_id,
			'Start Location': SegmentFormatEnum.start,
			'End Location': SegmentFormatEnum.end,
			'Centimorgans': SegmentFormatEnum.length_cm,
			'Matching SNPs': SegmentFormatEnum.snps
		}

# endregion
# endregion
