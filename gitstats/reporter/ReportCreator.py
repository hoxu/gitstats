class ReportCreator(object):
    """Creates the actual report based on given data."""

    def __init__(self, conf, data, path):
        self.conf = conf
        self.version = None
        self.data = data
        self.path = path

    def run(self):
        pass
