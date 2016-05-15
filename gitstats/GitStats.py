#!/usr/bin/env python3
# Copyright (c) 2007-2014 Heikki Hokkanen <hoxu@users.sf.net> & others (see doc/AUTHOR)
# GPLv2 / GPLv3
import argparse
import os
import pickle
import sys
import time
import zlib

from gitstats.Configuration import Configuration
from gitstats.RunExternal import RunExternal
from gitstats.collector.Data import Data
from gitstats.collector.DataCollector import DataCollector
from gitstats.reporter.HTMLReportCreator import HTMLReportCreator


class GitStats(object):
    @staticmethod
    def _create_output_dir(path):
        try:
            os.makedirs(path)
        except OSError:
            pass
        if not os.path.isdir(path):
            print('FATAL: Output path %s is not a directory or does not exist' % path)
            sys.exit(1)
        print('Output path: %s' % path)

    def __init__(self):
        self.exec_time_internal = 0.0
        self.time_start = time.time()
        self.conf = Configuration()
        self.data = Data()
        self.collector = DataCollector(self.data, self.conf)
        self.cache = {}

    def _usage(self):
        print("""
    Usage: gitstats [options] <gitpath..> <outputpath>

    Options:
    -c config_file     Override configuration value

    Default config values:
%s

    Please see the manual page for more details.
    """ % self.conf)

    def _collect_data(self, path):
        print('Git path: %s' % path)

        prev_dir = os.getcwd()
        os.chdir(path)

        print('Collecting data...')
        self.collector.collect()

        os.chdir(prev_dir)

    def _generate_report(self, conf, output_path):
        print('Generating report...')
        report = HTMLReportCreator(conf, self.data, output_path)
        report.run()

    ##
    # Load cacheable data
    def load_cache(self, cache_file):
        if not os.path.exists(cache_file):
            return
        print('Loading cache...')
        f = open(cache_file, 'rb')
        try:
            self.cache = pickle.loads(zlib.decompress(f.read()))
        except pickle.PickleError:
            # temporary hack to upgrade non-compressed caches
            f.seek(0)
            self.cache = pickle.load(f)
        f.close()

    ##
    # Save cacheable data
    def save_cache(self, cache_file):
        print('Saving cache...')
        temp_file = cache_file + '.tmp'
        f = open(temp_file, 'wb')
        # pickle.dump(self.cache, f)
        data = zlib.compress(pickle.dumps(self.cache))
        f.write(data)
        f.close()
        try:
            os.remove(cache_file)
        except OSError:
            pass
        os.rename(temp_file, cache_file)

    def run(self):
        if len(sys.argv) < 2:
            self._usage()
            sys.exit(0)

        parser = argparse.ArgumentParser(description='GitStats')
        parser.add_argument('-c', '--config', dest='config')

        (args, remaining_args) = parser.parse_known_args()
        if args.config:
            self.conf.load(args.config)

        # By default, gnuplot is searched from path, but can be overridden with the
        # environment variable "GNUPLOT"
        if 'GNUPLOT' in os.environ:
            self.conf.gnuplot_cmd = os.environ['GNUPLOT']

        output_path = remaining_args[-1]
        paths = remaining_args[0:-1]
        output_path = os.path.abspath(output_path)

        self._create_output_dir(output_path)

        # if not getgnuplotversion():
        #    print 'gnuplot not found'
        #    sys.exit(1)

        cachefile = os.path.join(output_path, 'gitstats.cache')

        self.data.project_name = self.conf.project_name

        self.load_cache(cachefile)
        self.data.cache = self.cache

        for gitpath in paths:
            self._collect_data(gitpath)

        self.save_cache(cachefile)

        self._generate_report(self.conf, output_path)

        time_end = time.time()
        exec_time_internal = time_end - self.time_start
        print('Execution time %.5f secs, %.5f secs (%.2f %%) in external commands)' % (
            exec_time_internal, RunExternal.exec_time_external,
            (100.0 * RunExternal.exec_time_external) / exec_time_internal))
        if sys.stdin.isatty():
            print('You may now run:')
            print()
            print('   sensible-browser \'%s\'' % os.path.join(output_path, 'index.html').replace("'", "'\\''"))
            print()


if __name__ == '__main__':
    g = GitStats()
    g.run()
