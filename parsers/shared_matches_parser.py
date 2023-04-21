import csv
import os
import re

from parsers.match_parsers import MatchDatabase
from parsers.headers import SharedMatchesFormat, FTDNAMatchFormat


class SharedMatchesJoinerFTDNA:
	__final_format = SharedMatchesFormat()
	__input_format = FTDNAMatchFormat()

	__result = []
	__already_found_pairs = {}

	__files_paths = []
	__ID_not_matched = False

	__matches_database = MatchDatabase()

	def add_file(self, path):
		self.__files_paths.append(path)

	def add_directory(self, directory):
		for f_name in os.listdir(directory):
			f = os.path.join(directory, f_name)

			self.__files_paths.append(f)

	def save_to_file(self, output_filename):
		with open(output_filename, "w", newline='', encoding="utf-8-sig") as output_file:
			writer = csv.writer(output_file)

			for row in self.__result:
				writer.writerow(row)

	def parse_added_files(self):
		for filepath in self.__files_paths:
			filename = os.path.basename(filepath)

			main_person_name = filename.strip(".csv")
			main_person_id = self.__matches_database.get_id_from_match_name(main_person_name)

			with open(filepath, 'r', encoding="utf-8-sig") as file:
				reader = csv.reader(file)

				# get and avoid the header
				_ = self.__get_header(reader)

				for row in reader:
					output_row = [''] * len(self.__final_format.get_header())

					id_1_index = self.__final_format.get_index("ID 1")
					name_1_index = self.__final_format.get_index("Name 1")
					id_2_index = self.__final_format.get_index("ID 2")
					name_2_index = self.__final_format.get_index("Name 2")

					output_row[id_1_index] = main_person_id
					output_row[name_1_index] = main_person_name

					# get new_person_name
					new_person_name = self.__create_name(row)
					output_row[name_2_index] = new_person_name

					# get id from new_person_name
					new_person_id = self.__matches_database.get_id_from_match_name(new_person_name)

					if new_person_id == -1:
						self.__ID_not_matched = True

					output_row[id_2_index] = new_person_id

					# check if they are the same person
					if new_person_id == main_person_id:
						continue  # skip if yes

					# check if this pair was previously found
					if self.__already_found(new_person_id, main_person_id):
						continue  # skip if yes

					# if this pair was not previously found, add it to dict
					self.__add_pair(new_person_id, main_person_id)

					# add to result
					self.__result.append(output_row)

		# get rid of parsed files
		self.__files_paths = []
		self.__print_message()

	def __create_name(self, row):
		name = [
			row[self.__input_format.get_index("First Name")],
			row[self.__input_format.get_index("Middle Name")],
			row[self.__input_format.get_index("Last Name")]
		]
		return re.sub(' +', ' ', " ".join(name))

	def __print_message(self):
		if self.__ID_not_matched:
			print("""AT LEAST ONE id DID NOT MATCH
	please check that all files are current
		if not, please rerun the procedure with current information
		if yes, please curate the files manually
		""")

	def __already_found(self, new_person_id, main_person_id):
		if new_person_id in self.__already_found_pairs.keys():
			if main_person_id in self.__already_found_pairs[new_person_id]:
				# if previously found, don't add again
				return True
		return False

	def __add_pair(self, new_person_id, main_person_id):
		if main_person_id in self.__already_found_pairs.keys():
			self.__already_found_pairs[main_person_id].append(new_person_id)
		else:
			self.__already_found_pairs[main_person_id] = [new_person_id]

	@staticmethod
	def __get_header(reader):
		for row in reader:
			return row

	@staticmethod
	def __get_column_index(header, column_name):
		if column_name in header:
			return header.index(column_name)
		return -1
