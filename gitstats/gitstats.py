#!/usr/bin/python
# Copyright (c) 2007-2014 Heikki Hokkanen <hoxu@users.sf.net> & others (see doc/AUTHOR)
# GPLv2 / GPLv3
import argparse
import os
import sys
import time

from .gitdatacollector import GitDataCollector
from .htmlreportcreator import HTMLReportCreator
from .miscfuncs import getgnuplotversion

exectime_internal = 0.0
exectime_external = 0.0

conf = {
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
    'start_date': ''
}

class GitStats:
    def _usage(self):
        print(f"""
    Usage: gitstats [options] <gitpath..> <outputpath>

    Options:
    -c key=value     Override configuration value

    Default config values:
    {conf}

    Please see the manual page for more details.
    """)

    def run(self):
        if len(sys.argv) < 2:
            self._usage()
            sys.exit(0)

        parser = argparse.ArgumentParser(description='GitStats')
#        parser.add_argument('-c', '--config', dest='config')

        (args, remaining_args) = parser.parse_known_args()
#        if args.config:
#            self.conf.load(args.config)

        time_start = time.time()

        outputpath = remaining_args[-1]
        paths = remaining_args[0:-1]
        outputpath = os.path.abspath(outputpath)

        rundir = os.getcwd()

        try:
            os.makedirs(outputpath)
        except OSError:
            pass
        if not os.path.isdir(outputpath):
            print('FATAL: Output path is not a directory or does not exist')
            sys.exit(1)

        if not getgnuplotversion():
            print('gnuplot not found')
            sys.exit(1)

        print(f'Output path: {outputpath}')
        cachefile = os.path.join(outputpath, 'gitstats.cache')

        data = GitDataCollector(conf)
        data.loadCache(cachefile)

        for gitpath in paths:
            print(f'Git path: {gitpath}')

            prevdir = os.getcwd()
            os.chdir(gitpath)

            print('Collecting data...')
            data.collect(gitpath)

            os.chdir(prevdir)

        print('Refining data...')
        data.saveCache(cachefile)
        data.refine()

        os.chdir(rundir)

        print('Generating report...')
        report = HTMLReportCreator(conf)
        report.create(data, outputpath)

        time_end = time.time()
        calculated_exectime_internal = time_end - time_start
        print(
            f'Execution time {calculated_exectime_internal} secs, {exectime_external} secs ({(100.0 * exectime_external) / calculated_exectime_internal}%) in external commands)')
        if sys.stdin.isatty():
            print('You may now run:')
            print()
            print('   sensible-browser \'%s\'' % os.path.join(outputpath, 'index.html').replace("'", "'\\''"))
            print()


if __name__ == '__main__':
    g = GitStats()
    g.run()
