import re
import datetime

from gitstats.RunExternal import RunExternal
from gitstats.collector.StatisticsCollector.StatisticsCollectorStrategy import StatisticsCollectorStrategy


class LineStrategy(StatisticsCollectorStrategy):
    def __init__(self, data, conf):
        super().__init__(data, conf)
        
    def collect(self):
        # outputs:
        #  N files changed, N insertions (+), N deletions(-)
        # <stamp> <author>
        self.data.changes_by_date = {}  # stamp -> { files, ins, del }
        # computation of lines of code by date is better done
        # on a linear history.
        extra = ''
        if self.conf.linear_linestats:
            extra = '--first-parent -m'
        lines = RunExternal.execute(
            ['git log --shortstat %s --pretty=format:"%%at %%aN" %s' % (extra, self.getlogrange('HEAD'))]).split('\n')
        lines.reverse()
        files = 0;
        inserted = 0;
        deleted = 0;
        total_lines = 0
        for line in lines:
            if len(line) == 0:
                continue

            line = str(line)

            # <stamp> <author>
            if re.search('files? changed', line) == None:
                pos = line.find(' ')
                if pos != -1:
                    try:
                        stamp = (int(line[:pos]), line[pos + 1:])[0]
                        self.data.changes_by_date[stamp] = {'files': files, 'ins': inserted, 'del': deleted,
                                                       'lines': total_lines}

                        date = datetime.datetime.fromtimestamp(stamp)
                        yymm = date.strftime('%Y-%m')
                        self.data.lines_added_by_month[yymm] = self.data.lines_added_by_month.get(yymm, 0) + inserted
                        self.data.lines_removed_by_month[yymm] = self.data.lines_removed_by_month.get(yymm, 0) + deleted

                        yy = date.year
                        self.data.lines_added_by_year[yy] = self.data.lines_added_by_year.get(yy, 0) + inserted
                        self.data.lines_removed_by_year[yy] = self.data.lines_removed_by_year.get(yy, 0) + deleted

                        files, inserted, deleted = 0, 0, 0
                    except ValueError:
                        print('Warning: unexpected line "%s"' % line)
                else:
                    print('Warning: unexpected line "%s"' % line)
            else:
                numbers = self.getstatsummarycounts(line)

                if len(numbers) == 3:
                    (files, inserted, deleted) = [int(el) for el in numbers]
                    total_lines += inserted
                    total_lines -= deleted
                    self.data.total_lines_added += inserted
                    self.data.total_lines_removed += deleted

                else:
                    print('Warning: failed to handle line "%s"' % line)
                    (files, inserted, deleted) = (0, 0, 0)
                    # self.data.changes_by_date[stamp] = { 'files': files, 'ins': inserted, 'del': deleted }
        self.data.total_lines += total_lines