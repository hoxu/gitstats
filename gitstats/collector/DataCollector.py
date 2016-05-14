from collector.StatisticsCollector import *
from collector.StatisticsCollector.StatisticsCollectorStrategy import StatisticsCollectorStrategy
from collector.RefineCollector import GitRefineCollector


class DataCollector(object):
    """Manages data collection from a revision control repository."""
    def __init__(self, data, conf):
        self.data = data
        self.conf = conf

    ##
    # This should be the main function to extract data from the repository.
    def collect(self):
        # collect statistics
        for cls in StatisticsCollectorStrategy.__subclasses__():
            cls(self.data, self.conf).collect()

        GitRefineCollector(self.data, self.conf).collect()
