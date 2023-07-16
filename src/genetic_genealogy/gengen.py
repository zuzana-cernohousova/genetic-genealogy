import argparse
import sys
import os

if 'genetic_genealogy' not in sys.modules:
	# if not using installed package
	sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from genetic_genealogy.usage.parse import parse_matches, parse_segments, parse_shared_matches
from genetic_genealogy.usage import find_segment_intersections
from genetic_genealogy.project import checkout_project, create_new_project, delete_project, list_projects, \
	current_project


def main():
	"""This is the main entry point for the application."""
	args_parser = argparse.ArgumentParser()

	subparsers = args_parser.add_subparsers(
		title='subcommands',
		description='valid subcommands',
		required=True)

	# region new-project
	new_project_args = subparsers.add_parser("new-project")
	new_project_args.add_argument("name")
	new_project_args.add_argument("path")
	new_project_args.add_argument("-e", "--existing", action="store_true")
	new_project_args.set_defaults(func=create_new_project.create_new_project)
	# endregion

	# region delete-project
	delete_args = subparsers.add_parser("delete-project")
	delete_args.add_argument("name")
	delete_args.set_defaults(func=delete_project.delete_project)
	# endregion

	# region checkout-project
	checkout_args = subparsers.add_parser("checkout")
	checkout_args.add_argument("name")
	checkout_args.set_defaults(func=checkout_project.checkout_project)
	# endregion

	# region list-projects
	list_args = subparsers.add_parser("list-projects")
	list_args.add_argument("-l", "--long", action="store_true")
	list_args.set_defaults(func=list_projects.list_projects)
	# endregion

	# region current
	current_args = subparsers.add_parser("current-project")
	current_args.add_argument("-l", "--long")
	current_args.set_defaults(func=current_project.current_project)
	# endregion

	# region parse-matches
	p_matches_args = subparsers.add_parser("parse-matches")
	p_matches_args.set_defaults(func=parse_matches.parse_matches)

	p_matches_args.add_argument("-sf", "--source_file")
	p_matches_args.add_argument("-of", "--output_file")
	p_matches_args.add_argument("-v", "--verbose", action="store_true")

	m_me_group = p_matches_args.add_mutually_exclusive_group(required=True)
	m_me_group.add_argument("--ftdna", action="store_true")
	m_me_group.add_argument("--gedmatch", action="store_true")
	# endregion

	# region parse-segments
	p_segments_args = subparsers.add_parser("parse-segments")
	p_segments_args.set_defaults(func=parse_segments.parse_segments)

	p_segments_args.add_argument("-sf", "--source_file")
	p_segments_args.add_argument("-of", "--output_file")
	p_segments_args.add_argument("-v", "--verbose", action="store_true")

	s_me_group = p_segments_args.add_mutually_exclusive_group(required=True)
	s_me_group.add_argument("--ftdna", action="store_true")
	s_me_group.add_argument("-gl", "--gedmatch_list_csv", action="store_true")
	s_me_group.add_argument("-gss", "--gedmatch_segment_search", action="store_true")
	# endregion

	# region parse_shared_matches
	parse_shared_matches_args = subparsers.add_parser("parse-shared")
	parse_shared_matches_args.set_defaults(func=parse_shared_matches.parse_shared_matches)

	parse_shared_matches_args.add_argument("-cf", "--config_file")
	parse_shared_matches_args.add_argument("-of", "--output_file")
	parse_shared_matches_args.add_argument("-v", "--verbose", action="store_true")

	sm_me_group = parse_shared_matches_args.add_mutually_exclusive_group(required=True)
	sm_me_group.add_argument("--ftdna", action="store_true")
	sm_me_group.add_argument("--gedmatch", action="store_true")
	# endregion

	# region intersections
	intersection_args = subparsers.add_parser("find-intersections")
	intersection_args.set_defaults(func=find_segment_intersections.find_segment_intersections)

	intersection_args.add_argument("-of", "--output_file")

	i_group_input = intersection_args.add_mutually_exclusive_group()
	i_group_input.add_argument("-sf", "--source_file")
	i_group_input.add_argument("-fd", "--from_database", action="store_true")

	i_group = intersection_args.add_mutually_exclusive_group()
	i_group.add_argument("-sid", "--segment_id", type=int)
	i_group.add_argument("-pid", "--person_id", type=int)

	# endregion

	# are there enough arguments?
	if len(sys.argv) < 2:
		# if not pring message
		print("""Welcome to the genetic-genealogy project!

To use any of the supported features, use one of the following subcommands:
Use one of the following subcommands:
new-project
delete-project
list-projects
current-project
checkout
parse-matches
parse-segments
parse-shared
find-intersections"""
)
		return

	args = args_parser.parse_args()
	args.func(args)


if __name__ == "__main__":
	main()
