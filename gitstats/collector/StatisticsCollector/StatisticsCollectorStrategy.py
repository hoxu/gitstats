import re


class StatisticsCollectorStrategy(object):
    def __init__(self, data, conf):
        self.data = data
        self.conf = conf

    def get_merged_author(self, author):
        if author in list(self.conf.authors_merge.keys()):
            return self.conf.authors_merge[author]
        return author

    @staticmethod
    def get_stat_summary_counts(line):
        numbers = []
        numbers += re.findall(r'\d+', line)
        if len(numbers) == 1:
            # neither insertions nor deletions: may probably only happen for "0 files changed"
            numbers.append(0)
            numbers.append(0)
        elif len(numbers) == 2 and line.find('(+)') != -1:
            numbers.append(0)  # only insertions were printed on line
        elif len(numbers) == 2 and line.find('(-)') != -1:
            numbers.insert(1, 0)  # only deletions were printed on line
        return numbers

    def get_commit_range(self, default_range='HEAD', end_only=False):
        if len(self.conf.commit_end) > 0:
            if end_only or len(self.conf.commit_begin) == 0:
                return self.conf.commit_end
            return '%s..%s' % (self.conf.commit_begin, self.conf.commit_end)
        return default_range

    def get_log_range(self, default_range='HEAD', end_only=True):
        commit_range = self.get_commit_range(default_range, end_only)
        if len(self.conf.start_date) > 0:
            return '--since="%s" "%s"' % (self.conf.start_date, commit_range)
        return commit_range

    def collect(self):
        pass
