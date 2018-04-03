#!/usr/bin/python
# Copyright (c) 2007-2014 Heikki Hokkanen <hoxu@users.sf.net> & others (see doc/AUTHOR)
# GPLv2 / GPLv3
import logging
import os
import sys
import time

import multiprocessing_logging

from gitstats.gitdatacollector import GitDataCollector
from gitstats.htmlreportcreator import HTMLReportCreator
from gitstats.miscfuncs import getgnuplotversion
from gitstats import cli

exectime_internal = 0.0
exectime_external = 0.0

def run():

    conf, paths, outputpath = cli.get_cli()

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
    run()
