#!/usr/bin/env python

import argparse
import subprocess
import os
import sys
import logging
import tarfile
from datetime import datetime


class Keeper:

    def __init__(self, system_directories=None):
        # Refuse to do anything if RunDeck is running
        # This is best practice according to the docs:
        # http://rundeck.org/2.6.11/administration/backup-and-recovery.html
        if self._rundeck_is_running():
            logging.error("rundeckd cannot be running while you take a backup"
                          " or restore from backup")
            raise Exception("rundeckd is still running")

        self.count = 0
        self.bar = None
        # Directories to include in backup and restore
        if system_directories is None:
            # Default is to backup and restore all directories
            self.system_directories = [
                "/var/lib/rundeck/data",          # database
                "/var/lib/rundeck/logs",          # execution logs (biggest)
                "/var/lib/rundeck/.ssh",          # ssh keys
                "/var/lib/rundeck/var/storage",   # keystore files and metadata
                "/var/rundeck/projects"           # project definitions
            ]
        else:
            self.system_directories = system_directories

        # Raise exception if duplicate or
        # overlapping directories are passed in
        if self._has_duplicate_or_overlap(self.system_directories):
            raise Exception("duplicate or overlapping directories detected")

        # Paths must be absolute
        for path in self.system_directories:
            if path[0] != "/":
                # Path is relative
                raise Exception(
                    "relative paths not allowed, please fix {}".format(path)
                )

    def _has_duplicate_or_overlap(self, paths):
        """Return true if list of paths has duplicate or overlapping paths"""
        if len(paths) > 1:
            # TODO: This seems inefficient; see if there's a simpler deduper possible
            first = paths[0]
            remaining = paths[1:]
            for item in remaining:
                if first in item or item in first:
                    logging.error("found conflicting paths {},{}".format(
                        first,
                        item
                    ))
                    return True
            self._has_duplicate_or_overlap(remaining)
        return False

    def _rundeck_is_running(self):
        """Return True if rundeckd is running, False otherwise"""
        try:
            status = subprocess.check_output(
                ["service", "rundeckd", "status"],
                # Universal newlines ensures error.output is a string
                universal_newlines=True
            )
        except subprocess.CalledProcessError as error:
            if "rundeckd" not in error.output:
                raise Exception(
                    "error running service command, "
                    "is rundeckd installed on this machine?"
                )
            else:
                status = error.output
        if "rundeckd" in status and "running" in status:
            return True
        else:
            return False

    def backup(self, destination_path, filename):
        """Create a backup file"""
        # Start message
        logging.debug("starting backup")

        # Fail if backup dir is not found
        if not os.path.exists(destination_path):
            logging.debug("backup directory {} not found; creating now".format(
                destination_path))
            os.makedirs(destination_path)

        file_path = os.path.join(destination_path, filename)
        logging.debug("using full backup path {}".format(file_path))

        # Create tar file and save all directories to it
        with tarfile.open(file_path, mode='w:gz', dereference=True) as archive:
            for directory in self.system_directories:
                logging.info("adding directory {}".format(directory))
                archive.add(directory)
                print("")

        logging.info("backup complete")

    def restore(self, filepath, directories=None):
        """Restore files from a backup tar file"""
        def _check_paths_before_restore(pathlist):
            """Check all files and raise exceptions if any already exists"""
            for path in pathlist:
                full_path = os.path.join("/", path.name)
                if (os.path.isfile(full_path)):
                    logging.error(
                        "no action taken, refusing to restore when"
                        " file already exists on file system: {}".format(
                            full_path
                        )
                    )
                    raise Exception(
                        "refusing to overwrite existing file: {}".format(
                            full_path
                        )
                    )
        logging.info("loading backup file...")
        with tarfile.open(filepath, 'r:gz') as archive:
            all_files = archive.getmembers()
            # All filenames go here
            files_to_restore = []
            for tarinfo in all_files:
                # Check each directory against all files
                for path in self.system_directories:
                    # Remove any '/' from the start of the path
                    if path.startswith('/'):
                        path = path[1:]
                    # Save each individual file for later checking existence
                    if tarinfo.name.startswith(path):
                        files_to_restore.append(tarinfo)
                        logging.debug("path: " + path)
            # Check that files don't already exist before restoring
            logging.info(
                "checking restore paths to avoid overwriting existing files..."
            )
            _check_paths_before_restore(files_to_restore)
            logging.info("restoring files into directories {}".format(
                ",".join(self.system_directories)
            ))

            restore_members = files_to_restore
            logging.debug(
                "restoring files in {}".format(self.system_directories)
            )
            archive.extractall(
                path="/",
                members=restore_members
            )
            logging.info("restore complete: {} files".format(
                len(files_to_restore)
            ))


def main(arguments):
    # Gather arguments
    parser_name = arguments.subparser_name
    debug_mode = arguments.debug

    # Enable debug logging if flag is set
    if debug_mode:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    # Set up logging
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(message)s',
        level=log_level)

    # Set backup directories
    if arguments.dirs:
        system_directories = arguments.dirs[0].split(",")
        if parser_name == "backup":
            # Validate that paths exist
            for directory in system_directories:
                if os.path.exists(directory) or os.access(directory, os.W_OK):
                    pass
                else:
                    raise Exception("directory is not a valid path "
                                    "or not writeable: {}".format(directory))
            logging.warning("overriding default directories with {}".format(
                ",".join(system_directories)
            ))
        # Add "partial" to the name since we are overriding
        partial = "partial-"
    else:
        system_directories = None
        partial = ""

    keeper = Keeper(system_directories=system_directories)

    if parser_name == "backup":
        # Set the name of the backup file to be created
        if arguments.filename:
            backup_filename = arguments.filename
        else:
            backup_filename = "rundeck-backup-" + partial + "{}.tar.gz".format(
                datetime.now().strftime('%Y-%m-%d--%H-%M-%S')
            )
        keeper.backup(
            destination_path=arguments.dest,
            filename=backup_filename)
    elif parser_name == "restore":
        keeper.restore(
            filepath=arguments.file)


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='keeper: helper for backup and restore of RunDeck')
    parser.add_argument(
        '--debug',
        '-d',
        action='store_true',
        help='enable debug logging')
    parser.add_argument(
        '--dirs',
        type=str,
        nargs="*",
        help='comma-separated list that overrides the default list of system'
             'directories to backup/restore')

    subparsers = parser.add_subparsers(help='command help',
                                       dest='subparser_name')

    # Backup options
    backup_parser = subparsers.add_parser('backup', help='create a backup')
    backup_parser.add_argument(
        '--dest',
        type=str,
        required=True,
        help='path to write backup file to')
    backup_parser.add_argument(
        '--filename',
        type=str,
        help='override the filename used the for backup file')

    # Restore options
    restore_parser = subparsers.add_parser(
        'restore',
        help='restore from a backup file')
    restore_parser.add_argument(
        '--file',
        type=str,
        help='path to backup file to restore from')

    return parser.parse_args(args)


if __name__ == "__main__":
    parsed = parse_args(sys.argv[1:])
    main(parsed)
