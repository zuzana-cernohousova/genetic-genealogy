import argparse
import configparser
import appdirs
import os

from genetic_genealogy.project.project_helper import get_global_configuration, write_global_configuration


def __try_to_checkout_project(name):
	"""Tries to change the current project in the projects configuration file."""
	cp = get_global_configuration()

	if name in cp["PROJECTS"].keys():
		cp["CURRENT_PROJECT"]["current_project"] = name

		write_global_configuration(cp)

		print("Project checkout was successful. You are now working with the " + name + " project.")
		return

	print(
		"Project does not exist, checkout was unsuccessful. You are still working with the " +
		cp["CURRENT_PROJECT"]["current_project"]
		+ " project.")


def checkout_project(args):
	n = args.name
	__try_to_checkout_project(n)


if __name__ == "__main__":
	args_parser = argparse.ArgumentParser()
	args_parser.add_argument("name")

	arguments = args_parser.parse_args()

	checkout_project(arguments)

