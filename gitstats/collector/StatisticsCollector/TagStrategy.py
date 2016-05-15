import datetime
import re

from RunExternal import RunExternal
from collector.StatisticsCollector.StatisticsCollectorStrategy import StatisticsCollectorStrategy


class TagStrategy(StatisticsCollectorStrategy):
    def __init__(self, data, conf):
        super().__init__(data, conf)
        
    def collect(self):
        lines = RunExternal.execute(['git show-ref --tags']).split('\n')
        for line in lines:
            if len(line) == 0:
                continue
            (hash, tag) = line.split(' ')

            tag = tag.replace('refs/tags/', '')
            output = RunExternal.execute(['git log "%s" --pretty=format:"%%at %%aN" -n 1' % hash])
            if len(output) > 0:
                parts = output.split(' ')
                try:
                    stamp = int(parts[0])
                except ValueError:
                    stamp = 0
                self.data.tags[tag] = {'stamp': stamp, 'hash': hash,
                                  'date': datetime.datetime.fromtimestamp(stamp).strftime(self.conf.date_format),
                                  'commits': 0, 'authors': {}}

        # collect info on tags, starting from latest
        tags_sorted_by_date_desc = [el[1] for el in
                                    reversed(sorted([(el[1]['date'], el[0]) for el in list(self.data.tags.items())]))]
        prev = None
        for tag in reversed(tags_sorted_by_date_desc):
            cmd = 'git shortlog -s "%s"' % tag
            if prev != None:
                cmd += ' "^%s"' % prev
            output = RunExternal.execute([cmd])
            if len(output) == 0:
                continue
            prev = tag
            for line in output.split('\n'):
                parts = re.split('\s+', line, 2)
                commits = int(parts[1])
                author = self.get_merged_author(parts[2])
                self.data.tags[tag]['commits'] += commits
                self.data.tags[tag]['authors'][author] = commits