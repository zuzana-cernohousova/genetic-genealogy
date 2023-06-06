from src.parsers.match_parsers import FTDNAMatchParser, GEDmatchMatchParser

import argparse


def parse_matches():
	args_parser = argparse.ArgumentParser()
	# add arguments
	args_parser.add_argument("source_file")
	args_parser.add_argument("-of", "--output_file")
	args_parser.add_argument("-v", "--verbose", action="store_true")

	me_group = args_parser.add_mutually_exclusive_group(required=True)
	me_group.add_argument("--ftdna", action="store_true")
	me_group.add_argument("--gedmatch", action="store_true")

	# parse arguments
	args = args_parser.parse_args()

	if args.ftdna:
		parser = FTDNAMatchParser()

	elif args.gedmatch:
		parser = GEDmatchMatchParser()

	# parse matches
	parser.parse(args.source_file)  # will always be not none, because ftdna or gedmatch is required

	# parse
	parser.save_to_file(args.output_file)

	if args.verbose:
		parser.print_message()


if __name__ == "__main__":
	parse_matches()
