from parsers.match_parsers import FTDNAMatchParser
import argparse

args_parser = argparse.ArgumentParser()

args_parser.add_argument("source")
args_parser.add_argument("source_file")
args_parser.add_argument("output_file")

args = args_parser.parse_args()

FTDNA_names = ["FamilyTreeDNA", "FTDNA", "ftdna", "ft"]
GEDmatch_names = ["GEDmatch", "GEDMatch", "gedmatch", "ged", "gm"]

if args.source in FTDNA_names:
	parser = FTDNAMatchParser()

elif args.source in GEDmatch_names:
	raise Exception("Cannot parse GEDmatch data yet.")

else:
	raise Exception("unknown source")

parser.parse_file(args.source_file)
parser.save_to_file(args.output_file)
