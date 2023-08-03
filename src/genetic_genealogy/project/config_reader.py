import configparser
import appdirs
import os

from genetic_genealogy.exit_codes import ExitCodes


class ConfigReader:
	"""Class used for parsing configuration from global configuration file (settings.ini)."""

	@staticmethod
	def get_match_database_location():
		current_proj_path = ConfigReader.get_current_project_path()

		project_config = configparser.ConfigParser()
		project_config.read(os.path.join(current_proj_path, "settings.ini"))

		return os.path.join(current_proj_path, project_config['CSV_LOCATIONS']['match_database'])

	@staticmethod
	def get_segment_database_location():
		current_proj_path = ConfigReader.get_current_project_path()

		project_config = configparser.ConfigParser()
		project_config.read(os.path.join(current_proj_path, "settings.ini"))

		return os.path.join(current_proj_path, project_config['CSV_LOCATIONS']['segment_database'])

	@staticmethod
	def get_current_project_path() -> str:
		projects_path = os.path.join(appdirs.user_config_dir("genetic-genealogy"), "projects.ini")

		cp = configparser.ConfigParser()
		cp.read(projects_path)

		if "current_project" in cp["CURRENT_PROJECT"].keys():
			current_project = cp["CURRENT_PROJECT"]["current_project"]
			return cp["PROJECTS"][current_project]
		else:
			print("Current project was not set, please use the 'gengen checkout' command to choose current project.")
			exit(ExitCodes.no_current_project)

	@staticmethod
	def get_global_configuration_path():
		"""Uses appdirs to get the default directory for the "genetic-genealogy" application,
		joins this directory path with "projects.ini" and returns it."""
		return os.path.join(appdirs.user_config_dir("genetic-genealogy"), "projects.ini")

	@staticmethod
	def get_global_configuration():
		"""Reads project configuration from the "project.ini" file
		and returns it in form of an instance of configparser.ConfigParser."""
		projects_config_path = ConfigReader.get_global_configuration_path()
		config_parser = configparser.ConfigParser()

		try:
			config_parser.read(projects_config_path)

		except IOError as err:
			err.add_note("IOError when reading global configuration.")
			raise

		return config_parser

	@staticmethod
	def write_project_configuration_to_file(config_parser, path):
		"""Writes the given config parser to the given path."""
		try:
			with open(path, "w") as settings:
				config_parser.write(settings)
			return True

		except IOError as err:
			err.add_note("IOError when writing to project configuration.")
			raise

	@staticmethod
	def write_global_configuration(config_parser):
		"""Writes the given config parser to the path of the global configuration
		for this application obtained from the get_global_configuration_path method."""
		projects_config_path = ConfigReader.get_global_configuration_path()

		try:
			with open(projects_config_path, "w") as projects:
				config_parser.write(projects)
			return True

		except IOError as err:
			err.add_note("IOError when writing to global configuration.")
			raise
