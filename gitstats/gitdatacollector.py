import datetime

from collections import defaultdict

from gitstats.datacollector import DataCollector
from gitstats.data import Author, AuthorRow, File, LocByDate, Revision, Tag
from gitstats.data_generators import gen_author_data, gen_author_totals_data, gen_tag_data, gen_revision_data, \
    gen_file_data, gen_loc_data
from gitstats.miscfuncs import getpipeoutput


class GitDataCollector(DataCollector):
    def __init__(self, conf):
        super(GitDataCollector, self).__init__(conf)
        
    def collect(self, directory):
        super(GitDataCollector, self).collect(directory)

        self.total_authors += self.get_total_authors()
        self.get_tags()
        self.get_revision_info()
        self.get_file_info()
        self.get_loc_info()
        self.get_author_info()

    def get_total_authors(self):
        return gen_author_totals_data(self.conf)

    def get_author_info(self):
        # Per-author statistics
        # defined for stamp, author only if author commited at this timestamp.

        self.changes_by_date_by_author = defaultdict(lambda: defaultdict(lambda: Author())) # stamp -> author -> lines_added

        def row_processor(row: AuthorRow):
            self.authors[row.author].commits += 1
            self.authors[row.author].lines_added += row.lines_inserted
            self.authors[row.author].lines_removed += row.lines_deleted
            self.changes_by_date_by_author[row.stamp][row.author].lines_added = self.authors[row.author].lines_added
            self.changes_by_date_by_author[row.stamp][row.author].commits = self.authors[row.author].commits

        gen_author_data(self.conf, row_processor)

    def get_loc_info(self):

        self.changes_by_date = {}  # stamp -> { files, ins, del }
        def row_processor(row: LocByDate):
            self.changes_by_date[row.stamp] = {
                'files': row.file_count,
                'ins': row.lines_inserted,
                'del': row.lines_deleted,
                'lines': row.total_lines
            }
            date = datetime.datetime.fromtimestamp(row.stamp)
            yymm = date.strftime('%Y-%m')
            self.lines_added_by_month[yymm] = self.lines_added_by_month.get(yymm, 0) + row.lines_inserted
            self.lines_removed_by_month[yymm] = self.lines_removed_by_month.get(yymm, 0) + row.lines_deleted

            yy = date.year
            self.lines_added_by_year[yy] = self.lines_added_by_year.get(yy, 0) + row.lines_inserted
            self.lines_removed_by_year[yy] = self.lines_removed_by_year.get(yy, 0) + row.lines_deleted

            self.total_lines_added += row.lines_inserted
            self.total_lines_removed += row.lines_deleted

        self.total_lines += gen_loc_data(self.conf, row_processor)

    def get_file_info(self):
        # extensions and size of files
        def row_processor(row: File):
            self.total_size += row.size
            self.total_files += 1
            if row.ext not in self.extensions:
                self.extensions[row.ext] = {'files': 0, 'lines': 0}
            self.extensions[row.ext]['files'] += 1
            self.extensions[row.ext]['lines'] += row.lines

        gen_file_data(self.conf, row_processor)

    def get_revision_info(self):
        # Collect revision statistics
        # Outputs "<stamp> <date> <time> <timezone> <author> '<' <mail> '>'"

        def row_processor(row: Revision):
            stamp = row.stamp
            domain = row.domain
            author = row.author
            timezone = row.timezone

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

            # file counts
            self.files_by_stamp[stamp] = row.file_count

        self.total_commits += gen_revision_data(self.conf, row_processor)

    def get_tags(self):
        def row_processor(row: Tag):
            self.tags[row.tag] = {
                'stamp': row.stamp,
                'hash': row.hash,
                'date': datetime.datetime.fromtimestamp(row.stamp).strftime('%Y-%m-%d'),
                'commits': row.commits,
                'authors': row.authors
            }

        gen_tag_data(self.conf, row_processor)

    def refine(self):
        # authors
        # name -> {place_by_commits, commits_frac, date_first, date_last, timedelta}
        self.authors_by_commits = self.getAuthors()
        total_commits_without_merge = 0
        for i, name in enumerate(self.authors_by_commits):
            self.authors[name].place_by_commits = i + 1
            total_commits_without_merge += self.authors[name].commits

        for name in self.authors.keys():
            a = self.authors[name]
            a.commits_frac = (100 * float(a.commits)) / total_commits_without_merge
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
