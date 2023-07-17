import configparser
import os

import appdirs


def get_global_configuration_path():
	return os.path.join(appdirs.user_config_dir("genetic-genealogy"), "projects.ini")


def get_global_configuration():
	"""Reads project configuration from the "project.ini" file
	and returns it in form of an instance of configparser.ConfigParser."""
	projects_config_path = get_global_configuration_path()
	config_parser = configparser.ConfigParser()

	try:
		config_parser.read(projects_config_path)

	except IOError as err:
		err.add_note("IOError when reading global configuration.")
		raise

	return config_parser


def write_project_configuration_to_file(config_parser, path):
	try:
		with open(path, "w") as settings:
			config_parser.write(settings)
		return True

	except IOError as err:
		err.add_note("IOError when writing to project configuration.")
		raise


def write_global_configuration(config_parser):
	projects_config_path = get_global_configuration_path()

	try:
		with open(projects_config_path, "w") as projects:
			config_parser.write(projects)
		return True

	except IOError as err:
		err.add_note("IOError when writing to global configuration.")
		raise
