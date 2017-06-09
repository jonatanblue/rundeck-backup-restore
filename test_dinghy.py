#!/usr/bin/env python

import unittest
import os
import zipfile
import shutil
from dinghy import Dinghy


class MockedDinghy(Dinghy):
    def __init__(self, *args):
        pass


class TestDinghy(unittest.TestCase):
    """
    Tests for `dinghy.py`
    """

    def _create_dir(self, path):
        """
        Create directory
        """
        if not os.path.exists(path):
            os.makedirs(path)

    def _purge_directory(self, path):
        """
        WARNING: This will recursively delete the directory and all
        subdirectories forever.
        """
        shutil.rmtree(path)

    def _list_files_in_zip(self, path):
        """
        Returns list of all file paths inside a zip file
        """
        with zipfile.ZipFile(path, 'r', allowZip64=True) as archive:
            return [i for i in archive.namelist()]

    def test_instantiating(self):
        """ Test that Dinghy class can be instantiated """
        directories = [
            "/var/lib/rundeck/data",          # database
            "/var/lib/rundeck/logs",          # execution logs (by far biggest)
            "/var/lib/rundeck/.ssh",          # ssh keys
            "/var/lib/rundeck/var/storage",   # key storage files and metadata
            "/var/rundeck/projects"           # project definitions
        ]
        Dinghy(system_directories=directories, show_progress=True)

    def test_has_overlap(self):
        """
        Test that overlap check works
        """
        overlapping_dirs = [
            "/tmp/a/b",
            "/tmp/a"
        ]
        dinghy = MockedDinghy()
        self.assertTrue(dinghy._has_duplicate_or_overlap(overlapping_dirs))

    def test_has_overlap_reverse(self):
        """
        Test that overlap check works
        """
        overlapping_dirs = [
            "/tmp/a",
            "/tmp/a/b"
        ]
        dinghy = MockedDinghy()
        self.assertTrue(dinghy._has_duplicate_or_overlap(overlapping_dirs))

    def test_has_duplicate(self):
        """
        Test that duplicate check works
        """
        duplicate_dirs = [
            "/tmp/a/b",
            "/tmp/a/b"
        ]
        dinghy = MockedDinghy()

        self.assertTrue(dinghy._has_duplicate_or_overlap(duplicate_dirs))

    def test_valid_path_list(self):
        """
        Test that a valid path list is valid according to check
        """
        valid_dirs = [
            "/tmp/a/b/c",
            "/tmp/a/b/d",
            "/tmp/q",
            "/var/troll"
        ]

        dinghy = MockedDinghy()

        self.assertFalse(dinghy._has_duplicate_or_overlap(valid_dirs))

    def test_raises_exception_on_overlapping_dirs(self):
        """
        Test that the dinghy raises exception for duplicate
        or overlapping directories. For example /tmp/a/b/c,/tmp/a/b should fail
        """
        # Set bad directories
        bad_directories = [
            "/tmp/dinghy_python_unittest_raises/a/b/c",
            "/tmp/dinghy_python_unittest_raises/a/b"
        ]
        # Set sails
        with self.assertRaises(Exception):
            Dinghy(system_directories=bad_directories, show_progress=False)

    def test_raises_exception_on_overlapping_dirs_reversed(self):
        """
        Test that the dinghy raises exception for duplicate
        or overlapping directories. For example /tmp/a/b,/tmp/a/b/c should fail
        """
        # Set bad directories
        bad_directories = [
            "/tmp/dinghy_python_unittest_raises/a/b",
            "/tmp/dinghy_python_unittest_raises/a/b/c"
        ]
        # Set sails
        with self.assertRaises(Exception):
            Dinghy(system_directories=bad_directories, show_progress=False)

    def test_add_directory_to_zip(self):
        """ Test that a directory can be added to a zip file """

        # Set sails
        directories = [
            "/var/lib/rundeck/data",          # database
            "/var/lib/rundeck/logs",          # execution logs (by far biggest)
            "/var/lib/rundeck/.ssh",          # ssh keys
            "/var/lib/rundeck/var/storage",   # key storage files and metadata
            "/var/rundeck/projects"           # project definitions
        ]
        dinghy = Dinghy(system_directories=directories, show_progress=False)

        # Set up workspace
        workpath = "/tmp/dinghy_test_add_directory_to_zip"
        self._create_dir(workpath)
        directory_path = os.path.join(workpath, "/testdir1/subdir1")
        self._create_dir(directory_path)
        textfile_path = os.path.join(directory_path, "somefile.txt")
        # Create file
        with open(textfile_path, "w") as textfile:
            textfile.write("lorem ipsum")
        filepath = os.path.join(workpath, "test1.zip")

        # Create zip file
        with zipfile.ZipFile(filepath, 'w', allowZip64=True) as archive:
            # Add directory
            dinghy._add_directory_to_zip(archive, directory_path)

        file_in_zip = self._list_files_in_zip(filepath)[0]

        expected = textfile_path
        actual = os.path.join("/", file_in_zip)

        # Assert that directory exists in zip file
        self.assertEqual(
            actual,
            expected,
            msg="actual={},expected={}".format(
                actual,
                expected))
        # Clean up
        self._purge_directory(workpath)

    def test_backup(self):
        """
        Test creating a backup file from a set of directories
        """

        # Set paths
        file_paths = [
            "/tmp/dinghy_python_unittest_backup/house/room/file1.txt",
            "/tmp/dinghy_python_unittest_backup/house/room/desk/file2.txt",
            "/tmp/dinghy_python_unittest_backup/house/room/desk/file3.txt",
            "/tmp/dinghy_python_unittest_backup/house/room/desk/drawer/file4",
            "/tmp/dinghy_python_unittest_backup/house/room/locker/file5.txt"
        ]
        folder_paths_to_create = [
            "/tmp/dinghy_python_unittest_backup/house/room/desk/drawer/",
            "/tmp/dinghy_python_unittest_backup/house/room/locker"
        ]
        directories_to_backup = [
            "/tmp/dinghy_python_unittest_backup/house/room/desk/drawer/",
            "/tmp/dinghy_python_unittest_backup/house/room/locker/"
        ]
        files_expected_in_zip = [
            "tmp/dinghy_python_unittest_backup/house/room/desk/drawer/file4",
            "tmp/dinghy_python_unittest_backup/house/room/locker/file5.txt"
        ]

        # Set sails
        dinghy = Dinghy(system_directories=directories_to_backup,
                        show_progress=False)

        # Create all directories
        for path in folder_paths_to_create:
            self._create_dir(path)

        # Create all files for backup test
        for path in file_paths:
            # Create file
            with open(path, "w") as file_handle:
                file_handle.write("For Gondor!\n")

        # Create backup
        dinghy.backup(
            destination_path="/tmp/dinghy_python_unittest_backup",
            filename="backup_test.zip"
        )

        # Get list of all file paths inside zip file
        files_in_zip = self._list_files_in_zip(
            "/tmp/dinghy_python_unittest_backup/backup_test.zip")

        # Zip file can't be empty
        self.assertNotEqual(len(files_in_zip), 0)

        # Compare zip file and list of files
        self.assertEqual(files_expected_in_zip,
                         files_in_zip)

        # Recursively remove all directories and files used in test
        self._purge_directory("/tmp/dinghy_python_unittest_backup")

    def test_restore(self):
        """
        Test restoring a set of directories and files from a backup file
        """

        # Set paths
        file_paths = [
            "/tmp/dinghy_python_unittest_restore/hotel/lobby/file1.txt",
            "/tmp/dinghy_python_unittest_restore/hotel/lobby/desk/file2.txt",
            "/tmp/dinghy_python_unittest_restore/hotel/lobby/desk/file3.txt",
            "/tmp/dinghy_python_unittest_restore/hotel/lobby/desk/drawer/f4",
            "/tmp/dinghy_python_unittest_restore/hotel/lobby/locker/file5.txt"
        ]
        folder_paths_to_create = [
            "/tmp/dinghy_python_unittest_restore/hotel/lobby/desk/drawer/",
            "/tmp/dinghy_python_unittest_restore/hotel/lobby/locker"
        ]
        directories_to_backup = [
            "/tmp/dinghy_python_unittest_restore/hotel/lobby/desk/drawer/",
            "/tmp/dinghy_python_unittest_restore/hotel/lobby/locker/"
        ]
        files_expected_in_restore = [
            "/tmp/dinghy_python_unittest_restore/hotel/lobby/desk/drawer/f4",
            "/tmp/dinghy_python_unittest_restore/hotel/lobby/locker/file5.txt"
        ]

        # Set sails
        dinghy = Dinghy(system_directories=directories_to_backup,
                        show_progress=False)

        # Create all directories
        for path in folder_paths_to_create:
            self._create_dir(path)

        # Create all files for backup
        for path in file_paths:
            # Create file
            with open(path, "w") as file_handle:
                file_handle.write("For Gondor!\n")

        # Create backup
        dinghy.backup(
            destination_path="/tmp/dinghy_python_unittest_restore",
            filename="restore_test.zip"
        )

        # Purge the source directory
        self._purge_directory("/tmp/dinghy_python_unittest_restore/hotel")

        # Restore
        dinghy.restore("/tmp/dinghy_python_unittest_restore/restore_test.zip")

        # List all directories
        restored = "/tmp/dinghy_python_unittest_restore/hotel"
        files_found = []
        for root, dirs, files in os.walk(restored):
            for f in files:
                files_found.append(os.path.join(root, f))

        self.assertEqual(files_found, files_expected_in_restore)

    def test_restore_does_not_overwrite(self):
        """
        Test that existing files are not overwritten by restore
        """
        base = "/tmp/dinghy_python_unittest_restore_no_overwrite"
        # Set paths
        file_paths = [
            base + "/hotel/lobby/file1.txt",
            base + "/hotel/lobby/desk/file2.txt",
            base + "/hotel/lobby/desk/file3.txt",
            base + "/hotel/lobby/desk/drawer/f4",
            base + "/hotel/lobby/locker/file5.txt"
        ]
        folder_paths_to_create = [
            base + "/hotel/lobby/desk/drawer/",
            base + "/hotel/lobby/locker"
        ]
        directories_to_backup = [
            base + "/hotel/lobby/desk/drawer/",
            base + "/hotel/lobby/locker/"
        ]
        files_expected_in_restore = [
            base + "/hotel/lobby/desk/drawer/f4",
            base + "/hotel/lobby/locker/file5.txt"
        ]

        # Set sails
        dinghy = Dinghy(system_directories=directories_to_backup,
                        show_progress=False)

        # Create all directories
        for path in folder_paths_to_create:
            self._create_dir(path)

        # Create all files for backup
        for path in file_paths:
            # Create file
            with open(path, "w") as file_handle:
                file_handle.write("For Gondor!\n")

        # Create backup
        dinghy.backup(
            destination_path=base,
            filename="restore_test.zip"
        )

        # Write to files again
        for name in files_expected_in_restore:
            with open(name, "w") as file_handle:
                file_handle.write("new version\n")

        # Restore should raise exception on existing file
        with self.assertRaises(Exception):
            dinghy.restore(base + "/restore_test.zip")

        # Get file contents
        files_content = []
        for name in files_expected_in_restore:
            with open(name, "r") as file_handle:
                content = file_handle.read()
                files_content.append(content)

        self.assertEqual(
            files_content,
            [
                "new version\n",
                "new version\n"
            ]
        )

        # Purge the test directory
        self._purge_directory(base)
