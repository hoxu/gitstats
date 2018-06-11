import getopt
import logging
import os
import sys

from datetime import datetime, timezone

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
    'end_date': '',
    'logging': logging.INFO,
    'resrouce_file_pattern': '**/resources/**/*',
}


def _usage():
    print(f"""
Usage: gitstats [options] <gitpath..> <outputpath>

Options:
-c key=value     Override configuration value

Default config values:
{conf}

Please see the manual page for more details.
""")


def get_cli():
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
            _usage()
            sys.exit()

    if len(args) < 2:
        _usage()
        sys.exit(0)

    outputpath = os.path.abspath(args[-1])
    paths = args[0:-1]
    outputpath = os.path.abspath(outputpath)

    return conf, paths, outputpath

def get_begin_end_timestamps(conf):
    if 'start_date' in conf and conf['start_date']:
        begin = int(datetime.strptime(conf['start_date'], '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp())
    else:
        begin = 0
    if 'end_date' in conf and conf['end_date']:
        end = int(datetime.strptime(conf['end_date'], '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp())
    else:
        end = 99999999999
    return begin, end