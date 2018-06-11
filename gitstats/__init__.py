from gitstats.git_csv_generator import gen_csv
from gitstats._version import get_versions
__version__ = get_versions()['version']
del get_versions

if __name__ == "__main__":
    gen_csv()