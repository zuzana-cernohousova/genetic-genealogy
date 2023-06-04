from source.boxes.segments.intersection_finder import CSVIntersectionFinder
import argparse

args_parser = argparse.ArgumentParser()

# add arguments
args_parser.add_argument("-sf", "--source_file")
args_parser.add_argument("-of", "--output_file")

group = args_parser.add_mutually_exclusive_group()
group.add_argument("-sid", "--segment_id", type=int)
group.add_argument("-id", "--person_id", type=int)

# parse arguments
args = args_parser.parse_args()

finder = CSVIntersectionFinder()
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
