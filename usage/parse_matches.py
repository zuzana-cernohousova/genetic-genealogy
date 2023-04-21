from parsers.match_parsers import FTDNAMatchParser
import sys

FTDNA_names = ["FamilyTreeDNA", "FTDNA", "ftdna", "ft"]
GEDmatch_names = ["GEDmatch", "GEDMatch", "gedmatch", "ged", "gm"]

source = sys.argv[1]

if source in FTDNA_names:
	parser = FTDNAMatchParser()

elif source in GEDmatch_names:
	raise Exception("Cannot parse GEDmatch data yet.")

else:
	raise Exception("unknown source")

source_file = sys.argv[2]
output_file = sys.argv[3]

parser.parse_file(source_file)
parser.save_to_file(output_file)
