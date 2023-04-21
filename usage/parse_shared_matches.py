from parsers.shared_matches_parser import SharedMatchesJoinerFTDNA
import sys

FTDNA_names = ["FamilyTreeDNA", "FTDNA", "ftdna", "ft"]
GEDmatch_names = ["GEDmatch", "GEDMatch", "gedmatch", "ged", "gm"]

source = sys.argv[1]

if source in FTDNA_names:
	parser = SharedMatchesJoinerFTDNA()

elif source in GEDmatch_names:
	raise Exception("Sorry, cannot parse GEDmatch data yet.")

else:
	raise Exception("Unknown source in the first argument.")

source_directory = sys.argv[2]
output_file = sys.argv[3]

parser.add_directory(source_directory)
parser.parse_added_files()
parser.save_to_file(output_file)
