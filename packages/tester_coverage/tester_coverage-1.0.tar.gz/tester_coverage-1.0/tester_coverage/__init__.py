"""
Module for incremental coverage files support
"""
import os
import sys
import unittest
from shutil import copyfile
import coverage

is_increment = False  # pylint: disable=invalid-name


def combine(dest_dir=".", data_dir="tests"):
    """
    Combine separate .coverage files to destination file in directory 'dest_dir'
    Process files recursively, starting from directory 'data_dir'
    """
    for root, _subdirs, files in os.walk(data_dir):
        for file_name in files:
            if file_name.startswith(".coverage"):
                src_name = os.path.join(root, file_name)
                dst_name = os.path.join(
                  dest_dir,
                  "{}_{}".format(file_name, '_'.join(root.split(os.path.sep)))
                )
                copyfile(src_name, dst_name)

    cov = coverage.Coverage(data_file=".coverage", config_file=True)
    cov.combine()
    cov.save()


def clean(test_dir):
    """
    Remove .coverage files recursively, starting from directory 'test_dir'
    """
    for root, _dirs, files in os.walk(test_dir):
        for file_name in files:
            if file_name.startswith(".coverage"):
                os.remove(os.path.join(root, file_name))


def clean_coverage_data(dir_name, mask):
    """
    Remove coverage datafiles that match 'mask' from directory 'dir_name'
    """
    try:
        for file_name in os.listdir(dir_name):
            if file_name.startswith(mask):
                full_name = os.path.join(dir_name, file_name)
                if os.path.isfile(full_name):
                    os.remove(full_name)
    except Exception:  # pylint: disable=broad-except
        pass


class TestCoverage(unittest.TestCase):
    """
    Implements incremental coverage files support
    """
    def setUp(self):
        """
        unittest setUp
        """
        self.cov = None
        if not is_increment:
            return

        path, basename = os.path.split(sys.modules[self.__module__].__file__)
        fname, _ext = os.path.splitext(basename)

        self.cov = coverage.Coverage(
          data_file=os.path.join(path, ".coverage.{}_{}".format(fname, self.__class__.__name__))
        )
        self.cov.load()
        self.cov.start()

    def tearDown(self):
        """
        unittest tearDown
        """
        if self.cov:
            self.cov.stop()
            self.cov.save()
