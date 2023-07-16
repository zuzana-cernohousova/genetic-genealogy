from enum import Enum, IntEnum

from genetic_genealogy.helper import lower_no_whitespace


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

	@classmethod
	def validate_format(cls, other_header):
		"""Check if header contains all columns, if not or contains a wrong column, return False.
		If order is different, create a mapping with the right order."""

		# for all necessary columns - lowercase them and get rid of all whitespaces
		lowercase_no_whitespace_minimal_column_set = {lower_no_whitespace(item) for item in
													  cls.get_minimal_column_names_set()}

		# the same for the other header
		lowercase_no_whitespace_other_header_set = {lower_no_whitespace(item) for item in
													other_header}

		# if the minimal column set is a subset of the other header set, it is OK
		if lowercase_no_whitespace_minimal_column_set.issubset(lowercase_no_whitespace_other_header_set):
			# additional columns are not detected and given the implementation
			# of the methods using the formats, it should not be a problem
			return True

		return False

	@classmethod
	def get_minimal_column_names_set(cls):
		"""Returns list of names of necessary columns."""
		return {item.name for item in cls}


class MatchFormatEnum(FormatEnum):
	"""This class defines the format of parsed match data."""

	@classmethod
	def comparison_key(cls, source: SourceEnum = None):
		"""If genetic_genealogy is stated, returns genetic_genealogy specific identification
		(gedmatch_kit_id if GEDmatch or person_name if FTDNA)
		else returns id."""

		if source == SourceEnum.GEDmatch:
			return [cls.gedmatch_kit_id]
		elif source == SourceEnum.FamilyTreeDNA:
			return [cls.person_name]

		return [cls.person_id]

	person_id = 0
	person_name = 1
	source = 2
	total_cm = 3
	largest_segment_cm = 4
	mt_haplogroup = 5
	y_haplogroup = 6
	x_total_cm = 7
	generations = 8
	gedmatch_kit_id = 9
	e_mail = 10
	x_largest_segment_cm = 11
	ged_match_source = 12
	snps_overlap = 13
	match_date = 14
	relationship_range = 15
	linked_relationship = 16
	ancestral_surnames = 17
	notes = 18
	matching_bucket = 19


class SegmentFormatEnum(FormatEnum):
	"""This class defines the format of parsed segment data."""

	@classmethod
	def comparison_key(cls, source: SourceEnum = None):
		return [
			cls.segment_id,
			cls.person_id,
			cls.person_name,
			cls.chromosome_id,
			cls.start,
			cls.end
		]

	segment_id = 0
	person_id = 1
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
	largest_segment = 5
	total_x_cm = 6
	largest_x_segment = 7


class SegmentIntersectionFormatEnum(FormatEnum):
	"""This class defines the format of segment intersection data."""

	person_id_1 = 0
	person_id_2 = 1
	segment_1_id = 2
	segment_2_id = 3
	start = 4
	end = 5
	length_snp = 6


class ClusterFormatEnum(FormatEnum):
	"""This class defines the format of clusters data."""

	cluster_id = 0
	person_id = 1
	person_name = 2


class PrimaryMatchesEnum(FormatEnum):
	person_id = 0
	path = 1

# endregion


# region Source formats

class InputFormatEnum(str, Enum):
	"""Child classes of this class define formats of input data of this application."""

	@classmethod
	def get_header(cls) -> list:
		"""Returns the header of the given format."""
		return [item for item in cls]

	@classmethod
	def mapping(cls) -> dict:
		"""Represents the mapping between the genetic_genealogy format and the corresponding
		final, app defined format."""
		raise NotImplementedError()

	# should not use the abstractmethod decorator, when metaclass is not ABCMeta --> must be overriden or will be error

	@classmethod
	def format_name(cls) -> str:
		"""Returns the name of the genetic_genealogy database.
		Is used as a text representation of genetic_genealogy identification"""

		return cls.get_source_id().name

	@classmethod
	def validate_format(cls, other_header):
		"""Check if header contains all columns, if not or contains a wrong column, return False.
		If order is different, create a mapping with the right order."""

		# for all necessary columns - lowercase them and get rid of all whitespaces
		lowercase_no_whitespace_minimal_column_set = {lower_no_whitespace(item) for item in
													  cls.get_minimal_column_set()}

		# the same for the other header
		lowercase_no_whitespace_other_header_set = {lower_no_whitespace(item) for item in
													other_header}

		# if the minimal column set is a subset of the other header set, it is OK
		if lowercase_no_whitespace_minimal_column_set.issubset(lowercase_no_whitespace_other_header_set):
			# additional columns are not detected and given the implementation
			# of the methods using the formats, it should not be a problem
			return True

		return False

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

	@classmethod
	def get_minimal_column_set(cls) -> set:
		"""Returns a list of all the column identifiers that are defined to be necessary."""
		return {item for item in cls}


# region Match formats

class FTDNAMatchFormatEnum(InputFormatEnum):
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
			cls.linked_relationship: MatchFormatEnum.linked_relationship,
			cls.ancestral_surnames: MatchFormatEnum.ancestral_surnames,
			cls.y_haplogroup: MatchFormatEnum.y_haplogroup,
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
	linked_relationship = 'Linked Relationship'
	ancestral_surnames = 'Ancestral Surnames'
	y_haplogroup = 'Y-DNA Haplogroup'
	mt_haplogroup = 'mtDNA Haplogroup'
	notes = 'Notes'
	matching_bucket = 'Matching Bucket'
	x_match = 'X-Match'

	@classmethod
	def get_minimal_column_set(cls) -> set:
		return {
			cls.first_name, cls.middle_name, cls.last_name,
			cls.shared_DNA, cls.longest_block, cls.x_match
		}


