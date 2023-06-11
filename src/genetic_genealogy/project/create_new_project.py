import os
import argparse
import appdirs
import configparser

from genetic_genealogy.exit_codes import ExitCodes


def __create_project_directory_structure(abs_path):
	if not os.path.exists(abs_path):
		os.mkdir(abs_path)

	for d in ["input_data", "database"]:
		if not os.path.exists(os.path.join(abs_path, d)):
			os.makedirs(os.path.join(abs_path, d))

	# todo create static template file - from there read how the directory structure should look


def __create_settings_file(name, abs_path):
	if os.path.exists(os.path.join(abs_path, "settings.ini")):
		# check that everything is present
		cp = configparser.ConfigParser()
		cp.read(os.path.join(abs_path, "settings.ini"))

		if cp["PROJECT_INFO"] is not None and cp["CSV_LOCATIONS"] is not None:
			ok = True
			for key in ["main_path", "name"]:
				if key not in cp["PROJECT_INFO"]:
					ok = False
			for key in ["match_database", "segment_database"]:
				if key not in cp["CSV_LOCATIONS"]:
					ok = False
			# todo rewrite this validation

			if ok:
				return

	cp = configparser.ConfigParser()
	cp["PROJECT_INFO"] = {}
	cp["PROJECT_INFO"]["main_path"] = abs_path
	cp["PROJECT_INFO"]["name"] = name.lower()

	cp["CSV_LOCATIONS"] = {}
	cp["CSV_LOCATIONS"]["match_database"] = os.path.join("database", "all_matches.csv")
	cp["CSV_LOCATIONS"]["segment_database"] = os.path.join("database", "all_segments.csv")

	with open(os.path.join(abs_path, "settings.ini"), "w", encoding="utf-8") as settings:
		cp.write(settings)


def __create_projects_ini_if_not_exists():
	global_config_dir = appdirs.user_config_dir("genetic-genealogy")

	if not os.path.exists(global_config_dir):
		# if it does not exist, create app specific user_config_dir as gotten form appdirs
		os.makedirs(global_config_dir)

	# get projects.ini file path
	projects_ini_path = os.path.join(global_config_dir, "projects.ini")

	if os.path.exists(projects_ini_path):
		# if the file exists, check its contents
		cp = configparser.ConfigParser()
		cp.read(projects_ini_path)

		if cp["PROJECTS"] is None:
			cp["PROJECTS"] = {}
		if cp["CURRENT_PROJECT"] is None:
			cp["CURRENT_PROJECT"] = {}

		with open(projects_ini_path, 'w') as f:
			cp.write(f)

	else:
		# else create the file and write into it what is necessary
		with open(os.path.join(global_config_dir, "projects.ini"), "w", encoding="utf-8") as projects:
			cp = configparser.ConfigParser()

			cp["CURRENT_PROJECT"] = {}
			cp["PROJECTS"] = {}
			# todo create sittings.ini template, to be recreated, this is stoopid

			cp.write(projects)


def __exists_name(name) -> bool:
	cp = configparser.ConfigParser()
	cp.read(os.path.join(appdirs.user_config_dir("genetic-genealogy"), "projects.ini"))

	if name in cp["PROJECTS"]:
		return True
	return False


def __exists_path(path) -> bool:
	cp = configparser.ConfigParser()
	cp.read(os.path.join(appdirs.user_config_dir("genetic-genealogy"), "projects.ini"))

	if path in cp["PROJECTS"].values():
		return True
	return False


def __add_project(name, path):
	projects_ini_path = os.path.join(appdirs.user_config_dir("genetic-genealogy"), "projects.ini")
	cp = configparser.ConfigParser()
	cp.read(projects_ini_path)

	cp["PROJECTS"][name] = path
	with open(projects_ini_path, "w") as f:
		cp.write(f)


def __try_to_add_new_project_to_projects(name, path, existing=False):
	if not existing and os.path.exists(path):
		print("Choose the -e/--existing option if you want to create a project from existing directory.")
		exit(ExitCodes.unique_required)

	__create_projects_ini_if_not_exists()

	if __exists_name(name):
		print("Choose unique name. This name already exists.")
		exit(ExitCodes.unique_required)

	if __exists_path(path):
		print("Choose unique path. Two projects cannot share path.")
		exit(ExitCodes.unique_required)

	__add_project(name, path)


def create_new_project(args):
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
