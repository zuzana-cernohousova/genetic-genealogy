from source.boxes.filters import Filter, DataContainer
from source.parsers.headers import MatchFormat

import csv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("input_file")
parser.add_argument("output_file")


group = parser.add_mutually_exclusive_group(required=True)

group.add_argument("-cm", "--min_cm")
group.add_argument("-x", "--x_min_cm")
group.add_argument("-l", "--largest_segment_cm")
group.add_argument("-xl", "--x_largest_segment_cm")

group.add_argument("-mt", "--mt_haplogroup", action="store_true")
group.add_argument("-y", "--y_haplogroup", action="store_true")

args = parser.parse_args()

column = ""
query = ""

columns = ["ID", "Name"]

f = Filter(MatchFormat(), columns)
data = DataContainer.load_from_file_to_list(args.input_file)
result = []

if args.mt_haplogroup or args.y_haplogroup:
	if args.mt_haplogroup:
		column = "mt haplogroup"
	elif args.y_haplogroup:
		column = "Y haplogroup"

	columns.append(column)

	result = f.filter_by_not_null(data, column)

else:
	if args.min_cm is not None:
		column = "Total cM"
		query = args.min_cm

	elif args.x_min_cm is not None:
		column = "X total match"
		query = args.x_min_cm

	elif args.largest_segment_cm is not None:
		column = "Largest segment cM"
		query = args.largest_segment_cm

	else:
		column = "X largest segment cM"
		query = args.x_largest_segment_cm

	columns.append(column)

	result = f.filter_by_value_comparison(data, column, query, True)

with open(args.output_file, "w", newline='', encoding="utf-8-sig") as output_file:
	writer = csv.writer(output_file)
	for row in result:
		writer.writerow(row)
