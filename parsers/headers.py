from enum import Enum
from abc import ABC, abstractmethod


class Databases(Enum):
	FTDNA = 0
	GEDMATCH = 1


class MatchFormatEnum(Enum):
	id = 0
	name = 1
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


class MatchFormat:
	@property
	def header(self):
		return [
			'ID', 'Name', 'Source', 'Total cM', 'Largest segment cM', 'mt haplogroup', 'Y haplogroup', 'X total cM',
			'Kit age', 'Generations', 'Match number', 'Kit ID', 'E-mail', 'GED WikiTree', 'Sex',
			'X largest segment cM', 'GEDmatch source', 'SNPs overlap', 'Match date', 'Relationship range',
			'Linked relationship', 'Ancestral surnames', 'Notes', 'Matching bucket'
		]

	def get_index(self, column_name):
		return self.header.index(column_name)


class InputFormat(ABC):
	@property
	@abstractmethod
	def header(self):
		"""Represents the header of the given format."""
		pass

	@property
	@abstractmethod
	def __mapping(self):
		"""Represents the mapping between the source format and the final format."""
		pass

	@property
	@abstractmethod
	def format_name(self):
		"""Represents the name of the source database."""
		pass

	def get_mapped_column_name(self, source_column_name):
		if source_column_name in self.__mapping.keys():
			return self.__mapping[source_column_name]
		else:
			return None

	def get_index(self, column_name):
		return self.header.index(column_name)

	def get_column_name(self, index):
		return self.header[index]


class FTDNAMatchFormat(InputFormat):
	@property
	def format_name(self):
		return "FamilyTreeDNA"

	@property
	def __mapping(self):
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


class SegmentFormat:
	@property
	def header(self):
		return ['Segment ID', 'ID', 'Name', 'Source', 'Chromosome ID',
				'Start', 'End', 'Length cM', 'SNPs', 'Density']

	def get_index(self, column_name):
		return self.header.index(column_name)


class FTDNASegmentFormat:

	@property
	def header(self):
		return ['Match Name', 'Chromosome', 'Start Location', 'End Location', 'Centimorgans', 'Matching SNPs']

	__headers_mapping = {
		'Match Name': 'Name',
		'Chromosome': 'Chromosome ID',
		'Start Location': 'Start',
		'End Location': 'End',
		'Centimorgans': 'Length cM',
		'Matching SNPs': 'SNPs'
	}

	def get_index(self, column_name):
		return self.header.index(column_name)

	def get_column_name(self, index):
		return self.header[index]

	def get_mapped_column_name(self, ftdna_column_name):
		if ftdna_column_name in self.__headers_mapping.keys():
			return self.__headers_mapping[ftdna_column_name]
		else:
			return None

	@staticmethod
	def get_format_name():
		return "FamilyTreeDNA"


class GedMatchSegmentFormat:
	def get_index(self, column_name):
		raise NotImplementedError()

	@property
	def header(self):
		raise NotImplementedError()

	def get_column_name(self, index):
		raise NotImplementedError()

	def get_mapped_column_name(self, gedmatch_column_name):
		raise NotImplementedError()

	@staticmethod
	def get_format_name():
		return "GEDMatch"


class SharedMatchesFormat:
	@property
	def header(self):
		return ["ID 1", "Name 1", "ID 2", "Name 2", "Total cM"]

	def get_index(self, column_name):
		return self.header.index(column_name)


class SegmentIntersectionFormat:
	@property
	def header(self):
		return ['ID 1', 'ID 2', 'Segment 1 ID', 'Segment 2 ID', 'Start', 'End', 'Length']

	def get_index(self, column_name):
		return self.header.index(column_name)


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
