from parsers.shared_matches_parser import SharedMatchesJoinerFTDNA
import argparse

args_parser = argparse.ArgumentParser()

args_parser.add_argument("output_file")
args_parser.add_argument("-d", "--directories", nargs="+")
args_parser.add_argument("-f", "--files", nargs="+")
args_parser.add_argument("-s", "--source", required=True)


args = args_parser.parse_args()

FTDNA_names = ["FamilyTreeDNA", "FTDNA", "ftdna", "ft"]
GEDmatch_names = ["GEDmatch", "GEDMatch", "gedmatch", "ged", "gm"]

source_database = args.source_database

if source_database in FTDNA_names:
	parser = SharedMatchesJoinerFTDNA()

elif source_database in GEDmatch_names:
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
