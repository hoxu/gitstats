#!/usr/bin/python
# Copyright (c) 2007-2014 Heikki Hokkanen <hoxu@users.sf.net> & others (see doc/AUTHOR)
# GPLv2 / GPLv3
import getopt
import logging
import os
import sys
import time

import multiprocessing_logging

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
    'start_date': '',
    'logging': logging.INFO,
    'name_xlate': {
        'lmonson': 'Lynn Monson',
        'DallanQ': 'Dallan Quass',
        'Daniel Rapp': 'Dan Rapp'
    }
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
        optlist, args = getopt.getopt(sys.argv[1:], 'hc:', ["help"])
        for o, v in optlist:
            if o == '-c':
                key, value = v.split('=', 1)
                if key not in conf:
                    raise KeyError('no such key "%s" in config' % key)
                if isinstance(conf[key], int):
                    conf[key] = int(value)
                else:
                    conf[key] = value
            elif o in ('-h', '--help'):
                self._usage()
                sys.exit()

        if len(args) < 2:
            self._usage()
            sys.exit(0)

        outputpath = os.path.abspath(args[-1])
        paths = args[0:-1]
        outputpath = os.path.abspath(outputpath)

        logging.basicConfig(level=conf['logging'], format='%(message)s')
        multiprocessing_logging.install_mp_handler()
        time_start = time.time()


        rundir = os.getcwd()

        try:
            os.makedirs(outputpath)
        except OSError:
            pass
        if not os.path.isdir(outputpath):
            logging.fatal('Output path is not a directory or does not exist')
            sys.exit(1)

        if not getgnuplotversion():
            logging.error('gnuplot not found')
            sys.exit(1)

        logging.info(f'Output path: {outputpath}')
        cachefile = os.path.join(outputpath, 'gitstats.cache')

        data = GitDataCollector(conf)
        data.loadCache(cachefile)

        for gitpath in paths:
            logging.info(f'Git path: {gitpath}')

            prevdir = os.getcwd()
            os.chdir(gitpath)

            logging.info('Collecting data...')
            data.collect(gitpath)

            os.chdir(prevdir)

        data.saveCache(cachefile)

        logging.info('Refining data...')
        data.refine()

        os.chdir(rundir)

        logging.info('Generating report...')
        report = HTMLReportCreator(conf)
        report.create(data, outputpath)

        time_end = time.time()
        calculated_exectime_internal = time_end - time_start
        logging.info(f'Execution time {calculated_exectime_internal} secs, {exectime_external} secs ({(100.0 * exectime_external) / calculated_exectime_internal}%) in external commands)')

        print('You may now run:')
        print()
        print('   sensible-browser \'%s\'' % os.path.join(outputpath, 'index.html').replace("'", "'\\''"))
        print()


if __name__ == '__main__':
    g = GitStats()
    g.run()
