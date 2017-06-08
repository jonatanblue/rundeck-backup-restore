#!/usr/bin/env python

import unittest, os, zipfile, logging, shutil
from dinghy import Dinghy

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

    def test_instantiating(self):
        """ Test that Dinghy class can be instantiated """
        dinghy = Dinghy(show_progress=True)

    def test_add_directory_to_zip(self):
        """ Test that a directory can be added to a zip file """

        # Set sails
        dinghy = Dinghy(show_progress=False)

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

        # Open zip file
        with zipfile.ZipFile(filepath, 'r', allowZip64=True) as archive:
            file_in_zip = [i for i in archive.namelist()][0]

        expected = textfile_path
        actual = os.path.join("/", file_in_zip)

        # Assert that directory exists in zip file
        self.assertEqual(actual,
                          expected,
                          msg="actual={},expected={}".format(
                            actual,
                            expected))
        # Clean up
        self._purge_directory(workpath)
