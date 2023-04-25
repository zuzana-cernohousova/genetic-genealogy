from parsers.segment_data_parsers import FTDNASegmentParser
import argparse

FTDNA_names = ["FamilyTreeDNA", "FTDNA", "ftdna", "ft"]
GEDmatch_names = ["GEDmatch", "GEDMatch", "gedmatch", "ged", "gm"]

args_parser = argparse.ArgumentParser()
args_parser.add_argument("source_file")
args_parser.add_argument("output_file")
args_parser.add_argument("-s", "--source", required=True)

args = args_parser.parse_args()

source = args.source

if source in FTDNA_names:
	parser = FTDNASegmentParser()

elif source in GEDmatch_names:
	raise Exception("Cannot parse GEDmatch segment data yet.")

else:
	raise Exception("unknown source")

source_file = args.source_file
output_file = args.output_file

parser.parse_file(source_file)
parser.save_to_file(output_file)
