from source.boxes.filters import Filter, DataContainer
from source.parsers.headers import SegmentFormat

import csv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("input_file")
parser.add_argument("output_file")

group = parser.add_mutually_exclusive_group(required=True)

group.add_argument("-id", "--person_ID")
group.add_argument("-n", "--person_name")

args = parser.parse_args()

column = ""
query = ""
if args.person_ID is not None:
	column = "ID"
	query = args.person_ID
else:
	column = "Name"
	query = args.person_name

f = Filter(SegmentFormat(), SegmentFormat().header)
result = f.filter_by_exact_match(
	DataContainer.load_from_file_to_list(args.input_file),
	column,
	query)

with open(args.output_file, "w", newline='', encoding="utf-8-sig") as output_file:
	writer = csv.writer(output_file)
	for row in result:
		writer.writerow(row)
