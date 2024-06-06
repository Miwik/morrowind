import argparse
import logging
import subprocess
import os
import json
import shutil
import fnmatch
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

def list_file_paths(directory):
    if not os.path.isdir(directory):
        logging.error("Directory %s does not exist or is not a directory", directory)
        return []
    return [str(file) for file in Path(directory).rglob('*') if file.is_file()]

# ---------------------------------------------------------------------------------------------------------------------

def copy_directory_ignore_case(src, dst):
    logging.info("src: %s", src)
    logging.info("dst: %s", dst)

    src_file_paths = list_file_paths(src)
    dst_file_paths = list_file_paths(dst)

    # Cut to data files directory to compare only the file paths
    src_file_paths = [file[len(str(src)):] for file in src_file_paths]
    dst_file_paths = [file[len(str(dst)):] for file in dst_file_paths]

    # INFO:File '/Patch for Purists - Semi-Purist Fixes.ESP' already exists in destination directory '/Patch for Purists - Semi-Purist Fixes.ESP'
    # INFO:File '/Patch for Purists.esm' already exists in destination directory '/Patch for Purists.esm'
    # INFO:File '/Patch for Purists - Book Typos.ESP' already exists in destination directory '/Patch for Purists - Book Typos.ESP'
    # INFO:File '/Meshes/xbase_anim.kf' already exists in destination directory '/Meshes/xbase_anim.kf'
    # INFO:File '/Meshes/xbase_anim.kf' already exists in destination directory '/Meshes/xBase_Anim.kf'
    # INFO:File '/Meshes/chimney_smoke_small.nif' already exists in destination directory '/Meshes/Chimney_Smoke_Small.nif'
    # INFO:File '/Meshes/chimney_smoke_small.nif' already exists in destination directory '/Meshes/chimney_smoke_small.nif'
    # INFO:File '/Meshes/xbase_anim_female.kf' already exists in destination directory '/Meshes/xbase_anim_female.kf'
    # INFO:File '/Meshes/xbase_anim_female.kf' already exists in destination directory '/Meshes/xBase_Anim_Female.kf'
    # INFO:File '/Meshes/chimney_smoke02.nif' already exists in destination directory '/Meshes/Chimney_Smoke02.nif'
    # INFO:File '/Meshes/chimney_smoke02.nif' already exists in destination directory '/Meshes/chimney_smoke02.nif'
    # INFO:File '/Meshes/chimney_smoke_green.nif' already exists in destination directory '/Meshes/Chimney_Smoke_Green.nif'
    # INFO:File '/Meshes/chimney_smoke_green.nif' already exists in destination directory '/Meshes/chimney_smoke_green.nif'
    #
    # -> overwrite with the name of the existing destination file, in case of two files with the same name but different case,
    #    choose the file with the most majs in the name and delete the lower case file

    # Look for files with the same name with case insensitive comparison
    for src_file_path in src_file_paths:
        already_exists = []
        for dst_file_path in dst_file_paths:
            if src_file_path.lower() == dst_file_path.lower():
                already_exists.append(dst_file_path)
                # logging.info("File '%s' already exists in destination directory '%s'", src_file_path, dst_file_path)
        if already_exists:
            logging.info("Source file '%s' already exists in destination:", str(src) + src_file_path)
            for dst_file_path in already_exists:
                logging.info("  - '%s'", dst + dst_file_path)

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

def find_directory_or_filename(start_path, target_names):
    start_path = Path(start_path)
    for dirpath, dirnames, filenames in os.walk(start_path):
        for dir_name in dirnames:
            if dir_name in target_names:
                return Path(dirpath)
        for filename in filenames:
            for target_name in target_names:
                if fnmatch.fnmatchcase(filename.lower(), target_name):
                    return Path(dirpath)
    return None

# ---------------------------------------------------------------------------------------------------------------------

def get_data_files_dir_hints(config):
    # Dirs, filenames extensions to look for
    return list_directories(config["morrowind_data_dir"]) + ["*.esm", "*.esp", "*.bsa", "*.omwaddon"]

# ---------------------------------------------------------------------------------------------------------------------

def match_case_insensitive(filename, patterns):
    filename_lower = filename.lower()
    for pattern in patterns:
        if fnmatch.fnmatchcase(filename_lower, pattern):
            return True
    return False

# ---------------------------------------------------------------------------------------------------------------------

def find_mod_data_files_directory(config, path):
    # Get the list of directories in the morrowind data files directory
    mw_data_files_patterns = get_data_files_dir_hints(config)
    if not mw_data_files_patterns:
        logging.error("Could not find any directories in the Morrowind data files directory.")
        return None

    # Find the mod data files directory
    mod_data_files_dir = find_directory_or_filename(path, mw_data_files_patterns)
    if not mod_data_files_dir:
        logging.error("Could not find the mod data files directory.")
        return None
    return mod_data_files_dir

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

    # Go to the mod subdirectory where data files are located
    mod_data_files_dir = find_mod_data_files_directory(config, mod) # find_directory(mod, mw_data_files_dir_names)
    if not mod_data_files_dir:
        logging.error("Could not find the mod data files directory.")
        return
    logging.info("mod data files dir: %s", mod_data_files_dir)

    # Copy the mod data files to the Morrowind data files directory
    copy_directory_ignore_case(mod_data_files_dir, config["morrowind_data_dir"])

# ---------------------------------------------------------------------------------------------------------------------

def main():
    logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

    # Argument parser
    parser = argparse.ArgumentParser(description="Morrowind utilities.")
    parser.add_argument("--config", default="config.json", help="Config file to use, default=config.json")
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

    # Parse arguments & load config
    args = parser.parse_args()
    config = load_config(args.config)
    
    # Commands execution
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
