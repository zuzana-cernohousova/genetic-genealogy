import configparser


class ConfigReader:
	@staticmethod
	def get_match_database_location():
		config = configparser.ConfigParser()
		config.read("settings.ini")

		return config['CSV_LOCATIONS']['match_database']

	@staticmethod
	def get_segment_database_location():
		config = configparser.ConfigParser()
		config.read("settings.ini")

		return config['CSV_LOCATIONS']['segment_database']
