import argparse
import logging
import subprocess
import os
import json
import shutil

# ---------------------------------------------------------------------------------------------------------------------

def load_file_as_json(json_file):
    if not json_file:
        return logging.error("Cannot load empty file name")
    try:
        f = open(json_file, 'r')
    except OSError:
        return logging.error("Could not open file %s", json_file)
    with f:
        return json.load(f)

# ---------------------------------------------------------------------------------------------------------------------

def remove_directory(directory_path):
    if os.path.exists(directory_path) and os.path.isdir(directory_path):
        try:
            shutil.rmtree(directory_path)
            logging.info("Directory %s and all its contents have been removed.", directory_path)
        except Exception as e:
            logging.error("An error occurred while removing the directory: %s", e)
    else:
        logging.warning("The directory %s does not exist or is not a directory.", directory_path)

# ---------------------------------------------------------------------------------------------------------------------

def copy_directory(src, dst):
    if os.path.isdir(dst):
        remove_directory(dst)
    try:
        shutil.copytree(src, dst)
        logging.info("Directory %s successfully copied to %s", src, dst)
        return True
    except shutil.Error as e:
        logging.error("Error occurred while copying directory: %s", e)
    except OSError as e:
        logging.error("OS error occurred while copying directory: %s", e)
    return False

# ---------------------------------------------------------------------------------------------------------------------

def load_config(configfile):
    script_path = os.path.dirname(__file__)
    config = load_file_as_json(os.path.join(script_path, configfile))
    if not config:
        return None
    return config

# ---------------------------------------------------------------------------------------------------------------------

def start(config):
    logging.info("Starting Morrowind...")
    subprocess.Popen([os.path.join(config["openmw_dir"], "openmw")])
    
# ---------------------------------------------------------------------------------------------------------------------

def launcher(config):
    logging.info("Running the launcher...")
    subprocess.Popen([os.path.join(config["openmw_dir"], "openmw-launcher")])

# ---------------------------------------------------------------------------------------------------------------------

def navmeshtool(config):
    logging.info("Running navmeshtool...")
    subprocess.Popen([os.path.join(config["openmw_dir"], "openmw-navmeshtool")])

# ---------------------------------------------------------------------------------------------------------------------

def save(config, name):
    logging.info("Saving game directory to %s...", name)
    return copy_directory(config["morrowind_dir"], os.path.join(config["steam_common_dir"], config["morrowind_dir_name"] + " (" + name + ")"))

# ---------------------------------------------------------------------------------------------------------------------

def restore(config, name):
    logging.info("Restoring game directory %s...", name)
    return copy_directory(os.path.join(config["steam_common_dir"], config["morrowind_dir_name"] + " (" + name + ")"), config["morrowind_dir"])

# ---------------------------------------------------------------------------------------------------------------------

def main():
    logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

    # Load config
    config = load_config("config.json")

    # Argument parser
    parser = argparse.ArgumentParser(description="Morrowind utilities.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: start -> default
    start_parser = subparsers.add_parser("start", help="Start the game.")

    # Command: launcher
    launcher_parser = subparsers.add_parser("launcher", help="Run the launcher.")

    # Command: navmeshtool
    navmeshtool_parser = subparsers.add_parser("navmeshtool", help="Run navmeshtool to generate navmeshs.")

    # Command: save
    save_parser = subparsers.add_parser("save", help="Save game directory.")
    save_parser.add_argument("name", help="Name of the save.")

    # Command: restore
    restore_parser = subparsers.add_parser("restore", help="Restore game directory.")
    restore_parser.add_argument("name", help="Name of the save.")

    # Commands execution
    args = parser.parse_args()
    if args.command == "start" or args.command is None:
        start(config)
    elif args.command == "launcher":
        launcher(config)
    elif args.command == "navmeshtool":
        navmeshtool(config)
    elif args.command == "save":
        save(config, args.name)
    elif args.command == "restore":
        restore(config, args.name)
    else:
        parser.print_help()

# ---------------------------------------------------------------------------------------------------------------------

main()
