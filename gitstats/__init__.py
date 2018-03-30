from gitstats.gitstats import GitStats
from gitstats._version import get_versions
__version__ = get_versions()['version']
del get_versions

def main():
    g = GitStats()
    g.run()

if __name__ == "__main__":
    main()