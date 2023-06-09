from genetic_genealogy.parsers.shared_matches_parser import FTDNASharedMatchesParser, GEDmatchSharedMatchesParser
import argparse


def parse_shared_matches(args):
	if args.ftdna:
		parser = FTDNASharedMatchesParser()

	elif args.gedmatch:
		parser = GEDmatchSharedMatchesParser()

	# parse files behind config_file
	parser.parse(args.config_file)
	parser.save_to_file(args.output_file)

	if args.verbose:
		parser.print_message()


if __name__ == "__main__":
	args_parser = argparse.ArgumentParser()

	# add arguments
	args_parser.add_argument("-cf", "--config_file")
	args_parser.add_argument("-of", "--output_file")
	args_parser.add_argument("-v", "--verbose", action="store_true")

	me_group = args_parser.add_mutually_exclusive_group(required=True)
	me_group.add_argument("--ftdna", action="store_true")
	me_group.add_argument("--gedmatch", action="store_true")

	# parse arguments
	arguments = args_parser.parse_args()

	parse_shared_matches(arguments)
