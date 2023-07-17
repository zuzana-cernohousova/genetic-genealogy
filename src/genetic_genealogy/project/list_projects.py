import argparse
import configparser
import appdirs
import os


def list_projects(args):
	projects_config_path = os.path.join(appdirs.user_config_dir("genetic-genealogy"), "projects.ini")
	cp = configparser.ConfigParser()
	cp.read(projects_config_path)

	print("Existing projects:")

	if args.long:
		for name in cp["PROJECTS"]:
			print("	name= " + name + " path= " + cp["PROJECTS"][name])
	else:
		for name in cp["PROJECTS"]:
			print("	name= " + name)

	if "current_project" in cp["CURRENT_PROJECT"]:
		print("Current project: " + cp["CURRENT_PROJECT"]["current_project"])
	else:
		print("No current project. To set a project as current, use the 'gengen checkout' command.")


if __name__ == "__main__":
	args_parser = argparse.ArgumentParser()
	args_parser.add_argument("-l", "--long", action="store_true")

	arguments = args_parser.parse_args()

	list_projects(arguments)
