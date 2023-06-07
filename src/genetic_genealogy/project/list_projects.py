import argparse
import configparser
import appdirs
import os


def list_projects(args):
	projects_config_path = os.path.join(appdirs.user_config_dir("genetic-genealogy"), "projects.ini")
	cp = configparser.ConfigParser()
	cp.read(projects_config_path)

	if args.long:
		for name in cp["PROJECTS"]:
			print("name= " + name + " path= " + cp["PROJECTS"][name])
	else:
		for name in cp["PROJECTS"]:
			print("name= " + name)


if __name__ == "__main__":
	args_parser = argparse.ArgumentParser()
	args_parser.add_argument("-l", "--long", action="store_true")

	arguments = args_parser.parse_args()

	list_projects(arguments)
