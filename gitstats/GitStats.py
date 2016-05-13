#!/usr/bin/env python3
# Copyright (c) 2007-2014 Heikki Hokkanen <hoxu@users.sf.net> & others (see doc/AUTHOR)
# GPLv2 / GPLv3
import getopt
import os
import sys

from collector.GitDataCollector import GitDataCollector
from reporter.HTMLReportCreator import HTMLReportCreator

# exectime_internal = 0.0
# exectime_external = 0.0
# time_start = time.time()

class GitStats:
    def __init__(self):
        self.conf = {
            'max_domains': 10,
            'max_ext_length': 10,
            'style': 'gitstats.css',
            'max_authors': 20,
            'authors_top': 5,
            'commit_begin': '',
            'commit_end': 'HEAD',
            'linear_linestats': 1,
            'project_name': '',
            'processes': 8,
            'start_date': '',
            'image_resolution': '1280,640',
            'date_format': '%Y-%m-%d',
            'authors_merge': '{}'
        }
        self.data = None

    def _usage(self):
        print("""
    Usage: gitstats [options] <gitpath..> <outputpath>

    Options:
    -c key=value     Override configuration value

    Default config values:
    %s

    Please see the manual page for more details.
    """ % self.conf)

    def _create_outputdir(self, path):
        try:
            os.makedirs(path)
        except OSError:
            pass
        if not os.path.isdir(path):
            print('FATAL: Output path %s is not a directory or does not exist' % path)
            sys.exit(1)
        print('Output path: %s' % path)

    def _collect_data(self, path):
        print('Git path: %s' % path)

        prevdir = os.getcwd()
        os.chdir(path)

        print('Collecting data...')
        self.data.collect(path, self.conf['project_name'])

        os.chdir(prevdir)

    def _refine_data(self, cachefile):
        print('Refining data...')
        self.data.saveCache(cachefile)
        self.data.refine()

    def _generate_report(self, conf, outputpath):
        print('Generating report...')
        report = HTMLReportCreator(conf)
        report.create(self.data, outputpath)

    def parse_args(self):
        if len(sys.argv) < 2:
            self._usage()
            sys.exit(0)

        optlist, args = getopt.getopt(sys.argv[1:], 'hc:', ["help"])
        for o, v in optlist:
            if o == '-c':
                key, value = v.split('=', 1)
                if key not in self.conf:
                    raise KeyError('no such key "%s" in config' % key)
                if isinstance(self.conf[key], int):
                    self.conf[key] = int(value)
                else:
                    self.conf[key] = value
            elif o in ('-h', '--help'):
                self._usage()
                sys.exit()
        self.conf['authors_merge'] = eval(self.conf['authors_merge'])
        return args[-1], args[0:-1]

    def run(self):
        (outputpath, paths) = self.parse_args()
        outputpath = os.path.abspath(outputpath)

        self._create_outputdir(outputpath)

        # if not getgnuplotversion():
        #    print 'gnuplot not found'
        #    sys.exit(1)

        cachefile = os.path.join(outputpath, 'gitstats.cache')

        self.data = GitDataCollector(self.conf)
        self.data.loadCache(cachefile)

        for gitpath in paths:
            self._collect_data(gitpath)

        self._refine_data(cachefile)

        self._generate_report(self.conf, outputpath)

        # time_end = time.time()
        # exectime_internal = time_end - time_start
        # print 'Execution time %.5f secs, %.5f secs (%.2f %%) in external commands)' % (exectime_internal, exectime_external, (100.0 * exectime_external) / exectime_internal)
        if sys.stdin.isatty():
            print('You may now run:')
            print()
            print('   sensible-browser \'%s\'' % os.path.join(outputpath, 'index.html').replace("'", "'\\''"))
            print()


if __name__ == '__main__':

    g = GitStats()
    g.run()
