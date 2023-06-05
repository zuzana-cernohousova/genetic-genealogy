from source.parsers.shared_matches_parser import FTDNASharedMatchesParser, GEDmatchSharedMatchesParser
import argparse

args_parser = argparse.ArgumentParser()

# add arguments
args_parser.add_argument("config_file")
args_parser.add_argument("-of","--output_file")
args_parser.add_argument("-v", "--verbose", action="store_true")

me_group = args_parser.add_mutually_exclusive_group(required=True)
me_group.add_argument("--ftdna", action="store_true")
me_group.add_argument("--gedmatch", action="store_true")

# parse arguments
args = args_parser.parse_args()

if args.ftdna:
	parser = FTDNASharedMatchesParser()

elif args.gedmatch:
	parser = GEDmatchSharedMatchesParser()

# parse files behind config_file
parser.parse(args.config_file)
parser.save_to_file(args.output_file)

if args.verbose:
	parser.print_message()
