import re
from multiprocessing import Pool

from gitstats.RunExternal import RunExternal
from gitstats.collector.StatisticsCollector.StatisticsCollectorStrategy import StatisticsCollectorStrategy


class FileStrategy(StatisticsCollectorStrategy):
    def __init__(self, data, conf):
        super().__init__(data, conf)

    @staticmethod
    def get_num_of_lines_in_blob(ext_blob):
        """
        Get number of lines in blob
        """
        ext, blob_id = ext_blob
        return ext, blob_id, int(RunExternal.execute(['git cat-file blob %s' % blob_id, 'wc -l']).split()[0])

    def collect(self):
        # extensions and size of files
        lines = RunExternal.execute(['git ls-tree -r -l -z %s' % self.get_commit_range('HEAD', end_only=True)]).split(
            '\000')
        blobs_to_read = []
        for line in lines:
            if len(line) == 0:
                continue
            parts = re.split('\s+', line, 4)
            if parts[0] == '160000' and parts[3] == '-':
                # skip submodules
                continue
            blob_id = parts[2]
            size = int(parts[3])
            full_path = parts[4]

            self.data.total_size += size
            self.data.total_files += 1

            filename = full_path.split('/')[-1]  # strip directories
            if filename.find('.') == -1 or filename.rfind('.') == 0:
                ext = ''
            else:
                ext = filename[(filename.rfind('.') + 1):]
            if len(ext) > self.conf.max_ext_length:
                ext = ''
            if ext not in self.data.extensions:
                self.data.extensions[ext] = {'files': 0, 'lines': 0}
            self.data.extensions[ext]['files'] += 1
            # if cache empty then add ext and blob id to list of new blob's
            # otherwise try to read needed info from cache
            if 'lines_in_blob' not in list(self.data.cache.keys()):
                blobs_to_read.append((ext, blob_id))
                continue
            if blob_id in list(self.data.cache['lines_in_blob'].keys()):
                self.data.extensions[ext]['lines'] += self.data.cache['lines_in_blob'][blob_id]
            else:
                blobs_to_read.append((ext, blob_id))

        # Get info about line count for new blob's that wasn't found in cache
        pool = Pool(processes=self.conf.processes)
        ext_blob_line_count = pool.map(self.get_num_of_lines_in_blob, blobs_to_read)
        pool.terminate()
        pool.join()

        # Update cache and write down info about number of number of lines
        for (ext, blob_id, line_count) in ext_blob_line_count:
            if 'lines_in_blob' not in self.data.cache:
                self.data.cache['lines_in_blob'] = {}
            self.data.cache['lines_in_blob'][blob_id] = line_count
            self.data.extensions[ext]['lines'] += self.data.cache['lines_in_blob'][blob_id]
