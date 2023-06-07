import argparse
import configparser
import appdirs
import os


def __try_to_checkout_project(name):
	projects_config_path = os.path.join(appdirs.user_config_dir("genetic-genealogy"), "projects.ini")
	cp = configparser.ConfigParser()
	cp.read(projects_config_path)

	if name in cp["PROJECTS"].keys():
		cp["CURRENT_PROJECT"]["current_project"] = name

		with open(projects_config_path, "w") as projects:
			cp.write(projects)

		print("Project checkout was successful. You are now working with the " + name + " project.")
		return

	print(
		"Project does not exist, checkout was unsuccessful. You are still working with the " +
		cp["CURRENT_PROJECT"]["current_project"]
		+ " project.")


def checkout_project(args):
	n = args.name
	__try_to_checkout_project(n)


if __name__ == "__main__":
	args_parser = argparse.ArgumentParser()
	args_parser.add_argument("name")

	arguments = args_parser.parse_args()

	checkout_project(arguments)

# todo add current project command
