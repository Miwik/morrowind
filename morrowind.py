import argparse
import logging
import subprocess

# ---------------------------------------------------------------------------------------------------------------------

def load_config():
    pass

# ---------------------------------------------------------------------------------------------------------------------

def start_morrowind():


# ---------------------------------------------------------------------------------------------------------------------

def main():
    logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

    # Argument parser
    parser = argparse.ArgumentParser(description="Morrowind utilities.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: start
    start_parser = subparsers.add_parser("start", help="Start the game.")

    # Commands execution
    args = parser.parse_args()
    if args.command == "start":
        logging.info("start")
    else:
        parser.print_help()

# ---------------------------------------------------------------------------------------------------------------------

main()
