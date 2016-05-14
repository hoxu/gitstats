import yaml


class Configuration(object):
    def __init__(self):
        self.max_domains = 10
        self.max_ext_length = 10
        self.style = 'gitstats.css'
        self.max_authors = 20
        self.authors_top = 5
        self.commit_begin = ''
        self.commit_end = 'HEAD'
        self.linear_linestats = 1
        self.project_name = ''
        self.processes = 8
        self.start_date = ''
        self.image_resolution = '1280,640'
        self.date_format = '%Y-%m-%d'
        self.authors_merge = {}
        self.gnuplot_cmd = "gnuplot"

    def load(self, filename):
        with open(filename, 'r') as f:
            try:
                conf = yaml.safe_load(f)
                attributes = [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self, a))]
                for attribute in attributes:
                    if attribute in conf.keys():
                        setattr(self, attribute, conf[attribute])
            except yaml.YAMLError as exc:
                print(exc)

    def __str__(self):
        attributes = [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self, a))]
        result = ""
        for attribute in attributes:
            result += "        %s=%s\n" % (attribute, getattr(self, attribute))
        return result
