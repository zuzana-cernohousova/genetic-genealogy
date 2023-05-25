from parsers.match_parsers import FTDNAMatchParser
from parsers.headers import Databases

import argparse

args_parser = argparse.ArgumentParser()
args_parser.add_argument("source_file")
args_parser.add_argument("output_file")

me_group = args_parser.add_mutually_exclusive_group(required=True)
me_group.add_argument("--ftdna", action="store_true")
me_group.add_argument("--gedmatch", action="store_true")

args = args_parser.parse_args()

if args.ftdna:
	parser = FTDNAMatchParser()

elif args.gedmatch:
	raise NotImplementedError("Cannot parse data from GEDMATCH")

parser.parse_file(args.source_file)  # will always be not none, because ftdna or gedmatch is required
parser.save_to_file(args.output_file)
