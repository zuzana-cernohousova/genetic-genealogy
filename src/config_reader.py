import configparser


class ConfigReader:
	"""Class used for parsing configuration from global configuration file (settings.ini)."""

	@staticmethod
	def get_match_database_location():
		config = configparser.ConfigParser()
		config.read("settings.ini")
		# todo somehow somewhere store the root of the project, than append the filenames to the path
		return config['CSV_LOCATIONS']['match_database']

	@staticmethod
	def get_segment_database_location():
		config = configparser.ConfigParser()
		config.read("settings.ini")

		return config['CSV_LOCATIONS']['segment_database']
