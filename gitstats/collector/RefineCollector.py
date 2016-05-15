import datetime


class GitRefineCollector(object):
    def __init__(self, data, conf):
        self.data = data
        self.conf = conf

    def collect(self):
        # authors
        # name -> {place_by_commits, commits_frac, date_first, date_last, timedelta}
        self.data.authors_by_commits = self.data.get_authors_by_commits()
        self.data.authors_by_commits.reverse()  # most first
        for i, name in enumerate(self.data.authors_by_commits):
            self.data.authors[name]['place_by_commits'] = i + 1

        for name in list(self.data.authors.keys()):
            a = self.data.authors[name]
            a['commits_frac'] = (100 * float(a['commits'])) / self.data.get_total_commits()
            date_first = datetime.datetime.fromtimestamp(a['first_commit_stamp'])
            date_last = datetime.datetime.fromtimestamp(a['last_commit_stamp'])
            delta = date_last - date_first
            a['date_first'] = date_first.strftime(self.conf.date_format)
            a['date_last'] = date_last.strftime(self.conf.date_format)
            a['timedelta'] = delta
            if 'lines_added' not in a:
                a['lines_added'] = 0
            if 'lines_removed' not in a:
                a['lines_removed'] = 0
