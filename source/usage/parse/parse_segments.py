from source.parsers.segment_data_parsers import FTDNASegmentParser
import argparse

args_parser = argparse.ArgumentParser()
args_parser.add_argument("source_file")
args_parser.add_argument("-of","--output_file")

me_group = args_parser.add_mutually_exclusive_group(required=True)
me_group.add_argument("--ftdna", action="store_true")
me_group.add_argument("--gedmatch", action="store_true")

args = args_parser.parse_args()

if args.ftdna:
	parser = FTDNASegmentParser()

elif args.gedmatch:
	raise NotImplementedError("Cannot parse GEDmatch segment data yet.")

source_file = args.source_file
output_file = args.output_file

parser.parse(source_file)
parser.save_to_file(output_file)
