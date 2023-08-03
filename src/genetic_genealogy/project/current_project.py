import argparse

from genetic_genealogy.project.config_reader import ConfigReader


def current_project(args):
	"""Prints the current project read from the global configuration file."""

	cp = ConfigReader.get_global_configuration()

	if "CURRENT_PROJECT" not in cp:
		print("There are no projects yet. First create some.")
		return

	if "current_project" in cp["CURRENT_PROJECT"]:
		name = cp["CURRENT_PROJECT"]["current_project"]

		if args.long:
			print("Current project: " + name)
			print("path= " + cp["PROJECTS"][name])
		else:
			print("Current project: " + name)

	else:
		print("No current project. To set a project as current, use the 'gengen checkout' command.")


if __name__ == "__main__":
	args_parser = argparse.ArgumentParser()
	args_parser.add_argument("-l", "--long")

	arguments = args_parser.parse_args()

	current_project(arguments)
