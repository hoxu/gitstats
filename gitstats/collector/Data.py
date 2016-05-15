import datetime
import time


class Data(object):
    def __init__(self):
        self.stamp_created = time.time()
        self.cache = {}

        self.project_name = None

        self.total_authors = 0
        self.activity_by_hour_of_day = {}  # hour -> commits
        self.activity_by_day_of_week = {}  # day -> commits
        self.activity_by_month_of_year = {}  # month [1-12] -> commits
        self.activity_by_hour_of_week = {}  # weekday -> hour -> commits
        self.activity_by_hour_of_day_busiest = 0
        self.activity_by_hour_of_week_busiest = 0
        self.activity_by_year_week = {}  # yy_wNN -> commits
        self.activity_by_year_week_peak = 0

        # name
        # {commits, first_commit_stamp, last_commit_stamp, last_active_day, active_days, lines_added, lines_removed}
        self.authors = {}

        self.total_commits = 0
        self.total_files = 0
        self.authors_by_commits = 0

        # domains
        self.domains = {}  # domain -> commits

        # author of the month
        self.author_of_month = {}  # month -> author -> commits
        self.author_of_year = {}  # year -> author -> commits
        self.commits_by_month = {}  # month -> commits
        self.commits_by_year = {}  # year -> commits
        self.lines_added_by_month = {}  # month -> lines added
        self.lines_added_by_year = {}  # year -> lines added
        self.lines_removed_by_month = {}  # month -> lines removed
        self.lines_removed_by_year = {}  # year -> lines removed
        self.first_commit_stamp = 0
        self.last_commit_stamp = 0
        self.last_active_day = None
        self.active_days = set()

        # lines
        self.total_lines = 0
        self.total_lines_added = 0
        self.total_lines_removed = 0

        # size
        self.total_size = 0

        # timezone
        self.commits_by_timezone = {}  # timezone -> commits

        # tags
        self.tags = {}

        self.files_by_stamp = {}  # stamp -> files

        # extensions
        self.extensions = {}  # extension -> files, lines

        # line statistics
        self.changes_by_date = {}  # stamp -> { files, ins, del }

    ##
    # : get a dictionary of author
    def get_author_info(self, author):
        return self.authors[author]

    def get_activity_by_day_of_week(self):
        return self.activity_by_day_of_week

    def get_activity_by_hour_of_day(self):
        return self.activity_by_hour_of_day

    def get_active_days(self):
        return self.active_days

    def get_domains(self):
        return list(self.domains.keys())

    # : get a dictionary of domains
    def get_domain_info(self, domain):
        return self.domains[domain]

    ##
    # Get a list of authors
    def get_authors(self, limit=None):
        res = self.get_keys_sorted_by_value_key(self.authors, 'commits')
        res.reverse()
        return res[:limit]

    def get_first_commit_date(self):
        return datetime.datetime.fromtimestamp(self.first_commit_stamp)

    def get_last_commit_date(self):
        return datetime.datetime.fromtimestamp(self.last_commit_stamp)

    def get_commit_delta_days(self):
        return (self.last_commit_stamp / 86400 - self.first_commit_stamp / 86400) + 1

    def get_stamp_created(self):
        return self.stamp_created

    def get_tags(self):
        return list(self.tags.keys()).sort()

    def get_total_authors(self):
        return self.total_authors

    def get_total_commits(self):
        return self.total_commits

    def get_total_files(self):
        return self.total_files

    def get_total_loc(self):
        return self.total_lines

    def get_total_size(self):
        return self.total_size

    def get_authors_by_commits(self):
        return self.get_keys_sorted_by_value_key(self.authors, 'commits')

    @staticmethod
    def get_keys_sorted_by_value_key(d, key):
        return [el[1] for el in sorted([(d[el][key], el) for el in list(d.keys())])]

    @staticmethod
    def get_keys_sorted_by_values(d):
        return [el[1] for el in sorted([(el[1], el[0]) for el in list(d.items())])]
