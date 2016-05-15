import datetime

from gitstats.RunExternal import RunExternal
from gitstats.collector.StatisticsCollector.StatisticsCollectorStrategy import StatisticsCollectorStrategy


class RevisionStrategy(StatisticsCollectorStrategy):
    def __init__(self, data, conf):
        super().__init__(data, conf)

    def collect(self):
        # Outputs "<stamp> <date> <time> <timezone> <author> '<' <mail> '>'"
        lines = RunExternal.execute(
            ['git rev-list --pretty=format:"%%at %%ai %%aN <%%aE>" %s' % self.getlogrange('HEAD'),
             'grep -v ^commit']).split('\n')
        for line in lines:
            parts = line.split(' ', 4)

            # First and last commit stamp (may be in any order because of cherry-picking and patches)
            stamp = self._collect_revision_stamps(parts)

            date = datetime.datetime.fromtimestamp(float(stamp))

            # activity
            # hour
            self._collect_activity_by_hour(date)

            # day of week
            self._collect_activty_by_day(date)

            # domain stats
            domain = self._collect_domain_stats(parts)

            # commits
            self._collect_commits(domain)

            # hour of week
            self._collect_hour_of_week(date)

            # most active hour?
            self._collect_most_active_hour(date)

            # month of year
            self._collect_month(date)

            # yearly/weekly activity
            self._collect_weekly_yearly_activity(date)

            # author stats
            author = self._collect_author(parts)

            #  commits, note again that commits may be in any date order because of cherry-picking and patches
            self._collect_author_commits(author, stamp)

            # author of the month/year
            self._collect_author_of_year(date, author)

            # authors: active days
            self._collect_author_active_days(date, author)

            # project: active days
            self._collect_project_active_days(date)

            # timezone
            self._collect_timezone(parts)

    def _collect_revision_stamps(self, parts):
        try:
            stamp = int(parts[0])
        except ValueError:
            stamp = 0
        if stamp > self.data.last_commit_stamp:
            self.data.last_commit_stamp = stamp
        if self.data.first_commit_stamp == 0 or stamp < self.data.first_commit_stamp:
            self.data.first_commit_stamp = stamp
        return stamp

    def _collect_activity_by_hour(self, date):
        hour = date.hour
        self.data.activity_by_hour_of_day[hour] = self.data.activity_by_hour_of_day.get(hour, 0) + 1
        # most active hour?
        if self.data.activity_by_hour_of_day[hour] > self.data.activity_by_hour_of_day_busiest:
            self.data.activity_by_hour_of_day_busiest = self.data.activity_by_hour_of_day[hour]

    def _collect_activty_by_day(self, date):
        day = date.weekday()
        self.data.activity_by_day_of_week[day] = self.data.activity_by_day_of_week.get(day, 0) + 1

    def _collect_domain_stats(self, parts):
        mail = parts[4].split('<', 1)[1]
        mail = mail.rstrip('>')
        domain = '?'
        if mail.find('@') != -1:
            domain = mail.rsplit('@', 1)[1]
        if domain not in self.data.domains:
            self.data.domains[domain] = {}
        return domain

    def _collect_commits(self, domain):
        self.data.domains[domain]['commits'] = self.data.domains[domain].get('commits', 0) + 1

    def _collect_hour_of_week(self, date):
        day = date.weekday
        hour = date.hour
        if day not in self.data.activity_by_hour_of_week:
            self.data.activity_by_hour_of_week[day] = {}
        self.data.activity_by_hour_of_week[day][hour] = self.data.activity_by_hour_of_week[day].get(hour, 0) + 1

    def _collect_most_active_hour(self, date):
        day = date.weekday
        hour = date.hour
        if self.data.activity_by_hour_of_week[day][hour] > self.data.activity_by_hour_of_week_busiest:
            self.data.activity_by_hour_of_week_busiest = self.data.activity_by_hour_of_week[day][hour]

    def _collect_month(self, date):
        month = date.month
        self.data.activity_by_month_of_year[month] = self.data.activity_by_month_of_year.get(month, 0) + 1

    def _collect_weekly_yearly_activity(self, date):
        yyw = date.strftime('%Y-%W')
        self.data.activity_by_year_week[yyw] = self.data.activity_by_year_week.get(yyw, 0) + 1
        if self.data.activity_by_year_week_peak < self.data.activity_by_year_week[yyw]:
            self.data.activity_by_year_week_peak = self.data.activity_by_year_week[yyw]

    def _collect_author(self, parts):
        author = parts[4].split('<', 1)[0]
        author = author.rstrip()
        author = self.get_merged_author(author)
        if author not in self.data.authors:
            self.data.authors[author] = {}
        return author

    def _collect_author_commits(self, author, stamp):
        if 'last_commit_stamp' not in self.data.authors[author]:
            self.data.authors[author]['last_commit_stamp'] = stamp
        if stamp > self.data.authors[author]['last_commit_stamp']:
            self.data.authors[author]['last_commit_stamp'] = stamp
        if 'first_commit_stamp' not in self.data.authors[author]:
            self.data.authors[author]['first_commit_stamp'] = stamp
        if stamp < self.data.authors[author]['first_commit_stamp']:
            self.data.authors[author]['first_commit_stamp'] = stamp

    def _collect_author_of_year(self, date, author):
        yymm = date.strftime('%Y-%m')
        if yymm in self.data.author_of_month:
            self.data.author_of_month[yymm][author] = self.data.author_of_month[yymm].get(author, 0) + 1
        else:
            self.data.author_of_month[yymm] = {}
            self.data.author_of_month[yymm][author] = 1
        self.data.commits_by_month[yymm] = self.data.commits_by_month.get(yymm, 0) + 1

        yy = date.year
        if yy in self.data.author_of_year:
            self.data.author_of_year[yy][author] = self.data.author_of_year[yy].get(author, 0) + 1
        else:
            self.data.author_of_year[yy] = {}
            self.data.author_of_year[yy][author] = 1
        self.data.commits_by_year[yy] = self.data.commits_by_year.get(yy, 0) + 1

    def _collect_author_active_days(self, date, author):
        yymmdd = date.strftime(self.conf.date_format)
        if 'last_active_day' not in self.data.authors[author]:
            self.data.authors[author]['last_active_day'] = yymmdd
            self.data.authors[author]['active_days'] = set([yymmdd])
        elif yymmdd != self.data.authors[author]['last_active_day']:
            self.data.authors[author]['last_active_day'] = yymmdd
            self.data.authors[author]['active_days'].add(yymmdd)

    def _collect_project_active_days(self, date):
        yymmdd = date.strftime(self.conf.date_format)
        if yymmdd != self.data.last_active_day:
            self.data.last_active_day = yymmdd
            self.data.active_days.add(yymmdd)

    def _collect_timezone(self, parts):
        timezone = parts[3]
        self.data.commits_by_timezone[timezone] = self.data.commits_by_timezone.get(timezone, 0) + 1
