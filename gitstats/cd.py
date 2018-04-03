"""Holds the current working directory context class. A python version of pushd/popd"""
import os

# pylint: disable=too-few-public-methods
class cd: # pylint: disable=invalid-name
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.new_path = os.path.expanduser(newPath)
        self.saved_path = os.getcwd()

    def __enter__(self):
        self.saved_path = os.getcwd()
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.saved_path)
