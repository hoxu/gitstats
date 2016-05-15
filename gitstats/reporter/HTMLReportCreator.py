import datetime
import glob
import os
import shutil
import time

from gitstats.RunExternal import RunExternal
from gitstats.reporter.PlotFileCreator import PlotFileCreator
from gitstats.reporter.ReportCreator import ReportCreator


class HTMLReportCreator(ReportCreator):
    @staticmethod
    def html_linkify(text):
        return text.lower().replace(' ', '_')

    @staticmethod
    def get_git_version():
        return RunExternal.execute(['git --version']).split('\n')[0]

    @staticmethod
    def print_nav(f):
        f.write("""
<div class="nav">
<ul>
<li><a href="index.html">General</a></li>
<li><a href="activity.html">Activity</a></li>
<li><a href="authors.html">Authors</a></li>
<li><a href="files.html">Files</a></li>
<li><a href="lines.html">Lines</a></li>
<li><a href="tags.html">Tags</a></li>
</ul>
</div>
    """)

    def __init__(self, conf, data, path):
        super().__init__(conf, data, path)
        self.title = self.data.project_name
        self.WEEKDAYS = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')

    def html_header(self, level, text):
        name = self.html_linkify(text)
        return '\n<h%d id="%s"><a href="#%s">%s</a></h%d>\n\n' % (level, name, name, text, level)

    def get_version(self):
        if not self.version:
            gitstats_repo = os.path.dirname(os.path.abspath(os.path.join(__file__, "../..")))
            self.version = RunExternal.execute(["git --git-dir=%s/.git --work-tree=%s rev-parse --short %s" %
                                                (gitstats_repo, gitstats_repo,
                                                 self.get_commit_range('HEAD').split('\n')[0])])
        return self.version

    def get_gnuplot_version(self):
        return RunExternal.execute(['%s --version' % self.conf.gnuplot_cmd]).split('\n')[0]

    def get_commit_range(self, default_range='HEAD', end_only=False):
        if len(self.conf.commit_end) > 0:
            if end_only or len(self.conf.commit_begin) == 0:
                return self.conf.commit_end
            return '%s..%s' % (self.conf.commit_begin, self.conf.commit_end)
        return default_range

    def _create_index(self):
        f = open(self.path + "/index.html", 'w')
        time_format = '%Y-%m-%d %H:%M:%S'
        self.print_header(f)

        f.write('<h1>GitStats - %s</h1>' % self.data.project_name)

        self.print_nav(f)

        f.write('<dl>')
        f.write('<dt>Project name</dt><dd>%s</dd>' % self.data.project_name)
        f.write('<dt>Generated</dt><dd>%s (in %d seconds)</dd>' % (
            datetime.datetime.now().strftime(time_format), time.time() - self.data.get_stamp_created()))
        f.write(
            '<dt>Generator</dt><dd><a href="http://gitstats.sourceforge.net/">GitStats</a> (version %s), %s, %s</dd>' % (
                self.get_version(), self.get_git_version(), self.get_gnuplot_version()))
        f.write('<dt>Report Period</dt><dd>%s to %s</dd>' % (
            self.data.get_first_commit_date().strftime(time_format), self.data.get_last_commit_date().strftime(time_format)))
        f.write('<dt>Age</dt><dd>%d days, %d active days (%3.2f%%)</dd>' % (
            self.data.get_commit_delta_days(), len(self.data.get_active_days()),
            (100.0 * len(self.data.get_active_days()) / self.data.get_commit_delta_days())))
        f.write('<dt>Total Files</dt><dd>%s</dd>' % self.data.get_total_files())
        f.write('<dt>Total Lines of Code</dt><dd>%s (%d added, %d removed)</dd>' % (
            self.data.get_total_loc(), self.data.total_lines_added, self.data.total_lines_removed))
        f.write('<dt>Total Commits</dt><dd>%s (average %.1f commits per active day, %.1f per all days)</dd>' % (
            self.data.get_total_commits(), float(self.data.get_total_commits()) / len(self.data.get_active_days()),
            float(self.data.get_total_commits()) / self.data.get_commit_delta_days()))
        f.write('<dt>Authors</dt><dd>%s (average %.1f commits per author)</dd>' % (
            self.data.get_total_authors(), (1.0 * self.data.get_total_commits()) / self.data.get_total_authors()))
        f.write('</dl>')

        f.write('</body>\n</html>')
        f.close()

    def _create_activity(self):
        f = open(self.path + '/activity.html', 'w')
        self.print_header(f)
        f.write('<h1>Activity</h1>')
        self.print_nav(f)

        # f.write('<h2>Last 30 days</h2>')

        # f.write('<h2>Last 12 months</h2>')

        # Weekly activity
        weeks_nr = 32
        f.write(self.html_header(2, 'Weekly activity'))
        f.write('<p>Last %d weeks</p>' % weeks_nr)

        # generate weeks to show (previous N weeks from now)
        now = datetime.datetime.now()
        delta_week = datetime.timedelta(7)
        weeks = []
        stamp_cur = now
        for i in range(weeks_nr):
            weeks.insert(0, stamp_cur.strftime('%Y-%W'))
            stamp_cur -= delta_week

        # top row: commits & bar
        f.write('<table class="noborders"><tr>')
        for i in range(weeks_nr):
            commits = 0
            if weeks[i] in self.data.activity_by_year_week:
                commits = self.data.activity_by_year_week[weeks[i]]

            percentage = 0
            if weeks[i] in self.data.activity_by_year_week:
                percentage = float(self.data.activity_by_year_week[weeks[i]]) / self.data.activity_by_year_week_peak
            height = max(1, int(200 * percentage))
            f.write(
                '<td style="text-align: center; vertical-align: bottom">%d<div style="display: block; background-color: red; width: 20px; height: %dpx"></div></td>' % (
                    commits, height))

        # bottom row: year/week
        f.write('</tr><tr>')
        for i in range(weeks_nr):
            f.write('<td>%s</td>' % (weeks_nr - i))
        f.write('</tr></table>')

        # Hour of Day
        f.write(self.html_header(2, 'Hour of Day'))
        hour_of_day = self.data.get_activity_by_hour_of_day()
        f.write('<table><tr><th>Hour</th>')
        for i in range(24):
            f.write('<th>%d</th>' % i)
        f.write('</tr>\n<tr><th>Commits</th>')
        fp = open(self.path + '/hour_of_day.dat', 'w')
        for i in range(24):
            if i in hour_of_day:
                r = 127 + int((float(hour_of_day[i]) / self.data.activity_by_hour_of_day_busiest) * 128)
                f.write('<td style="background-color: rgb(%d, 0, 0)">%d</td>' % (r, hour_of_day[i]))
                fp.write('%d %d\n' % (i, hour_of_day[i]))
            else:
                f.write('<td>0</td>')
                fp.write('%d 0\n' % i)
        fp.close()
        f.write('</tr>\n<tr><th>%</th>')
        total_commits = self.data.get_total_commits()
        for i in range(0, 24):
            if i in hour_of_day:
                r = 127 + int((float(hour_of_day[i]) / self.data.activity_by_hour_of_day_busiest) * 128)
                f.write('<td style="background-color: rgb(%d, 0, 0)">%.2f</td>' % (
                    r, (100.0 * hour_of_day[i]) / total_commits))
            else:
                f.write('<td>0.00</td>')
        f.write('</tr></table>')
        f.write('<img src="hour_of_day.png" alt="Hour of Day">')
        fg = open(self.path + '/hour_of_day.dat', 'w')
        for i in range(0, 24):
            if i in hour_of_day:
                fg.write('%d %d\n' % (i + 1, hour_of_day[i]))
            else:
                fg.write('%d 0\n' % (i + 1))
        fg.close()

        # Day of Week
        f.write(self.html_header(2, 'Day of Week'))
        day_of_week = self.data.get_activity_by_day_of_week()
        f.write('<div class="vtable"><table>')
        f.write('<tr><th>Day</th><th>Total (%)</th></tr>')
        fp = open(self.path + '/day_of_week.dat', 'w')
        for d in range(0, 7):
            commits = 0
            if d in day_of_week:
                commits = day_of_week[d]
            fp.write('%d %s %d\n' % (d + 1, self.WEEKDAYS[d], commits))
            f.write('<tr>')
            f.write('<th>%s</th>' % (self.WEEKDAYS[d]))
            if d in day_of_week:
                f.write('<td>%d (%.2f%%)</td>' % (day_of_week[d], (100.0 * day_of_week[d]) / total_commits))
            else:
                f.write('<td>0</td>')
            f.write('</tr>')
        f.write('</table></div>')
        f.write('<img src="day_of_week.png" alt="Day of Week">')
        fp.close()

        # Hour of Week
        f.write(self.html_header(2, 'Hour of Week'))
        f.write('<table>')

        f.write('<tr><th>Weekday</th>')
        for hour in range(0, 24):
            f.write('<th>%d</th>' % hour)
        f.write('</tr>')

        for weekday in range(0, 7):
            f.write('<tr><th>%s</th>' % (self.WEEKDAYS[weekday]))
            for hour in range(0, 24):
                try:
                    commits = self.data.activity_by_hour_of_week[weekday][hour]
                except KeyError:
                    commits = 0
                if commits != 0:
                    f.write('<td')
                    r = 127 + int((float(commits) / self.data.activity_by_hour_of_week_busiest) * 128)
                    f.write(' style="background-color: rgb(%d, 0, 0)"' % r)
                    f.write('>%d</td>' % commits)
                else:
                    f.write('<td></td>')
            f.write('</tr>')

        f.write('</table>')

        # Month of Year
        f.write(self.html_header(2, 'Month of Year'))
        f.write('<div class="vtable"><table>')
        f.write('<tr><th>Month</th><th>Commits (%)</th></tr>')
        fp = open(self.path + '/month_of_year.dat', 'w')
        for mm in range(1, 13):
            commits = 0
            if mm in self.data.activity_by_month_of_year:
                commits = self.data.activity_by_month_of_year[mm]
            f.write(
                '<tr><td>%d</td><td>%d (%.2f %%)</td></tr>' % (
                    mm, commits, (100.0 * commits) / self.data.get_total_commits()))
            fp.write('%d %d\n' % (mm, commits))
        fp.close()
        f.write('</table></div>')
        f.write('<img src="month_of_year.png" alt="Month of Year">')

        # Commits by year/month
        f.write(self.html_header(2, 'Commits by year/month'))
        f.write(
            '<div class="vtable"><table><tr><th>Month</th><th>Commits</th><th>Lines added</th><th>Lines removed</th></tr>')
        for yy_mm in reversed(sorted(self.data.commits_by_month.keys())):
            f.write('<tr><td>%s</td><td>%d</td><td>%d</td><td>%d</td></tr>' % (
                yy_mm, self.data.commits_by_month.get(yy_mm, 0), self.data.lines_added_by_month.get(yy_mm, 0),
                self.data.lines_removed_by_month.get(yy_mm, 0)))
        f.write('</table></div>')
        f.write('<img src="commits_by_year_month.png" alt="Commits by year/month">')
        fg = open(self.path + '/commits_by_year_month.dat', 'w')
        for yy_mm in sorted(self.data.commits_by_month.keys()):
            fg.write('%s %s\n' % (yy_mm, self.data.commits_by_month[yy_mm]))
        fg.close()

        # Commits by year
        f.write(self.html_header(2, 'Commits by Year'))
        f.write(
            '<div class="vtable"><table><tr><th>Year</th><th>Commits (% of all)</th><th>Lines added</th><th>Lines removed</th></tr>')
        for yy in reversed(sorted(self.data.commits_by_year.keys())):
            f.write('<tr><td>%s</td><td>%d (%.2f%%)</td><td>%d</td><td>%d</td></tr>' % (
                yy, self.data.commits_by_year.get(yy, 0),
                (100.0 * self.data.commits_by_year.get(yy, 0)) / self.data.get_total_commits(),
                self.data.lines_added_by_year.get(yy, 0), self.data.lines_removed_by_year.get(yy, 0)))
        f.write('</table></div>')
        f.write('<img src="commits_by_year.png" alt="Commits by Year">')
        fg = open(self.path + '/commits_by_year.dat', 'w')
        for yy in sorted(self.data.commits_by_year.keys()):
            fg.write('%d %d\n' % (yy, self.data.commits_by_year[yy]))
        fg.close()

        # Commits by timezone
        f.write(self.html_header(2, 'Commits by Timezone'))
        f.write('<table><tr>')
        f.write('<th>Timezone</th><th>Commits</th>')
        f.write('</tr>')
        max_commits_on_tz = max(self.data.commits_by_timezone.values())
        for i in sorted(list(self.data.commits_by_timezone.keys()), key=lambda n: int(n)):
            commits = self.data.commits_by_timezone[i]
            r = 127 + int((float(commits) / max_commits_on_tz) * 128)
            f.write('<tr><th>%s</th><td style="background-color: rgb(%d, 0, 0)">%d</td></tr>' % (i, r, commits))
        f.write('</table>')

        f.write('</body></html>')
        f.close()

    def _create_authors(self):
        f = open(self.path + '/authors.html', 'w')
        self.print_header(f)

        f.write('<h1>Authors</h1>')
        self.print_nav(f)

        # Authors :: List of authors
        f.write(self.html_header(2, 'List of Authors'))

        f.write('<table class="authors sortable" id="authors">')
        f.write(
            '<tr><th>Author</th><th>Commits (%)</th><th>+ lines</th><th>- lines</th><th>First commit</th><th>Last commit</th><th class="unsortable">Age</th><th>Active days</th><th># by commits</th></tr>')
        for author in self.data.get_authors(self.conf.max_authors):
            info = self.data.get_author_info(author)
            f.write(
                '<tr><td>%s</td><td>%d (%.2f%%)</td><td>%d</td><td>%d</td><td>%s</td><td>%s</td><td>%s</td><td>%d</td><td>%d</td></tr>' % (
                    author, info['commits'], info['commits_frac'], info['lines_added'], info['lines_removed'],
                    info['date_first'], info['date_last'], info['timedelta'], len(info['active_days']),
                    info['place_by_commits']))
        f.write('</table>')

        all_authors = self.data.get_authors()
        if len(all_authors) > self.conf.max_authors:
            rest = all_authors[self.conf.max_authors:]
            f.write('<p class="moreauthors">These didn\'t make it to the top: %s</p>' % ', '.join(rest))

        f.write(self.html_header(2, 'Cumulated Added Lines of Code per Author'))
        f.write('<img src="lines_of_code_by_author.png" alt="Lines of code per Author">')
        if len(all_authors) > self.conf.max_authors:
            f.write('<p class="moreauthors">Only top %d authors shown</p>' % self.conf.max_authors)

        f.write(self.html_header(2, 'Commits per Author'))
        f.write('<img src="commits_by_author.png" alt="Commits per Author">')
        if len(all_authors) > self.conf.max_authors:
            f.write('<p class="moreauthors">Only top %d authors shown</p>' % self.conf.max_authors)

        fgl = open(self.path + '/lines_of_code_by_author.dat', 'w')
        fgc = open(self.path + '/commits_by_author.dat', 'w')

        lines_by_authors = {}  # cumulated added lines by
        # author. to save memory,
        # changes_by_date_by_author[stamp][author] is defined
        # only at points where author commits.
        # lines_by_authors allows us to generate all the
        # points in the .dat file.

        # Don't rely on getAuthors to give the same order each
        # time. Be robust and keep the list in a variable.
        commits_by_authors = {}  # cumulated added lines by

        self.authors_to_plot = self.data.get_authors(self.conf.max_authors)
        for author in self.authors_to_plot:
            lines_by_authors[author] = 0
            commits_by_authors[author] = 0
        for stamp in sorted(self.data.changes_by_date_by_author.keys()):
            fgl.write('%d' % stamp)
            fgc.write('%d' % stamp)
            for author in self.authors_to_plot:
                if author in list(self.data.changes_by_date_by_author[stamp].keys()):
                    lines_by_authors[author] = self.data.changes_by_date_by_author[stamp][author]['lines_added']
                    commits_by_authors[author] = self.data.changes_by_date_by_author[stamp][author]['commits']
                fgl.write(' %d' % lines_by_authors[author])
                fgc.write(' %d' % commits_by_authors[author])
            fgl.write('\n')
            fgc.write('\n')
        fgl.close()
        fgc.close()

        # Authors :: Author of Month
        f.write(self.html_header(2, 'Author of Month'))
        f.write('<table class="sortable" id="aom">')
        f.write(
            '<tr><th>Month</th><th>Author</th><th>Commits (%%)</th><th class="unsortable">Next top %d</th><th>Number of authors</th></tr>' %
            self.conf.authors_top)
        for yy_mm in reversed(sorted(self.data.author_of_month.keys())):
            author_dict = self.data.author_of_month[yy_mm]
            authors = self.data.get_keys_sorted_by_values(author_dict)
            authors.reverse()
            commits = self.data.author_of_month[yy_mm][authors[0]]
            next_line = ', '.join(authors[1:self.conf.authors_top + 1])
            f.write('<tr><td>%s</td><td>%s</td><td>%d (%.2f%% of %d)</td><td>%s</td><td>%d</td></tr>' % (
                yy_mm, authors[0], commits, (100.0 * commits) / self.data.commits_by_month[yy_mm],
                self.data.commits_by_month[yy_mm],
                next_line, len(authors)))

        f.write('</table>')

        f.write(self.html_header(2, 'Author of Year'))
        f.write(
            '<table class="sortable" id="aoy"><tr><th>Year</th><th>Author</th><th>Commits (%%)</th><th class="unsortable">Next top %d</th><th>Number of authors</th></tr>' %
            self.conf.authors_top)
        for yy in reversed(sorted(self.data.author_of_year.keys())):
            author_dict = self.data.author_of_year[yy]
            authors = self.data.get_keys_sorted_by_values(author_dict)
            authors.reverse()
            commits = self.data.author_of_year[yy][authors[0]]
            next_line = ', '.join(authors[1:self.conf.authors_top + 1])
            f.write('<tr><td>%s</td><td>%s</td><td>%d (%.2f%% of %d)</td><td>%s</td><td>%d</td></tr>' % (
                yy, authors[0], commits, (100.0 * commits) / self.data.commits_by_year[yy], self.data.commits_by_year[yy],
                next_line,
                len(authors)))
        f.write('</table>')

        # Domains
        f.write(self.html_header(2, 'Commits by Domains'))
        domains_by_commits = self.data.get_keys_sorted_by_value_key(self.data.domains, 'commits')
        domains_by_commits.reverse()  # most first
        f.write('<div class="vtable"><table>')
        f.write('<tr><th>Domains</th><th>Total (%)</th></tr>')
        fp = open(self.path + '/domains.dat', 'w')
        n = 0
        for domain in domains_by_commits:
            if n == self.conf.max_domains:
                break
            n += 1
            info = self.data.get_domain_info(domain)
            fp.write('%s %d %d\n' % (domain, n, info['commits']))
            f.write('<tr><th>%s</th><td>%d (%.2f%%)</td></tr>' % (
                domain, info['commits'], (100.0 * info['commits'] / self.data.get_total_commits())))
        f.write('</table></div>')
        f.write('<img src="domains.png" alt="Commits by Domains">')
        fp.close()

        f.write('</body></html>')
        f.close()

    def _create_files(self):
        f = open(self.path + '/files.html', 'w')
        self.print_header(f)
        f.write('<h1>Files</h1>')
        self.print_nav(f)

        f.write('<dl>\n')
        f.write('<dt>Total files</dt><dd>%d</dd>' % self.data.get_total_files())
        f.write('<dt>Total lines</dt><dd>%d</dd>' % self.data.get_total_loc())
        try:
            f.write(
                '<dt>Average file size</dt><dd>%.2f bytes</dd>' % (
                    float(self.data.get_total_size()) / self.data.get_total_files()))
        except ZeroDivisionError:
            pass
        f.write('</dl>\n')

        # Files :: File count by date
        f.write(self.html_header(2, 'File count by date'))

        # use set to get rid of duplicate/unnecessary entries
        files_by_date = set()
        for stamp in sorted(self.data.files_by_stamp.keys()):
            files_by_date.add('%s %d' % (
                datetime.datetime.fromtimestamp(stamp).strftime(self.conf.date_format), self.data.files_by_stamp[stamp]))

        fg = open(self.path + '/files_by_date.dat', 'w')
        for line in sorted(list(files_by_date)):
            fg.write('%s\n' % line)
        # for stamp in sorted(self.data.files_by_stamp.keys()):
        #    fg.write('%s %d\n' % (datetime.datetime.fromtimestamp(stamp).strftime(self.conf.date_format']), self.data.files_by_stamp[stamp]))
        fg.close()

        f.write('<img src="files_by_date.png" alt="Files by Date">')

        # f.write('<h2>Average file size by date</h2>')

        # Files :: Extensions
        f.write(self.html_header(2, 'Extensions'))
        f.write(
            '<table class="sortable" id="ext"><tr><th>Extension</th><th>Files (%)</th><th>Lines (%)</th><th>Lines/file</th></tr>')
        for ext in sorted(self.data.extensions.keys()):
            files = self.data.extensions[ext]['files']
            lines = self.data.extensions[ext]['lines']
            try:
                loc_percentage = (100.0 * lines) / self.data.get_total_loc()
            except ZeroDivisionError:
                loc_percentage = 0
            f.write('<tr><td>%s</td><td>%d (%.2f%%)</td><td>%d (%.2f%%)</td><td>%d</td></tr>' % (
                ext, files, (100.0 * files) / self.data.get_total_files(), lines, loc_percentage, lines / files))
        f.write('</table>')

        f.write('</body></html>')
        f.close()

    def _create_lines(self):
        f = open(self.path + '/lines.html', 'w')
        self.print_header(f)
        f.write('<h1>Lines</h1>')
        self.print_nav(f)

        f.write('<dl>\n')
        f.write('<dt>Total lines</dt><dd>%d</dd>' % self.data.get_total_loc())
        f.write('</dl>\n')

        f.write(self.html_header(2, 'Lines of Code'))
        f.write('<img src="lines_of_code.png" alt="Lines of Code">')

        fg = open(self.path + '/lines_of_code.dat', 'w')
        for stamp in sorted(self.data.changes_by_date.keys()):
            fg.write('%d %d\n' % (stamp, self.data.changes_by_date[stamp]['lines']))
        fg.close()

        f.write('</body></html>')
        f.close()

    def _create_tags(self):
        f = open(self.path + '/tags.html', 'w')
        self.print_header(f)
        f.write('<h1>Tags</h1>')
        self.print_nav(f)

        f.write('<dl>')
        f.write('<dt>Total tags</dt><dd>%d</dd>' % len(self.data.tags))
        if len(self.data.tags) > 0:
            f.write('<dt>Average commits per tag</dt><dd>%.2f</dd>' % (1.0 * self.data.get_total_commits() / len(self.data.tags)))
        f.write('</dl>')

        f.write('<table class="tags">')
        f.write('<tr><th>Name</th><th>Date</th><th>Commits</th><th>Authors</th></tr>')
        # sort the tags by date desc
        tags_sorted_by_date_desc = [el[1] for el in
                                    reversed(sorted([(el[1]['date'], el[0]) for el in list(self.data.tags.items())]))]
        for tag in tags_sorted_by_date_desc:
            author_info = []
            self.authors_by_commits = self.data.get_keys_sorted_by_values(self.data.tags[tag]['authors'])
            for i in reversed(self.authors_by_commits):
                author_info.append('%s (%d)' % (i, self.data.tags[tag]['authors'][i]))
            f.write('<tr><td>%s</td><td>%s</td><td>%d</td><td>%s</td></tr>' % (
                tag, self.data.tags[tag]['date'], self.data.tags[tag]['commits'], ', '.join(author_info)))
        f.write('</table>')

        f.write('</body></html>')
        f.close()

    def run(self):
        # copy static files. Looks in the binary directory, ../share/gitstats and /usr/share/gitstats
        binary_path = os.path.dirname(os.path.abspath(__file__))
        secondary_path = os.path.join(binary_path, '..', 'share', 'gitstats')
        basedirs = [binary_path, secondary_path, '/usr/share/gitstats']
        for file in (self.conf.style, 'sortable.js', 'arrow-up.gif', 'arrow-down.gif', 'arrow-none.gif'):
            for base in basedirs:
                src = base + '/' + file
                if os.path.exists(src):
                    shutil.copyfile(src, self.path + '/' + file)
                    break
            else:
                print('Warning: "%s" not found, so not copied (searched: %s)' % (file, basedirs))

        # Index
        self._create_index()

        # Activity
        self._create_activity()

        # Authors
        self._create_authors()

        # Files
        self._create_files()

        # Lines
        self._create_lines()

        # tags.html
        self._create_tags()

        # Images
        self.create_graphs()

    def create_graphs(self):
        print('Generating graphs...')

        # hour of day
        plot = "'hour_of_day.dat' using 1:2:(0.5) w boxes fs solid"
        plot_file = PlotFileCreator(self.conf, self.path + '/hour_of_day.plot', 'hour_of_day.png', plot)
        plot_file.ylabel = 'Commits'
        plot_file.yrange = "[0:]"
        plot_file.xrange = "[0.5:24.5]"
        plot_file.xtics = "4"
        plot_file.xtics_rotate = False
        plot_file.create()

        # day of week
        plot = "'day_of_week.dat' using 1:3:(0.5):xtic(2) w boxes fs solid"
        plot_file = PlotFileCreator(self.conf, self.path + '/day_of_week.plot', 'day_of_week.png', plot)
        plot_file.ylabel = 'Commits'
        plot_file.yrange = "[0:]"
        plot_file.xrange = "[0.5:7.5]"
        plot_file.xtics = "1"
        plot_file.xtics_rotate = False
        plot_file.create()

        # Domains
        plot = "'domains.dat' using 2:3:(0.5) with boxes fs solid, '' using 2:3:1 with labels rotate by 45 offset 0,1"
        plot_file = PlotFileCreator(self.conf, self.path + '/domains.plot', 'domains.png', plot)
        plot_file.ylabel = 'Commits'
        plot_file.xtics_rotate = False
        plot_file.create()

        # Month of Year
        plot = "'month_of_year.dat' using 1:2:(0.5) w boxes fs solid"
        plot_file = PlotFileCreator(self.conf, self.path + '/month_of_year.plot', 'month_of_year.png', plot)
        plot_file.ylabel = 'Commits'
        plot_file.yrange = "[0:]"
        plot_file.xrange = "[0.5:12.5]"
        plot_file.xtics = "1"
        plot_file.xtics_rotate = False
        plot_file.create()

        # commits_by_year_month
        plot = "'commits_by_year_month.dat' using 1:2:(0.5) w boxes fs solid"
        plot_file = PlotFileCreator(self.conf, self.path + '/commits_by_year_month.plot', 'commits_by_year_month.png', plot)
        plot_file.set_time("%Y-%m")
        plot_file.ylabel = 'Commits'
        plot_file.create()

        # commits_by_year
        plot = "'commits_by_year.dat' using 1:2:(0.5) w boxes fs solid"
        plot_file = PlotFileCreator(self.conf, self.path + '/commits_by_year.plot', 'commits_by_year.png', plot)
        plot_file.set_time_from_string()
        plot_file.ylabel = 'Commits'
        plot_file.xtics = "1"
        plot_file.create()

        # Files by date
        plot = "'files_by_date.dat' using 1:2 w steps"
        plot_file = PlotFileCreator(self.conf, self.path + '/files_by_date.plot', 'files_by_date.png', plot)
        plot_file.set_time_from_string()
        plot_file.ylabel = "Lines"
        plot_file.additional = "set ytics autofreq"
        plot_file.create()

        # Lines of Code
        plot = "'lines_of_code.dat' using 1:2 w lines"
        plot_file = PlotFileCreator(self.conf, self.path + '/lines_of_code.plot', 'lines_of_code.png', plot)
        plot_file.set_time_from_string()
        plot_file.ylabel = "Lines"
        plot_file.create()

        # Lines of Code Added per author
        i = 1
        plots = []
        for a in self.authors_to_plot:
            i += 1
            author = a.replace("\"", "\\\"").replace("`", "")
            plots.append("""'lines_of_code_by_author.dat' using 1:%d title "%s" w lines""" % (i, author))
        plots = ", ".join(plots)
        plot_file = PlotFileCreator(self.conf, self.path + '/lines_of_code_by_author.plot', 'lines_of_code_by_author.png',
                                    plots)
        plot_file.ylabel = "Lines"
        plot_file.key = "set key left top"
        plot_file.set_time_from_string()
        plot_file.create()

        # Commits per author
        i = 1
        plots = []
        for a in self.authors_to_plot:
            i += 1
            author = a.replace("\"", "\\\"").replace("`", "")
            plots.append("""'commits_by_author.dat' using 1:%d title "%s" w lines""" % (i, author))
        plots = ", ".join(plots)
        plot_file = PlotFileCreator(self.conf, self.path + '/commits_by_author.plot', 'commits_by_author.png', plots)
        plot_file.ylabel = "Commits"
        plot_file.key = "set key left top"
        plot_file.set_time_from_string()
        plot_file.create()

        os.chdir(self.path)
        files = glob.glob(self.path + '/*.plot')
        for f in files:
            out = RunExternal.execute([self.conf.gnuplot_cmd + ' "%s"' % f])
            if len(out) > 0:
                print(out)

    def print_header(self, f):
        f.write(
            """<!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>GitStats - %s</title>
                <link rel="stylesheet" href="%s" type="text/css">
                <meta name="generator" content="GitStats %s">
                <script type="text/javascript" src="sortable.js"></script>
            </head>
            <body>
            """ % (self.title, self.conf.style, self.get_version()))
