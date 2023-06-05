import configparser
import appdirs
import os


class ConfigReader:
	"""Class used for parsing configuration from global configuration file (settings.ini)."""

	@staticmethod
	def get_match_database_location():
		current_proj_path = ConfigReader.get_current_project_path()

		project_config = configparser.ConfigParser()
		project_config.read(os.path.join(current_proj_path, "settings.ini"))

		return project_config['CSV_LOCATIONS']['match_database']

	@staticmethod
	def get_segment_database_location():
		current_proj_path = ConfigReader.get_current_project_path()

		project_config = configparser.ConfigParser()
		project_config.read(os.path.join(current_proj_path, "settings.ini"))

		return project_config['CSV_LOCATIONS']['segment_database']

	@staticmethod
	def get_current_project_path() -> str:
		projects_path = os.path.join(appdirs.user_config_dir("genetic-genealogy"), "projects.ini")

		cp = configparser.ConfigParser()
		cp.read(projects_path)

		current_project = cp["CURRENT_PROJECT"]["current_project"]
		return cp["PROJECTS"][current_project]
