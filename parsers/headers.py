from enum import Enum


class Databases(Enum):
	FTDNA = 0
	GEDMATCH = 1


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


class FTDNAMatchFormat:
	__headers_mapping = {
		'Match Date': 'Match date',
		'Relationship Range': 'Relationship range',
		'Shared DNA': 'Total cM',
		'Longest Block': 'Largest segment cM',
		'Linked Relationship': 'Linked relationship',
		'Ancestral Surnames': 'Ancestral surnames',
		'Y - DNA Haplogroup': 'Y haplogroup',
		'mtDNA Haplogroup': 'mt haplogroup',
		'Notes': 'Notes',
		'Matching Bucket': 'Matching bucket',
		'X - Match': 'X total cM'
	}

	@property
	def header(self):
		return [
			'Full Name', 'First Name', 'Middle Name', 'Last Name', 'Match Date', 'Relationship Range',
			'Shared DNA', 'Longest Block', 'Linked Relationship', 'Ancestral Surnames', 'Y-DNA Haplogroup',
			'mtDNA Haplogroup', 'Notes', 'Matching Bucket', 'X-Match'
		]

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


class GEDMatchMatchFormat:
	@property
	def header(self):
		raise NotImplementedError()

	def get_index(self, column_name):
		raise NotImplementedError()

	def get_column_name(self, index):
		raise NotImplementedError()

	def get_mapped_column_name(self, gedmatch_column_name):
		raise NotImplementedError()

	@staticmethod
	def get_format_name():
		return "GEDMatch"


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
