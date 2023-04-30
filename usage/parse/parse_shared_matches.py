from parsers.shared_matches_parser import SharedMatchesJoinerFTDNA
import argparse

args_parser = argparse.ArgumentParser()

args_parser.add_argument("output_file")
args_parser.add_argument("-d", "--directories", nargs="+")
args_parser.add_argument("-f", "--files", nargs="+")

me_group = args_parser.add_mutually_exclusive_group(required=True)
me_group.add_argument("--ftdna", action="store_true")
me_group.add_argument("--gedmatch", action="store_true")

args = args_parser.parse_args()

source_database = args.source_database

if args.ftdna:
	parser = SharedMatchesJoinerFTDNA()

elif args.gedmatch:
	raise Exception("Sorry, cannot parse GEDmatch data yet.")

else:
	raise Exception("Unknown source in the first argument.")

source_files = args.files
source_directories = args.directories

if source_files is None and source_directories is None:
	raise Exception("At least one source file or source directory is required.")

output_file = args.output_file

if source_directories is not None:
	for directory in source_directories:
		parser.add_directory(directory)

if source_files is not None:
	for file in source_files:
		parser.add_file(file)

parser.parse_added_files()
parser.save_to_file(output_file)
