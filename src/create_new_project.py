import os
import argparse
import appdirs
import configparser


def __create_project_directory_structure(name, path):
	final_path = os.path.join(path, name)

	try:
		os.mkdir(final_path)

	except FileExistsError:
		print("Project of this path and name already exists.")
		exit(1)

	os.makedirs(os.path.join(final_path, "input_files", "matches", "FTDNA"))
	os.makedirs(os.path.join(final_path, "input_files", "matches", "GEDmatch"))
	os.makedirs(os.path.join(final_path, "input_files", "segments", "FTDNA"))
	os.makedirs(os.path.join(final_path, "input_files", "segments", "GEDmatch"))
	os.makedirs(os.path.join(final_path, "input_files", "shared_matches", "FTDNA"))
	os.makedirs(os.path.join(final_path, "input_files", "shared_matches", "GEDmatch"))

	os.makedirs(os.path.join(final_path, "work_files", "matches"))
	os.makedirs(os.path.join(final_path, "work_files", "segments"))
	os.makedirs(os.path.join(final_path, "work_files", "intersections"))
	os.makedirs(os.path.join(final_path, "work_files", "shared_matches"))


def __create_settings_file(name, path):
	line_list = [line + "\n" for line in [
		"[PROJECT_INFO]",
		"main_path = " + os.path.join(path, name),
		"name = " + name,
		"",
		"[CSV_LOCATIONS]",
		"match_database = " + os.path.join("work_files", "all_matches.csv"),
		"segment_database = " + os.path.join("work_files", "all_segments.csv")
	]]

	with open(os.path.join(path, name, "settings.ini"), "w", encoding="utf-8") as settings:
		settings.writelines(line_list)


def __try_to_add_new_project(name, path):
	config_dir = appdirs.user_config_dir("genetic-genealogy")

	if not os.path.exists(config_dir):
		os.makedirs(config_dir)

	config_file_path = os.path.join(config_dir, "projects.ini")

	project_path = os.path.join(path, name)
	if os.path.exists(project_path):
		raise ValueError("A directory already exists on this path.")

	if os.path.exists(config_file_path):
		cp = configparser.ConfigParser()
		cp.read(config_file_path)

		if name in cp["PROJECTS"]:
			raise ValueError("Project of this name already exists.")

		cp["PROJECTS"][name] = project_path

		with open(os.path.join(config_dir, "projects.ini"), "w", encoding="utf-8") as projects:
			cp.write(projects)

	else:
		with open(os.path.join(config_dir, "projects.ini"), "w", encoding="utf-8") as projects:
			cp = configparser.ConfigParser()

			cp["CURRENT_PROJECT"] = {"current_project": name}
			cp["PROJECTS"] = {name: project_path}

			cp.write(projects)


if __name__ == "__main__":
	args_parser = argparse.ArgumentParser()
	args_parser.add_argument("name")
	args_parser.add_argument("path")
	args = args_parser.parse_args()

	__try_to_add_new_project(args.name, args.path)
	__create_project_directory_structure(args.name, args.path)
	__create_settings_file(args.name, args.path)
