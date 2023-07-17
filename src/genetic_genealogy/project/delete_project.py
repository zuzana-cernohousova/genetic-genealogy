import argparse
import configparser
import appdirs
import os
import sys
from genetic_genealogy.project.project_helper import get_global_configuration, write_global_configuration


def __try_to_delete_project(name):
	cp = get_global_configuration()

	if name in cp["PROJECTS"].keys():

		if "current_project" in cp["CURRENT_PROJECT"].keys() and cp["CURRENT_PROJECT"]["current_project"] == name:
			print("Do you want to delete the current project? yes/no")

			for line in sys.stdin:
				if 'yes' == line.rstrip().lower():
					cp["PROJECTS"].pop(name)
					cp["CURRENT_PROJECT"].pop("current_project")

					write_global_configuration(cp)

					print("Project was successfully deleted from projects.")
					return

				if 'no' == line.rstrip().lower():
					print("Project was not deleted from projects.")
					return

		cp["PROJECTS"].pop(name)
		write_global_configuration(cp)
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
