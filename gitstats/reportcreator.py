class ReportCreator:
    """Creates the actual report based on given data."""

    def __init__(self, conf):
        self.conf = conf
        self.data = None
        self.path = None

    def create(self, data, path):
        self.data = data
        self.path = path
