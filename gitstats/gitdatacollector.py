import datetime
import logging
import re
import os

from multiprocessing import Pool

from gitstats.data.author import Author
from gitstats.datacollector import DataCollector
from gitstats.miscfuncs import getcommitrange, getlogrange, getnumoffilesfromrev, getnumoflinesinblob, \
    getpipeoutput, getstatsummarycounts


class GitDataCollector(DataCollector):
    def __init__(self, conf):
        super(GitDataCollector, self).__init__(conf)
        
    def collect(self, directory):
        super(GitDataCollector, self).collect(directory)

        self.total_authors += int(getpipeoutput(['git shortlog -s %s' % getlogrange(self.conf), 'wc -l']))
        # self.total_lines = int(getoutput('git-ls-files -z |xargs -0 cat |wc -l'))
        self.get_tags()
        self.get_revision_info()
        self.get_file_info()
        self.get_loc_info()
        self.get_author_info()

    def xlate(self, name):
        if name in self.conf['name_xlate']:
            return self.conf['name_xlate'][name]
        return name

    def get_author_info(self):
        # Per-author statistics
        # defined for stamp, author only if author commited at this timestamp.
        self.changes_by_date_by_author = {}  # stamp -> author -> lines_added
        # Similar to the above, but never use --first-parent
        # (we need to walk through every commit to know who
        # committed what, not just through mainline)
        lines = getpipeoutput(
            ['git log --shortstat --date-order --pretty=format:"%%at %%aN" %s' % (
                getlogrange(self.conf, 'HEAD'))]).split('\n')
        lines.reverse()
        inserted = 0
        deleted = 0
        stamp = 0
        for line in lines:
            if len(line) == 0:
                continue

            # <stamp> <author>
            if re.search('files? changed', line) is None:
                pos = line.find(' ')
                if pos != -1:
                    try:
                        oldstamp = stamp
                        (stamp, author) = (int(line[:pos]), line[pos + 1:])
                        author = self.xlate(author)
                        if oldstamp > stamp:
                            # clock skew, keep old timestamp to avoid having ugly graph
                            stamp = oldstamp
                        if author not in self.authors:
                            self.authors[author] = Author()
                        self.authors[author].commits += 1
                        self.authors[author].lines_added += inserted
                        self.authors[author].lines_removed += deleted
                        if stamp not in self.changes_by_date_by_author:
                            self.changes_by_date_by_author[stamp] = {}
                        if author not in self.changes_by_date_by_author[stamp]:
                            self.changes_by_date_by_author[stamp][author] = Author()
                        self.changes_by_date_by_author[stamp][author].lines_added = self.authors[author].lines_added
                        self.changes_by_date_by_author[stamp][author].commits = self.authors[author].commits
                        files, inserted, deleted = 0, 0, 0
                    except ValueError:
                        logging.warning(f'unexpected line "{line}')
                else:
                    logging.warning(f'unexpected line "{line}')
            else:
                numbers = getstatsummarycounts(line)

                if len(numbers) == 3:
                    (files, inserted, deleted) = map(lambda el: int(el), numbers)
                else:
                    logging.warning(f'Failed to handle line "{line}"')
                    (files, inserted, deleted) = (0, 0, 0)

    def get_loc_info(self):
        # line statistics
        # outputs:
        #  N files changed, N insertions (+), N deletions(-)
        # <stamp> <author>
        self.changes_by_date = {}  # stamp -> { files, ins, del }
        # computation of lines of code by date is better done
        # on a linear history.
        extra = ''
        if self.conf['linear_linestats']:
            extra = '--first-parent -m'
        lines = getpipeoutput(
            ['git log --shortstat %s --pretty=format:"%%at %%aN" %s' % (extra, getlogrange(self.conf, 'HEAD'))]).split(
            '\n')
        lines.reverse()
        files = 0
        inserted = 0
        deleted = 0
        total_lines = 0
        for line in lines:
            if len(line) == 0:
                continue

            # <stamp> <author>
            if re.search('files? changed', line) is None:
                pos = line.find(' ')
                if pos != -1:
                    try:
                        (stamp, author) = (int(line[:pos]), line[pos + 1:])
                        self.changes_by_date[stamp] = {'files': files, 'ins': inserted, 'del': deleted,
                                                       'lines': total_lines}

                        date = datetime.datetime.fromtimestamp(stamp)
                        yymm = date.strftime('%Y-%m')
                        self.lines_added_by_month[yymm] = self.lines_added_by_month.get(yymm, 0) + inserted
                        self.lines_removed_by_month[yymm] = self.lines_removed_by_month.get(yymm, 0) + deleted

                        yy = date.year
                        self.lines_added_by_year[yy] = self.lines_added_by_year.get(yy, 0) + inserted
                        self.lines_removed_by_year[yy] = self.lines_removed_by_year.get(yy, 0) + deleted

                        files, inserted, deleted = 0, 0, 0
                    except ValueError:
                        logging.warning(f'unexpected line "{line}')
                else:
                    logging.warning(f'unexpected line "{line}')
            else:
                numbers = getstatsummarycounts(line)

                if len(numbers) == 3:
                    (files, inserted, deleted) = map(lambda el: int(el), numbers)
                    total_lines += inserted
                    total_lines -= deleted
                    self.total_lines_added += inserted
                    self.total_lines_removed += deleted

                else:
                    logging.warning(f'Failed to handle line "{line}"')
                    (files, inserted, deleted) = (0, 0, 0)
            # self.changes_by_date[stamp] = { 'files': files, 'ins': inserted, 'del': deleted }
        self.total_lines += total_lines

    def get_file_info(self):
        # extensions and size of files
        lines = getpipeoutput(['git ls-tree -r -l -z %s' % getcommitrange(self.conf, 'HEAD', end_only=True)]).split(
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
            fullpath = parts[4]

            self.total_size += size
            self.total_files += 1

            _, ext = os.path.splitext(fullpath)
            if len(ext) > self.conf['max_ext_length']:
                ext = ''
            if ext not in self.extensions:
                self.extensions[ext] = {'files': 0, 'lines': 0}
            self.extensions[ext]['files'] += 1
            # if cache empty then add ext and blob id to list of new blob's
            # otherwise try to read needed info from cache
            if 'lines_in_blob' not in self.cache.keys():
                blobs_to_read.append((ext, blob_id))
                continue
            if blob_id in self.cache['lines_in_blob'].keys():
                self.extensions[ext]['lines'] += self.cache['lines_in_blob'][blob_id]
            else:
                blobs_to_read.append((ext, blob_id))
        # Get info abount line count for new blob's that wasn't found in cache
        pool = Pool(processes=self.conf['processes'])
        ext_blob_linecount = pool.map(getnumoflinesinblob, blobs_to_read)
        pool.terminate()
        pool.join()
        # Update cache and write down info about number of number of lines
        for (ext, blob_id, linecount) in ext_blob_linecount:
            if 'lines_in_blob' not in self.cache:
                self.cache['lines_in_blob'] = {}
            self.cache['lines_in_blob'][blob_id] = linecount
            self.extensions[ext]['lines'] += self.cache['lines_in_blob'][blob_id]

    def get_revision_info(self):
        # Collect revision statistics
        # Outputs "<stamp> <date> <time> <timezone> <author> '<' <mail> '>'"
        lines = getpipeoutput(
            ['git rev-list --pretty=format:"%%at %%ai %%aN <%%aE>" %s' % getlogrange(self.conf, 'HEAD'),
             'grep -v ^commit']).split(
            '\n')
        for line in lines:
            parts = line.split(' ', 4)
            try:
                stamp = int(parts[0])
            except ValueError:
                stamp = 0
            timezone = parts[3]
            author, mail = parts[4].split('<', 1)
            author = self.xlate(author.rstrip())
            mail = mail.rstrip('>')
            domain = '?'
            if mail.find('@') != -1:
                domain = mail.rsplit('@', 1)[1]
            date = datetime.datetime.fromtimestamp(float(stamp))

            # First and last commit stamp (may be in any order because of cherry-picking and patches)
            if stamp > self.last_commit_stamp:
                self.last_commit_stamp = stamp
            if self.first_commit_stamp == 0 or stamp < self.first_commit_stamp:
                self.first_commit_stamp = stamp

            # activity
            # hour
            hour = date.hour
            self.activity_by_hour_of_day[hour] = self.activity_by_hour_of_day.get(hour, 0) + 1
            # most active hour?
            if self.activity_by_hour_of_day[hour] > self.activity_by_hour_of_day_busiest:
                self.activity_by_hour_of_day_busiest = self.activity_by_hour_of_day[hour]

            # day of week
            day = date.weekday()
            self.activity_by_day_of_week[day] = self.activity_by_day_of_week.get(day, 0) + 1

            # domain stats
            if domain not in self.domains:
                self.domains[domain] = {}
            # commits
            self.domains[domain]['commits'] = self.domains[domain].get('commits', 0) + 1

            # hour of week
            if day not in self.activity_by_hour_of_week:
                self.activity_by_hour_of_week[day] = {}
            self.activity_by_hour_of_week[day][hour] = self.activity_by_hour_of_week[day].get(hour, 0) + 1
            # most active hour?
            if self.activity_by_hour_of_week[day][hour] > self.activity_by_hour_of_week_busiest:
                self.activity_by_hour_of_week_busiest = self.activity_by_hour_of_week[day][hour]

            # month of year
            month = date.month
            self.activity_by_month_of_year[month] = self.activity_by_month_of_year.get(month, 0) + 1

            # yearly/weekly activity
            yyw = date.strftime('%Y-%W')
            self.activity_by_year_week[yyw] = self.activity_by_year_week.get(yyw, 0) + 1
            if self.activity_by_year_week_peak < self.activity_by_year_week[yyw]:
                self.activity_by_year_week_peak = self.activity_by_year_week[yyw]

            # author stats
            if author not in self.authors:
                self.authors[author] = Author()
            self.authors[author].activity_by_day_and_hour[day][hour] += 1
            # commits, note again that commits may be in any date order because of cherry-picking and patches
            if not self.authors[author].last_commit_stamp:
                self.authors[author].last_commit_stamp = stamp
            if stamp > self.authors[author].last_commit_stamp:
                self.authors[author].last_commit_stamp = stamp
            if not self.authors[author].first_commit_stamp:
                self.authors[author].first_commit_stamp = stamp
            if stamp < self.authors[author].first_commit_stamp:
                self.authors[author].first_commit_stamp = stamp

            # author of the month/year
            yymm = date.strftime('%Y-%m')
            if yymm in self.author_of_month:
                self.author_of_month[yymm][author] = self.author_of_month[yymm].get(author, 0) + 1
            else:
                self.author_of_month[yymm] = {}
                self.author_of_month[yymm][author] = 1
            self.commits_by_month[yymm] = self.commits_by_month.get(yymm, 0) + 1

            yy = date.year
            if yy in self.author_of_year:
                self.author_of_year[yy][author] = self.author_of_year[yy].get(author, 0) + 1
            else:
                self.author_of_year[yy] = {}
                self.author_of_year[yy][author] = 1
            self.commits_by_year[yy] = self.commits_by_year.get(yy, 0) + 1

            # authors: active days
            yymmdd = date.strftime('%Y-%m-%d')
            if not self.authors[author].last_active_day:
                self.authors[author].last_active_day = yymmdd
            elif yymmdd != self.authors[author].last_active_day:
                self.authors[author].last_active_day = yymmdd
            self.authors[author].active_days.add(yymmdd)

            # project: active days
            if yymmdd != self.last_active_day:
                self.last_active_day = yymmdd
                self.active_days.add(yymmdd)

            # timezone
            self.commits_by_timezone[timezone] = self.commits_by_timezone.get(timezone, 0) + 1
        # outputs "<stamp> <files>" for each revision
        revlines = getpipeoutput(
            ['git rev-list --pretty=format:"%%at %%T" %s' % getlogrange(self.conf, 'HEAD'),
             'grep -v ^commit']).strip().split('\n')
        lines = []
        revs_to_read = []
        # Look up rev in cache and take info from cache if found
        # If not append rev to list of rev to read from repo
        for revline in revlines:
            time, rev = revline.split(' ')
            # if cache empty then add time and rev to list of new rev's
            # otherwise try to read needed info from cache
            if 'files_in_tree' not in self.cache.keys():
                revs_to_read.append((time, rev))
                continue
            if rev in self.cache['files_in_tree'].keys():
                lines.append('%d %d' % (int(time), self.cache['files_in_tree'][rev]))
            else:
                revs_to_read.append((time, rev))
        # Read revisions from repo
        pool = Pool(processes=self.conf['processes'])
        time_rev_count = pool.map(getnumoffilesfromrev, revs_to_read)
        pool.terminate()
        pool.join()
        # Update cache with new revisions and append then to general list
        for (time, rev, count) in time_rev_count:
            if 'files_in_tree' not in self.cache:
                self.cache['files_in_tree'] = {}
            self.cache['files_in_tree'][rev] = count
            lines.append('%d %d' % (int(time), count))
        self.total_commits += len(lines)
        for line in lines:
            parts = line.split(' ')
            if len(parts) != 2:
                continue
            (stamp, files) = parts[0:2]
            try:
                self.files_by_stamp[int(stamp)] = int(files)
            except ValueError:
                logging.warning(f'Failed to parse line "{line}"')

    def get_tags(self):
        # tags
        lines = getpipeoutput(['git show-ref --tags']).split('\n')
        for line in lines:
            if len(line) == 0:
                continue
            (line_hash, tag) = line.split(' ')

            tag = tag.replace('refs/tags/', '')
            output = getpipeoutput(['git log "%s" --pretty=format:"%%at %%aN" -n 1' % line_hash])
            if len(output) > 0:
                parts = output.split(' ')
                try:
                    stamp = int(parts[0])
                except ValueError:
                    stamp = 0
                self.tags[tag] = {'stamp': stamp,
                                  'hash': line_hash,
                                  'date': datetime.datetime.fromtimestamp(stamp).strftime('%Y-%m-%d'),
                                  'commits': 0,
                                  'authors': {}}
        # collect info on tags, starting from latest
        tags_sorted_by_date_asc = [tup[1] for tup in sorted([(el[1]['date'], el[0]) for el in self.tags.items()])]
        # tags_sorted_by_date_desc = map(lambda el: el[1],
        #                                reversed(sorted(map(lambda el: (el[1]['date'], el[0]), self.tags.items()))))
        prev = None
        #        for tag in reversed(tags_sorted_by_date_desc):
        for tag in tags_sorted_by_date_asc:
            cmd = 'git shortlog -s "%s"' % tag
            if prev is not None:
                cmd += ' "^%s"' % prev
            output = getpipeoutput([cmd])
            if len(output) == 0:
                continue
            prev = tag
            for line in output.split('\n'):
                parts = re.split('\s+', line, 2)
                commits = int(parts[1])
                author = parts[2]
                self.tags[tag]['commits'] += commits
                self.tags[tag]['authors'][author] = commits

    def refine(self):
        # authors
        # name -> {place_by_commits, commits_frac, date_first, date_last, timedelta}
        self.authors_by_commits = self.getAuthors()
        for i, name in enumerate(self.authors_by_commits):
            self.authors[name].place_by_commits = i + 1

        for name in self.authors.keys():
            a = self.authors[name]
            a.commits_frac = (100 * float(a.commits)) / self.getTotalCommits()
            date_first = datetime.datetime.fromtimestamp(a.first_commit_stamp)
            date_last = datetime.datetime.fromtimestamp(a.last_commit_stamp)
            delta = date_last - date_first
            a.date_first = date_first.strftime('%Y-%m-%d')
            a.date_last = date_last.strftime('%Y-%m-%d')
            a.timedelta = delta
            for day in range(6):
                for hour in range(24):
                    if day > 4 or hour < 8 or hour > 17:
                        a.extra_effort += a.activity_by_day_and_hour[day][hour]
            a.extra_frac = (100 * float(a.extra_effort)) / a.commits

    def getActiveDays(self):
        return self.active_days

    def getActivityByDayOfWeek(self):
        return self.activity_by_day_of_week

    def getActivityByHourOfDay(self):
        return self.activity_by_hour_of_day

    def getAuthorInfo(self, author):
        return self.authors[author]

    def getAuthors(self, limit=None):
        res = [el[0] for el in sorted(self.authors.items(), key=lambda x: x[1].commits, reverse=True)]
        return res[:limit]

    def getCommitDeltaDays(self):
        return (self.last_commit_stamp / 86400 - self.first_commit_stamp / 86400) + 1

    def getDomainInfo(self, domain):
        return self.domains[domain]

    def getDomains(self):
        return self.domains.keys()

    def getFirstCommitDate(self):
        return datetime.datetime.fromtimestamp(self.first_commit_stamp)

    def getLastCommitDate(self):
        return datetime.datetime.fromtimestamp(self.last_commit_stamp)

    def getTags(self):
        lines = getpipeoutput(['git show-ref --tags', 'cut -d/ -f3'])
        return lines.split('\n')

    def getTagDate(self, tag):
        return self.revToDate('tags/' + tag)

    def getTotalAuthors(self):
        # because we are equating names (see name_xlate), the total authors will be the number of
        # elements in the authors dictionary rather than the count from the git log
        return len(self.authors)

    def getTotalCommits(self):
        return self.total_commits

    def getTotalFiles(self):
        return self.total_files

    def getTotalLOC(self):
        return self.total_lines

    def getTotalSize(self):
        return self.total_size

    def revToDate(self, rev):
        stamp = int(getpipeoutput(['git log --pretty=format:%%at "%s" -n 1' % rev]))
        return datetime.datetime.fromtimestamp(stamp).strftime('%Y-%m-%d')
