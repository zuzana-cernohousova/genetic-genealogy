from source.parsers.shared_matches_parser import FTDNASharedMatchesParser
import argparse

args_parser = argparse.ArgumentParser()

args_parser.add_argument("config_file")  # todo rename parameter
args_parser.add_argument("output_file")

me_group = args_parser.add_mutually_exclusive_group(required=True)
me_group.add_argument("--ftdna", action="store_true")
me_group.add_argument("--gedmatch", action="store_true")

args = args_parser.parse_args()

if args.ftdna:
	parser = FTDNASharedMatchesParser()

elif args.gedmatch:
	raise NotImplementedError("Cannot parse GEDMatch data yet.")

parser.load_primary_matches(args.config_file)

parser.parse_files()
parser.print_message()

parser.save_to_file(args.output_file)
