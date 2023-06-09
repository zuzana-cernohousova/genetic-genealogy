from genetic_genealogy.boxes.segments.intersection_finder import CSVIntersectionFinder
import argparse


def find_segment_intersections(args):
	finder = CSVIntersectionFinder()

	if args.from_database:
		finder.load_segments(from_database=True)

	else:
		finder.load_segments(args.source_file)

	intersections = []

	# check witch usage is requested
	if args.segment_id is not None:
		intersections = finder.find_intersections_of_segment(args.segment_id)
	elif args.person_id is not None:
		intersections = finder.find_intersections_of_person(args.person_id)
	else:
		intersections = finder.find_all_intersections()

	finder.save_intersections(intersections, args.output_file)


if __name__ == "__main__":
	args_parser = argparse.ArgumentParser()

	# add arguments
	args_parser.add_argument("-of", "--output_file")

	i_group_input = args_parser.add_mutually_exclusive_group()
	i_group_input.add_argument("-sf", "--source_file")
	i_group_input.add_argument("-fd", "--from_database", action="store_true")

	group = args_parser.add_mutually_exclusive_group()
	group.add_argument("-sid", "--segment_id", type=int)
	group.add_argument("-id", "--person_id", type=int)

	# parse arguments
	arguments = args_parser.parse_args()

	find_segment_intersections(arguments)
