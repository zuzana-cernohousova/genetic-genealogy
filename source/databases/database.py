from abc import ABC, abstractmethod


class Database(ABC):
	def __init__(self):
		self._database = []
		self._largest_ID = 0

	@abstractmethod
	def load(self):
		"""Loads the database."""
		pass

	@abstractmethod
	def save(self) -> None:
		"""Saves the database."""
		pass

	@property
	@abstractmethod
	def format(self):
		"""Represents the format of the database."""
		pass

	def get_id(self, parsed_record, source, searched_id_type) -> int | None:
		"""If the parsed_record already exists,
		finds it by linearly going through the database and returns
		the record ID (type of id specified by the searched_id_type
		parameter), else returns None."""
		match_record_id = None

		for old_record in self._database:
			match = True

			# compare all fields except for the id field
			for index in self.format.comparison_key(source=source):
				if index == searched_id_type:
					continue

				if str(old_record[index]) != str(parsed_record[index]):
					match = False
					break

			if match:
				match_record_id = old_record[searched_id_type]
				break

		return match_record_id

	def get_new_id(self) -> int:
		"""Creates a new maximum ID and returns it."""
		self._largest_ID += 1
		return self._largest_ID

	def add_record(self, complete_parsed_record: dict) -> None:
		"""Adds a complete parsed record to the database list."""
		self._database.append(complete_parsed_record)
