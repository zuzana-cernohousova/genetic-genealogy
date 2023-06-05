import argparse
import configparser
import appdirs
import os


def __try_to_delete_project(name):
	projects_config_path = os.path.join(appdirs.user_config_dir("genetic-genealogy"), "projects.ini")
	cp = configparser.ConfigParser()
	cp.read(projects_config_path)

	if name in cp["PROJECTS"].keys():
		cp["PROJECTS"].pop(name)

		with open(projects_config_path, "w") as projects:
			cp.write(projects)

		print("Project was successfully deleted from projects.")
		return

	print("Project does not exist, it was not deleted.")


if __name__ == "__main__":
	args_parser = argparse.ArgumentParser()
	args_parser.add_argument("name")

	args = args_parser.parse_args()

	n = args.name

	__try_to_delete_project(n)