class GEDmatchMatchFormatEnum(InputFormatEnum):
	"""Describes the format of matches downloaded from GEDmatch."""

	@classmethod
	def get_source_id(cls):
		return SourceEnum.GEDmatch

	@classmethod
	def mapping(cls):
		return {
			cls.matched_kit: MatchFormatEnum.gedmatch_kit_id,
			cls.matched_name: MatchFormatEnum.person_name,
			cls.matched_email: MatchFormatEnum.e_mail,
			cls.largest_segment: MatchFormatEnum.largest_segment_cm,
			cls.total_cm: MatchFormatEnum.total_cm,
			cls.generations: MatchFormatEnum.generations,
			cls.largest_x_segment: MatchFormatEnum.x_largest_segment_cm,
			cls.total_x_cm: MatchFormatEnum.x_total_cm,
			cls.overlap: MatchFormatEnum.snps_overlap,
			cls.created_date: MatchFormatEnum.match_date,
			cls.test_company: MatchFormatEnum.ged_match_source
		}

	@classmethod
	def shared_matches_mapping(cls):
		return {
			cls.total_cm: SharedMatchesFormatEnum.total_cm,
			cls.largest_x_segment: SharedMatchesFormatEnum.largest_x_segment,
			cls.total_x_cm: SharedMatchesFormatEnum.total_x_cm,
			cls.largest_segment: SharedMatchesFormatEnum.largest_segment
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
	largest_x_segment = "LargestXSeg"
	total_x_cm = "TotalXCM"
	overlap = "Overlap"
	created_date = "CreatedDate"
	test_company = "TestCompany"

	person_identifier = matched_kit

	@classmethod
	def get_minimal_column_set(cls) -> set:
		return {
			cls.matched_kit, cls.largest_segment, cls.total_cm, cls.largest_x_segment, cls.total_x_cm,
			cls.test_company
		}


# endregion

# region Segment formats

class FTDNASegmentFormatEnum(InputFormatEnum):
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

	person_identifier = match_name

	@classmethod
	def get_minimal_column_set(cls) -> set:
		return {
			cls.match_name, cls.chromosome, cls.start_location, cls.end_location, cls.centimorgans, cls.matching_snps
		}


class ListCSV_GEDmatchSegmentFormatEnum(InputFormatEnum):
	"""Describes the format of segments downloaded from GEDmatch using List/CSV feature."""

	@classmethod
	def get_source_id(cls):
		return SourceEnum.GEDmatch

	@classmethod
	def mapping(cls):
		return {
			cls.chromosome: SegmentFormatEnum.chromosome_id,
			cls.start_location: SegmentFormatEnum.start,
			cls.end_location: SegmentFormatEnum.end,
			cls.centimorgans: SegmentFormatEnum.length_cm,
			cls.matching_snps: SegmentFormatEnum.snps
		}

	primary_kit = "PrimaryKit"
	primary_name = "PrimaryName"
	primary_sex = "Primary Sex"
	primary_email = "PrimaryEmail"
	matched_kit = "MatchedKit"
	chromosome = "chr"
	start_location = "B37Start"
	end_location = "B37End"
	centimorgans = "segment CM"
	matching_snps = "SNPs"
	matched_name = "MatchedName"
	matched_sex = "Matched Sex"
	matched_email = "MatchedEmail"
	total_cm = "Total CM"
	created_date = "CreatedDate"
	y_haplogroup = "Y - Haplogroup"
	mt_haplogroup = "MT - Haplogroup"
	test_company = "TestCompany"

	person_identifier = matched_kit

	@classmethod
	def get_minimal_column_set(cls) -> set:
		return {
			cls.matched_kit, cls.chromosome, cls.start_location, cls.end_location, cls.centimorgans, cls.matching_snps
		}


class SegmentSearch_GEDmatchSegmentFormatEnum(InputFormatEnum):
	"""Describes the format of segments downloaded from GEDmatch using segemnt search feature."""

	@classmethod
	def get_source_id(cls):
		return SourceEnum.GEDmatch

	@classmethod
	def mapping(cls):
		return {
			# person name is not matched to matched name, name will be extracted from database
			cls.chromosome: SegmentFormatEnum.chromosome_id,
			cls.start_location: SegmentFormatEnum.start,
			cls.end_location: SegmentFormatEnum.end,
			cls.centimorgans: SegmentFormatEnum.length_cm,
			cls.matching_snps: SegmentFormatEnum.snps
		}

	primary_kit = "PrimaryKit"
	matched_kit = "MatchedKit"
	chromosome = "chr"
	start_location = "Start"
	end_location = "End"
	centimorgans = "segment cM"
	matching_snps = "SNPs"
	matched_name = "MatchedName"
	matched_sex = "Matched Sex"
	matched_email = "MatchedEmail"

	person_identifier = matched_kit

	@classmethod
	def get_minimal_column_set(cls) -> set:
		return {
			cls.matched_kit, cls.chromosome, cls.start_location, cls.end_location, cls.centimorgans, cls.matching_snps
		}

# endregion
# endregion


# todo for every parsing option, put names of colums into readme
# for both input and output formats
