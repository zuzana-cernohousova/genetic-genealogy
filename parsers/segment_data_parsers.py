import csv
import re

from parsers.match_parsers import MatchDatabase
from parsers.headers import FTDNASegmentFormat, SegmentFormat

class SegmentDatabase:
	__format = SegmentFormat()
	__file_name = "working_files/databases/all_segments.csv"

	def __init__(self):
		self.__database = self.__load_from_file()

	def get_segment_id(self, parsed_segment):
		person_id_index = self.__format.get_index('ID')

		for raw_segment in self.__database:
			if raw_segment[person_id_index] == parsed_segment[person_id_index]:
				if raw_segment[2:] == parsed_segment[2:]:  # all other columns must match
					# todo rewrite so that id does not have to be in the first position
					return raw_segment[self.__format.get_index("Segment ID")]

		# if match not found, segment is new
		return None

	def get_new_segment_id(self):
		self.__biggest_segment_ID += 1
		return self.__biggest_segment_ID

	def add_segment(self, complete_parsed_segment):
		self.__database.append(complete_parsed_segment)

	def __load_from_file(self):
		segments = []

		biggest_id = 0
		segment_id_index = self.__format.get_index("Segment ID")

		with open(self.__file_name, 'r', encoding="utf-8-sig") as input_file:
			reader = csv.reader(input_file)

			# skip header
			for _ in reader:
				break

			for segment in reader:
				record_id = int(segment[segment_id_index])
				if record_id > biggest_id:
					biggest_id = record_id

				segments.append(segment)

		self.__biggest_segment_ID = biggest_id
		return segments

	def save_to_file(self):
		with open(self.__file_name, "w", newline='', encoding="utf-8-sig") as output_file:
			writer = csv.writer(output_file)
			writer.writerow(self.__format.get_header())
			for row in self.__database:
				writer.writerow(row)


class FTDNASegmentParser:
	__final_format = SegmentFormat()
	__ftdna_format = FTDNASegmentFormat()

	result = [__final_format.get_header()]
	person_ID_not_matched = False

	def parse_file(self, filename):
		existing_matches = MatchDatabase()
		existing_segments = SegmentDatabase()

		with open(filename, "r", encoding="utf-8-sig") as input_file:
			reader = csv.reader(input_file)
			self.__pass_header(reader)

			for record in reader:
				output_row = [''] * len(self.__final_format.get_header())

				# add source
				output_row[self.__final_format.get_index("Source")] = "FamilyTreeDNA"

				# get person name and id from it
				name_column_name = self.__ftdna_format.get_mapped_column_name('Match Name')
				name_index = self.__final_format.get_index(name_column_name)

				name = re.sub(' +', ' ', record[self.__ftdna_format.get_index('Match Name')])
				output_row[name_index] = name

				# extract person id from match name and add it
				person_id = existing_matches.get_id_from_match_name(name)

				if person_id == -1:  # no matching person found
					self.person_ID_not_matched = True
				output_row[self.__final_format.get_index("ID")] = person_id

				# copy all remaining relevant existing information
				for ftdna_index in range(0, len(record)):
					if ftdna_index == self.__ftdna_format.get_index("Match Name"):
						continue  # name already parsed

					item = record[ftdna_index]
					final_column_name = self.__ftdna_format.get_mapped_column_name(self.__ftdna_format.get_column_name(ftdna_index))
					if final_column_name is not None:
						new_index = self.__final_format.get_index(final_column_name)
						output_row[new_index] = item

				# get and add segment id
				segment_id = existing_segments.get_segment_id(output_row)
				if segment_id is None:
					segment_id = existing_segments.get_new_segment_id()
					output_row[self.__final_format.get_index("Segment ID")] = segment_id
					existing_segments.add_segment(output_row)
				output_row[self.__final_format.get_index("Segment ID")] = segment_id

				self.result.append(output_row)

		existing_segments.save_to_file()
		self.__print_message()

	def save_to_file(self, output_filename):
		with open(output_filename, "w", newline='', encoding="utf-8-sig") as output_file:
			writer = csv.writer(output_file)

			for row in self.result:
				writer.writerow(row)

	@staticmethod
	def __pass_header(reader):
		for _ in reader:
			return

	def __print_message(self):
		if self.person_ID_not_matched:
			print("""AT LEAST ONE id DID NOT MATCH
	please check that all files are current
		if not, please rerun the procedure with current information
		if yes, please correct the files manually
		""")
