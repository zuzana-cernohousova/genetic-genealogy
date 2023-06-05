import os
import argparse


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

	os.mkdir(os.path.join(final_path, "work_files"))


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


if __name__ == "__main__":
	args_parser = argparse.ArgumentParser()
	args_parser.add_argument("name")
	args_parser.add_argument("path")
	args = args_parser.parse_args()

	__create_project_directory_structure(args.name, args.path)
	__create_settings_file(args.name, args.path)
