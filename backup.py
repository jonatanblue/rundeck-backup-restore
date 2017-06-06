#!/usr/bin/env python

import argparse, subprocess, os, logging
from datetime import datetime

def rundeck_is_running():
    """
    Returns True if rundeckd is running, False otherwise
    """
    try:
        status = subprocess.check_output(["service", "rundeckd", "status"])
    except subprocess.CalledProcessError as error:
        if "rundeckd is not running" not in error.output:
            raise Exception("error running service command")
        else:
            status = error.output
    if "rundeckd is running" in status:
        return True
    else:
        return False

def main(arguments):
    # Gather arguments
    debug_mode = arguments.debug
    destination_path = arguments.dest

    # Enable debug logging if flag is set
    if debug_mode:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    # Set up logging
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',level=log_level)

    # Start message
    logging.debug("starting backup")

    # Refuse to do anything if RunDeck is running
    if rundeck_is_running():
        logging.error("rundeckd cannot be running while you take a backup")
        raise Exception("rundeckd is still running")

    # Create backup directory
    current_time = datetime.now()
    directory_name = "rundeck-backup-" + current_time.strftime("%Y-%M-%d--%H-%m-%S")
    backup_path = os.path.join(destination_path,directory_name)
    logging.debug("using full backup path {}".format(backup_path))
    if not os.path.exists(backup_path):
        logging.debug("creating backup directory {}".format(backup_path))
        os.makedirs(backup_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="rundeck-backup")
    parser.add_argument("--debug",
                        "-d",
                        action='store_true')
    parser.add_argument("--dest",
                        type=str,
                        required=True)
    main(parser.parse_args())
