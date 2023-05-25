from source.boxes.segments.segment_intersections import IntersectionFinder
import argparse

args_parser = argparse.ArgumentParser()

args_parser.add_argument("source_file")
args_parser.add_argument("output_file")

args_parser.add_argument("-id", "--personID", type=int)

args = args_parser.parse_args()

finder = IntersectionFinder()
finder.load_segments(args.source_file)

if args.personID is not None:
	finder.find_intersection(args.personID)

else:
	finder.find_all_intersections()

finder.save_to_file(args.output_file)
