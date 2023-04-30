from parsers.match_parsers import MatchParser
import argparse

args_parser = argparse.ArgumentParser()
args_parser.add_argument("source_file")
args_parser.add_argument("output_file")

me_group = args_parser.add_mutually_exclusive_group(required=True)
me_group.add_argument("--ftdna", action="store_true")
me_group.add_argument("--gedmatch", action="store_true")

args = args_parser.parse_args()

if args.ftdna:
	parser = MatchParser("ftdna")

elif args.gedmatch:
	raise Exception("Cannot parse GEDmatch data yet.")

else:
	raise Exception("unknown source")

parser.parse_file(args.source_file)
parser.save_to_file(args.output_file)
