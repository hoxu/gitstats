import re

from gitstats.RunExternal import RunExternal
from gitstats.collector.StatisticsCollector.StatisticsCollectorStrategy import StatisticsCollectorStrategy


class AuthorStrategy(StatisticsCollectorStrategy):
    def __init__(self, data, conf):
        super().__init__(data, conf)

    def collect(self):
        # TODO: fix for merged authors
        self.data.total_authors += int(RunExternal.execute(['git shortlog -s %s' % self.get_log_range(), 'wc -l']))
        # self.total_lines = int(getoutput('git-ls-files -z |xargs -0 cat |wc -l'))

        # defined for stamp, author only if author committed at this timestamp.
        self.data.changes_by_date_by_author = {}  # stamp -> author -> lines_added

        # Similar to the above, but never use --first-parent
        # (we need to walk through every commit to know who
        # committed what, not just through mainline)
        lines = RunExternal.execute(
            ['git log --shortstat --date-order --pretty=format:"%%at %%aN" %s' % (self.get_log_range('HEAD'))]).split(
            '\n')
        lines.reverse()
        inserted = 0
        deleted = 0
        stamp = 0
        for line in lines:
            if len(line) == 0:
                continue

            # <stamp> <author>
            if re.search(r'files? changed', line) is None:
                pos = line.find(' ')
                if pos != -1:
                    try:
                        old_stamp = stamp
                        (stamp, author) = (int(line[:pos]), line[pos + 1:])
                        author = self.get_merged_author(author)
                        if old_stamp > stamp:
                            # clock skew, keep old timestamp to avoid having ugly graph
                            stamp = old_stamp
                        if author not in self.data.authors:
                            self.data.authors[author] = {'lines_added': 0, 'lines_removed': 0, 'commits': 0}
                        self.data.authors[author]['commits'] = self.data.authors[author].get('commits', 0) + 1
                        self.data.authors[author]['lines_added'] = self.data.authors[author].get('lines_added',
                                                                                                 0) + inserted
                        self.data.authors[author]['lines_removed'] = self.data.authors[author].get('lines_removed',
                                                                                                   0) + deleted
                        if stamp not in self.data.changes_by_date_by_author:
                            self.data.changes_by_date_by_author[stamp] = {}
                        if author not in self.data.changes_by_date_by_author[stamp]:
                            self.data.changes_by_date_by_author[stamp][author] = {}
                        self.data.changes_by_date_by_author[stamp][author]['lines_added'] = self.data.authors[author][
                            'lines_added']
                        self.data.changes_by_date_by_author[stamp][author]['commits'] = self.data.authors[author][
                            'commits']
                        files, inserted, deleted = 0, 0, 0
                    except ValueError:
                        print('Warning: unexpected line "%s"' % line)
                else:
                    print('Warning: unexpected line "%s"' % line)
            else:
                numbers = self.get_stat_summary_counts(line)

                if len(numbers) == 3:
                    (files, inserted, deleted) = [int(el) for el in numbers]
                else:
                    print('Warning: failed to handle line "%s"' % line)
                    (files, inserted, deleted) = (0, 0, 0)
