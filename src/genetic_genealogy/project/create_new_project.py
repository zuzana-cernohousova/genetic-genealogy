import os
import argparse
import appdirs
import configparser

from genetic_genealogy.exit_codes import ExitCodes
from genetic_genealogy.project.project_helper import get_global_configuration, write_global_configuration, \
	get_global_configuration_path, write_project_configuration_to_file


def __create_project_directory_structure(abs_path):
	"""Creates the simple directory structure of the project on the given path."""
	if not os.path.exists(abs_path):
		os.mkdir(abs_path)

	for d in ["input_data", "database"]:
		if not os.path.exists(os.path.join(abs_path, d)):
			os.makedirs(os.path.join(abs_path, d))


def __create_settings_file(name, abs_path):
	"""Creates the project configuration file, adds the project info.
	Configuration file is created based on a template."""
	settings_path = os.path.join(abs_path, "settings.ini")

	cp = configparser.ConfigParser()
	try:
		with open(os.path.join(os.path.dirname(__file__), "templates", "project_config_template.ini")) as template:
			cp.read(template)

	except IOError as err:
		err.add_note("IOError when reading project_config_template.ini")
		raise

	cp["PROJECT_INFO"]["main_path"] = abs_path
	cp["PROJECT_INFO"]["name"] = name.lower()
	cp["CSV_LOCATIONS"]["match_database"] = os.path.join("database", "all_matches.csv")
	cp["CSV_LOCATIONS"]["segment_database"] = os.path.join("database", "all_segments.csv")

	write_project_configuration_to_file(cp, settings_path)


def __create_global_config():
	"""Creates an empty global configuration file, where project list will be added.
	Configuration file is created based on a template."""

	global_config_dir = appdirs.user_config_dir("genetic-genealogy")

	if not os.path.exists(global_config_dir):
		# if it does not exist, create app specific user_config_dir gotten form appdirs
		os.makedirs(global_config_dir)

	cp = configparser.ConfigParser()
	# read the template

	try:
		with open(os.path.join(os.path.dirname(__file__), "templates", "global_config_template.ini")) as template:
			cp.read(template)
	except IOError as err:
		err.add_note("IOError when reading global_config_template.ini")
		raise

	# write the contents of the global configuration file
	write_global_configuration(cp)


def __name_taken(name, cp) -> bool:
	if name in cp["PROJECTS"]:
		return True
	return False


def __path_taken(path, cp) -> bool:
	if path in cp["PROJECTS"].values():
		return True
	return False


def __add_project(name, path, cp):
	cp["PROJECTS"][name] = path
	write_global_configuration(cp)


def __try_to_add_new_project_to_projects(name, path, existing_path=False):
	"""Tries to add new project to the list of existing projects.
	If the name or the path are taken, the project will not be created."""

	if not existing_path and os.path.exists(path):
		print("Choose the -e/--existing option if you want to create a project from an existing directory.")
		exit(ExitCodes.unique_required)

	# if global configuration does not exist, create it
	global_config_path = get_global_configuration_path()
	if not os.path.exists(global_config_path):
		__create_global_config()

	cp = get_global_configuration()
	# if name or path is taken, the project cannot be created
	if __name_taken(name, cp):
		print("Choose unique name. This name already exists.")
		exit(ExitCodes.unique_required)

	if __path_taken(path, cp):
		print("Choose unique path. Two projects cannot share path.")
		exit(ExitCodes.unique_required)

	__add_project(name, path, cp)


def create_new_project(args):
	"""Creates a new project given the arguments."""

	a_p = os.path.abspath(args.path)
	n = args.name

	__try_to_add_new_project_to_projects(n, a_p, args.existing)
	__create_project_directory_structure(a_p)
	__create_settings_file(n, a_p)

	print("Project " + n + " was successfully created.")


if __name__ == "__main__":
	args_parser = argparse.ArgumentParser()
	args_parser.add_argument("name")
	args_parser.add_argument("path")
	args_parser.add_argument("-e", "--existing")
	arguments = args_parser.parse_args()

	create_new_project(arguments)
