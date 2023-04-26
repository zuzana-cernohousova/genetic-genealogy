class MatchFormat:
	__header = [
		'ID', 'Name', 'Source', 'Total cM', 'Largest segment cM', 'mt haplogroup', 'Y haplogroup', 'X total cM',
		'Kit age', 'Generations', 'Match number', 'Kit ID', 'E-mail', 'GED WikiTree', 'Sex',
		'X largest segment cM', 'GEDmatch source', 'SNPs overlap', 'Match date', 'Relationship range',
		'Linked relationship', 'Ancestral surnames', 'Notes', 'Matching bucket'
	]

	def get_header(self):
		return self.__header

	def get_index(self, column_name):
		return self.__header.index(column_name)


class FTDNAMatchFormat:
	__header = [
		'Full Name', 'First Name', 'Middle Name', 'Last Name', 'Match Date', 'Relationship Range',
		'Shared DNA', 'Longest Block', 'Linked Relationship', 'Ancestral Surnames', 'Y-DNA Haplogroup',
		'mtDNA Haplogroup', 'Notes', 'Matching Bucket', 'X-Match'
	]

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

	def get_header(self):
		return self.__header

	def get_index(self, column_name):
		return self.__header.index(column_name)

	def get_column_name(self, index):
		return self.__header[index]

	def get_mapped_column_name(self, ftdna_column_name):
		if ftdna_column_name in self.__headers_mapping.keys():
			return self.__headers_mapping[ftdna_column_name]
		else:
			return None

	@staticmethod
	def get_format_name(self):
		return "FamilyTreeDNA"


class GEDMatchMatchFormat:
	def get_header(self):
		pass

	def get_index(self, column_name):
		pass

	def get_column_name(self, index):
		pass

	def get_mapped_column_name(self, ftdna_column_name):
		pass

	@staticmethod
	def get_format_name():
		return "GEDMatch"


class SegmentFormat:
	__header = ['Segment ID', 'ID', 'Name', 'Source', 'Chromosome ID',
				'Start', 'End', 'Length cM', 'SNPs', 'Density']

	def get_header(self):
		return self.__header

	def get_index(self, column_name):
		return self.__header.index(column_name)


class FTDNASegmentFormat:
	__header = ['Match Name', 'Chromosome', 'Start Location', 'End Location', 'Centimorgans', 'Matching SNPs']
	__headers_mapping = {
		'Match Name': 'Name',
		'Chromosome': 'Chromosome ID',
		'Start Location': 'Start',
		'End Location': 'End',
		'Centimorgans': 'Length cM',
		'Matching SNPs': 'SNPs'
	}

	def get_header(self):
		return self.__header

	def get_index(self, column_name):
		return self.__header.index(column_name)

	def get_column_name(self, index):
		return self.__header[index]

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
		pass

	def get_header(self):
		pass

	def get_column_name(self, index):
		pass

	def get_mapped_column_name(self, ftdna_column_name):
		pass

	@staticmethod
	def get_format_name():
		return "GEDMatch"


class SharedMatchesFormat:
	__header = ["ID 1", "Name 1", "ID 2", "Name 2", "Total cM"]

	def get_header(self):
		return self.__header

	def get_index(self, column_name):
		return self.__header.index(column_name)


class SegmentIntersectionFormat:
	__header = ['ID 1', 'ID 2', 'Segment 1 ID', 'Segment 2 ID', 'Start', 'End', 'Length']

	def get_header(self):
		return self.__header

	def get_index(self, column_name):
		return self.__header.index(column_name)
