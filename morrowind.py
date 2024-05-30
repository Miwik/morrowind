import argparse
import logging
import subprocess
import os
import json

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

def load_config(configfile):
    script_path = os.path.dirname(__file__)
    config = load_file_as_json(os.path.join(script_path, configfile))
    if not config:
        return None
    return config

# ---------------------------------------------------------------------------------------------------------------------

def start_morrowind(config):
    logging.info("Starting Morrowind...")
    subprocess.Popen([os.path.join(config["openmw_dir"], "openmw")])
    
# ---------------------------------------------------------------------------------------------------------------------



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
    navmeshtool_parser = subparsers.add_parser("navmeshtool", help="Run navmeshtool.")

    # Commands execution
    args = parser.parse_args()
    if args.command == "start" or args.command is None:
        start_morrowind(config)
    elif args.command == "launcher":
        pass
    elif args.command == "navmeshtool":
        pass
    elif args.command == "save":
        pass
    elif args.command == "restore":
        pass
    else:
        parser.print_help()

# ---------------------------------------------------------------------------------------------------------------------

main()
