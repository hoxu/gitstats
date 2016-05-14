from multiprocessing import Pool

from helper import *
from collector.StatisticsCollector.StatisticsCollectorStrategy import StatisticsCollectorStrategy


class RevisionHistoryStrategy(StatisticsCollectorStrategy):
    def __init__(self, data, conf):
        super().__init__(data, conf)
        
    def getnumoffilesfromrev(self, time_rev):
        """
        Get number of files changed in commit
        """
        time, rev = time_rev
        return (int(time), rev, int(getpipeoutput(['git ls-tree -r --name-only "%s"' % rev, 'wc -l']).split('\n')[0]))


    def collect(self):
        # outputs "<stamp> <files>" for each revision
        revlines = getpipeoutput(
            ['git rev-list --pretty=format:"%%at %%T" %s' % self.getlogrange('HEAD'),
             'grep -v ^commit']).strip().split(
            '\n')
        lines = []
        revs_to_read = []
        # Look up rev in cache and take info from cache if found
        # If not append rev to list of rev to read from repo
        for revline in revlines:
            time, rev = revline.split(' ')
            # if cache empty then add time and rev to list of new rev's
            # otherwise try to read needed info from cache
            if 'files_in_tree' not in list(self.data.cache.keys()):
                revs_to_read.append((time, rev))
                continue
            if rev in list(self.data.cache['files_in_tree'].keys()):
                lines.append('%d %d' % (int(time), self.data.cache['files_in_tree'][rev]))
            else:
                revs_to_read.append((time, rev))

        # Read revisions from repo
        pool = Pool(processes=self.conf.processes)
        time_rev_count = pool.map(self.getnumoffilesfromrev, revs_to_read)
        pool.terminate()
        pool.join()

        # Update cache with new revisions and append then to general list
        for (time, rev, count) in time_rev_count:
            if 'files_in_tree' not in self.data.cache:
                self.data.cache['files_in_tree'] = {}
            self.data.cache['files_in_tree'][rev] = count
            lines.append('%d %d' % (int(time), count))

        self.data.total_commits += len(lines)
        for line in lines:
            parts = line.split(' ')
            if len(parts) != 2:
                continue
            (stamp, files) = parts[0:2]
            try:
                self.data.files_by_stamp[int(stamp)] = int(files)
            except ValueError:
                print('Warning: failed to parse line "%s"' % line)
