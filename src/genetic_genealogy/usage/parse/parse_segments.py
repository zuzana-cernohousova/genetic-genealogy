from genetic_genealogy.parsers.segment_data_parsers import FTDNASegmentParser, ListCSV_GEDmatchSegmentParser, \
	SegmentSearch_GEDmatchSegmentParser
import argparse


def parse_segments(args):
	if args.ftdna:
		parser = FTDNASegmentParser()

	elif args.gedmatch_list_csv:
		parser = ListCSV_GEDmatchSegmentParser()
	elif args.gedmatch_segment_search:
		parser = SegmentSearch_GEDmatchSegmentParser()

	source_file = args.source_file
	output_file = args.output_file

	parser.parse(source_file)
	parser.save_to_file(output_file)

	if args.verbose:
		parser.print_message()


if __name__ == "__main__":
	args_parser = argparse.ArgumentParser()
	# add arguments
	args_parser.add_argument("-sf", "--source_file")
	args_parser.add_argument("-of", "--output_file")
	args_parser.add_argument("-v", "--verbose", action="store_true")

	me_group = args_parser.add_mutually_exclusive_group(required=True)
	me_group.add_argument("--ftdna", action="store_true")
	me_group.add_argument("-gl", "--gedmatch_list_csv", action="store_true")
	me_group.add_argument("-gss", "--gedmatch_segment_search", action="store_true")

	# parse arguments
	arguments = args_parser.parse_args()

	parse_segments(arguments)
