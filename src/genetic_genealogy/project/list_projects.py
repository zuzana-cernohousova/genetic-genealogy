import argparse

from genetic_genealogy.project.project_helper import get_global_configuration


def list_projects(args):
	"""Reads the global configuration and prints a list of all existing projects,
	the list contains both name and path of each project.
	Prints the name of the current project."""

	cp = get_global_configuration()

	if "PROJECTS" not in cp:
		print("There are no projects yet. First create some.")
		return

	print("Existing projects:")

	if args.long:
		for name in cp["PROJECTS"]:
			print("	name= " + name + " path= " + cp["PROJECTS"][name])
	else:
		for name in cp["PROJECTS"]:
			print("	name= " + name)

	if "current_project" in cp["CURRENT_PROJECT"]:
		print("Current project: " + cp["CURRENT_PROJECT"]["current_project"])
	else:
		print("No current project. To set a project as current, use the 'gengen checkout' command.")


if __name__ == "__main__":
	args_parser = argparse.ArgumentParser()
	args_parser.add_argument("-l", "--long", action="store_true")

	arguments = args_parser.parse_args()

	list_projects(arguments)
