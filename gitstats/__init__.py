from gitstats.process import run
from gitstats._version import get_versions
__version__ = get_versions()['version']
del get_versions

if __name__ == "__main__":
    run()