from source.boxes.filters import Filter, DataContainer
from source.parsers.headers import ClusterFormat

import csv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("input_file")
parser.add_argument("output_file")

group = parser.add_mutually_exclusive_group(required=True)

group.add_argument("-id", "--cluster_id")
args = parser.parse_args()

column = ""
query = ""

columns = ["ID", "Name"]

f = Filter(ClusterFormat(), columns)
data = DataContainer.load_from_file_to_list(args.input_file)
result = []

if args.cluster_id is not None:
	column = "Cluster ID"
	query = args.cluster_id

	columns.append(column)

	result = f.filter_by_value_comparison(data, column, query, True)

with open(args.output_file, "w", newline='', encoding="utf-8-sig") as output_file:
	writer = csv.writer(output_file)
	for row in result:
		writer.writerow(row)
