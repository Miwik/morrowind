import argparse
import logging
import subprocess
import os
import json
import shutil
from pathlib import Path

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

def copy_directory(src, dst, overwrite=False):
    if overwrite:
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

def copy_directory_ignore_case_gpt(src, dst):
    if not os.path.isdir(src):
        raise ValueError(f"Source directory '{src}' does not exist or is not a directory")
    
    if not os.path.isdir(dst):
        raise ValueError(f"Destination directory '{dst}' does not exist or is not a directory")
    
    # Build a case-insensitive map of existing files and directories in the destination
    dst_lower_map = {item.lower(): item for item in os.listdir(dst)}
    
    for root, dirs, files in os.walk(src):
        print(f"root: {root}, dirs: {dirs}, files: {files}")

        # Determine the relative path from the source root
        rel_path = os.path.relpath(root, src)
        dst_dir = os.path.join(dst, rel_path)
        
        # Ensure the destination directory exists
        if rel_path != '.':
            dst_dir_lower = dst_dir.lower()
            dst_dir_actual = dst_lower_map.get(dst_dir_lower, dst_dir)
            # os.makedirs(dst_dir_actual, exist_ok=True)
            print(f"Created directory '{dst_dir_actual}'")
        else:
            dst_dir_actual = dst
        
        # Copy subdirectories
        for dir_name in dirs:
            src_subdir = os.path.join(root, dir_name)
            dst_subdir_name_lower = dir_name.lower()
            dst_subdir_name_actual = dst_lower_map.get(dst_subdir_name_lower, dir_name)
            dst_subdir = os.path.join(dst_dir_actual, dst_subdir_name_actual)
            if not os.path.exists(dst_subdir):
                # os.makedirs(dst_subdir)
                print(f"Created directory '{dst_subdir}'")
        
        # Copy files
        for file_name in files:
            src_file = os.path.join(root, file_name)
            dst_file_name_lower = file_name.lower()
            dst_file_name_actual = dst_lower_map.get(dst_file_name_lower, file_name)
            dst_file = os.path.join(dst_dir_actual, dst_file_name_actual)
            # shutil.copy2(src_file, dst_file)
            print(f"Copied '{src_file}' to '{dst_file}'")

# ---------------------------------------------------------------------------------------------------------------------

def list_file_paths(directory):
    if not os.path.isdir(directory):
        logging.error("Directory %s does not exist or is not a directory", directory)
        return []
    return [str(file) for file in Path(directory).rglob('*') if file.is_file()]

# ---------------------------------------------------------------------------------------------------------------------

def copy_directory_ignore_case(src, dst):
    if not os.path.isdir(src):
        logging.error("Source directory %s does not exist or is not a directory", src)
        return
    
    if not os.path.isdir(dst):
        logging.error("Destination directory %s does not exist or is not a directory", dst)
        return

    src_file_paths = list_file_paths(src)
    dst_file_paths = list_file_paths(dst)

# ---------------------------------------------------------------------------------------------------------------------

def list_directories(path):
    try:
        # Create a Path object for the directory
        directory = Path(path)
        # Filter out only directories
        directories = [item.name for item in directory.iterdir() if item.is_dir()]
        return directories
    except Exception as e:
        logging.error("An error occurred: %s", e)
        return []

# ---------------------------------------------------------------------------------------------------------------------

def find_directory(start_path, target_names):
    start_path = Path(start_path)
    for dirpath, dirnames, filenames in os.walk(start_path):
        for dir_name in dirnames:
            if dir_name in target_names:
                return Path(dirpath)
    return None

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
    return copy_directory(config["morrowind_dir"], os.path.join(config["steam_common_dir"], config["morrowind_dir_name"] + " (" + name + ")"), overwrite=True)

# ---------------------------------------------------------------------------------------------------------------------

def restore(config, name):
    logging.info("Restoring game directory %s...", name)
    return copy_directory(os.path.join(config["steam_common_dir"], config["morrowind_dir_name"] + " (" + name + ")"), config["morrowind_dir"], overwrite=True)

# ---------------------------------------------------------------------------------------------------------------------

def install(config, mod):
    logging.info("Installing mod %s...", mod)

    # Check if the mod directory exists
    if not os.path.isdir(mod):
        logging.error("Mod directory %s does not exist.", mod)
        return

    # Get the list of directories in the morrowind data files directory
    mw_data_files_dir_names = list_directories(config["morrowind_data_dir"])
    if not mw_data_files_dir_names:
        logging.error("Could not find any directories in the Morrowind data files directory.")
        return
    print(mw_data_files_dir_names)

    # Go to the mod subdirectory where data files are located
    mod_data_files_dir = find_directory(mod, mw_data_files_dir_names)
    if not mod_data_files_dir:
        logging.error("Could not find the mod data files directory.")
        return
    print(mod_data_files_dir)

    # Copy the mod data files to the Morrowind data files directory
    copy_directory_ignore_case(mod_data_files_dir, config["morrowind_data_dir"])

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

    # Command: install
    install_parser = subparsers.add_parser("install", help="Install mod.")
    install_parser.add_argument("mod", help="Mod to install.")

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
    elif args.command == "install":
        install(config, args.mod)
    else:
        parser.print_help()

# ---------------------------------------------------------------------------------------------------------------------

main()
