import argparse
import sys

from genetic_genealogy.project.config_reader import ConfigReader


def __try_to_delete_project(name):
	"""Deletes the project from the global configuration file.
	Does not delete the project directory structure.
	If the current project is to be deleted, user is asked for confirmation."""

	cp = ConfigReader.get_global_configuration()

	if name in cp["PROJECTS"].keys():

		if "current_project" in cp["CURRENT_PROJECT"].keys() and cp["CURRENT_PROJECT"]["current_project"] == name:
			print("Do you want to delete the current project? yes/no")

			for line in sys.stdin:
				if 'yes' == line.rstrip().lower():
					cp["PROJECTS"].pop(name)
					cp["CURRENT_PROJECT"].pop("current_project")

					ConfigReader.write_global_configuration(cp)

					print("Project was successfully deleted from projects.")
					return

				if 'no' == line.rstrip().lower():
					print("Project was not deleted from projects.")
					return

		cp["PROJECTS"].pop(name)
		ConfigReader.write_global_configuration(cp)
		print("Project was successfully deleted from projects.")
		return

	print("Project does not exist, it was not deleted.")


def delete_project(args):
	n = args.name

	__try_to_delete_project(n)


if __name__ == "__main__":
	args_parser = argparse.ArgumentParser()
	args_parser.add_argument("name")

	arguments = args_parser.parse_args()

	delete_project(arguments)
