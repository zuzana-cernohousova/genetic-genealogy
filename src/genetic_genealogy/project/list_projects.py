import argparse
import configparser
import appdirs
import os

def list_projects():
	args_parser = argparse.ArgumentParser()
	args_parser.add_argument("-p", "--paths", action="store_true")

	args = args_parser.parse_args()

	projects_config_path = os.path.join(appdirs.user_config_dir("genetic-genealogy"), "projects.ini")
	cp = configparser.ConfigParser()
	cp.read(projects_config_path)

	if args.paths:
		for name in cp["PROJECTS"]:
			print("name= " + name + " ,path= " + cp["PROJECTS"][name])
	else:
		for name in cp["PROJECTS"]:
			print("name= " + name)

if __name__ == "__main__":
	list_projects()
