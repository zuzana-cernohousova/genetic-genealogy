import csv
import re

from parsers.match_parsers import CSVMatchDatabase
from parsers.headers import FTDNASegmentFormat, SegmentFormat



class SegmentParser:

	def __init__(self, source_database):

		if source_database not in ["ftdna", "gedmatch"]:
			raise Exception("Unknown format.")

		if source_database == "ftdna":
			self.__input_format = FTDNASegmentFormat()

		self.__final_format = SegmentFormat()

		self.result = [self.__final_format.header]
		self.person_ID_not_matched = False

	def parse_file(self, filename):
		existing_matches = CSVMatchDatabase()
		existing_segments = SegmentDatabase()

		with open(filename, "r", encoding="utf-8-sig") as input_file:
			reader = csv.reader(input_file)
			header = self.__pass_header(reader)

			if header != self.__input_format.header:
				raise Exception("Input file is in incorrect format.")

			for record in reader:
				output_row = [''] * len(self.__final_format.header)

				# add source
				output_row[self.__final_format.get_index("Source")] = self.__input_format.get_format_name()

				# get person name and id from it
				name_column_name = self.__input_format.get_mapped_column_name('Match Name')
				name_index = self.__final_format.get_index(name_column_name)

				name = re.sub(' +', ' ', record[self.__input_format.get_index('Match Name')])
				output_row[name_index] = name

				# extract person id from match name and add it
				person_id = existing_matches.get_id_from_match_name(name)

				if person_id == -1:  # no matching person found
					self.person_ID_not_matched = True
				output_row[self.__final_format.get_index("ID")] = person_id

				# copy all remaining relevant existing information
				for input_index in range(0, len(record)):
					if input_index == self.__input_format.get_index("Match Name"):
						continue  # name already parsed

					item = record[input_index]
					final_column_name = self.__input_format.get_mapped_column_name(self.__input_format.get_column_name(input_index))
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
		for header in reader:
			return header

	def __print_message(self):
		if self.person_ID_not_matched:
			print("""AT LEAST ONE id DID NOT MATCH
	please check that all files are current
		if not, please rerun the procedure with current information
		if yes, please correct the files manually
		""")
