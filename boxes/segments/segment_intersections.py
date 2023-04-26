import csv
from parsers.headers import SegmentIntersectionFormat, SegmentFormat


class intersectionsFinder:
	__segments_by_id = {}
	__segments = []

	__segments_format = SegmentFormat()
	__final_format = SegmentIntersectionFormat()

	__result = []

	@staticmethod
	def __pass_header(reader):
		for _ in reader:
			return

	def load_segments(self, segments_filename):
		with open(segments_filename, 'r', encoding="utf-8-sig") as f:
			reader = csv.reader(f)

			self.__pass_header(reader)

			for row in reader:
				self.__segments.append(row)
				id = int(row[self.__segments_format.get_index('ID')])

				if id in self.__segments_by_id.keys():
					self.__segments_by_id[id].append(row)
				else:
					self.__segments_by_id[id] = [row]

	def find_intersection(self, ID):
		result = [self.__final_format.get_header()]

		if ID in self.__segments_by_id.keys():
			s_segments = self.__segments_by_id[ID]

		else:
			return None

		ch_index = self.__segments_format.get_index('Chromosome ID')
		start_index = self.__segments_format.get_index('Start')
		end_index = self.__segments_format.get_index('End')
		id_index = self.__segments_format.get_index('ID')

		for s in s_segments:
			for r in self.__segments:
				if s[id_index] == r[id_index]:
					continue

				if s[ch_index] != r[ch_index]:
					continue

				intersection = self.__get_intersection((int(s[start_index]), int(s[end_index])),
													   (int(r[start_index]), int(r[end_index])))

				if intersection is None:
					continue

				output_row = self.__fill_output_row(s, r, intersection)
				result.append(output_row)

		self.__result = result
		return result

	def find_all_intersections(self):  # todo only find everything once
		final_result = [self.__final_format.get_header()]
		for ID in self.__segments_by_id.keys():

			res = self.find_intersection(ID)
			if len(res) > 1:
				res = res[1:]
			else:
				res = []

			final_result.extend(res)

		self.__result = final_result

	def save_to_file(self, output_filename):
		with open(output_filename, "w", newline='', encoding="utf-8-sig") as output_file:
			writer = csv.writer(output_file)

			for row in self.__result:
				writer.writerow(row)

	@staticmethod
	def __get_intersection(coords1, coords2):
		coords = [(coords1, coords2), (coords2, coords1)]

		for cs in coords:
			s_s = cs[0][0]
			s_e = cs[0][1]
			r_s = cs[1][0]
			r_e = cs[1][1]

			if s_s <= r_s <= s_e:
				if r_e <= s_e:
					return r_s, r_e
				else:
					return r_s, s_e

			if s_s <= r_e <= s_e:
				return s_s, r_e

		return None

	def __fill_output_row(self, s1, s2, intersection):
		ff = self.__final_format
		sf = self.__segments_format

		row = [''] * len(ff.get_header())

		row[ff.get_index('ID 1')] = s1[sf.get_index('ID')]
		row[ff.get_index('ID 2')] = s2[sf.get_index('ID')]
		row[ff.get_index('Segment 1 ID')] = s1[sf.get_index('Segment ID')]
		row[ff.get_index('Segment 2 ID')] = s2[sf.get_index('Segment ID')]

		row[ff.get_index('Start')] = intersection[0]
		row[ff.get_index('End')] = intersection[1]
		row[ff.get_index('Length')] = intersection[1] - intersection[0] + 1

		return row







