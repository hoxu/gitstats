import os
import platform
import re
import subprocess
import sys
import time

os.environ['LC_ALL'] = 'C'

ON_LINUX = (platform.system() == 'Linux')

# By default, gnuplot is searched from path, but can be overridden with the
# environment variable "GNUPLOT"
gnuplot_cmd = 'gnuplot'
if 'GNUPLOT' in os.environ:
    gnuplot_cmd = os.environ['GNUPLOT']


def getpipeoutput(cmds, quiet=False):
    start = time.time()
    if not quiet and ON_LINUX and os.isatty(1):
        print('>> ' + ' | '.join(cmds), sys.stdout.flush())
    p = subprocess.Popen(cmds[0], stdout=subprocess.PIPE, shell=True)
    processes = [p]
    for x in cmds[1:]:
        p = subprocess.Popen(x, stdin=p.stdout, stdout=subprocess.PIPE, shell=True)
        processes.append(p)
    output = p.communicate()[0].decode('utf-8')
    for p in processes:
        p.wait()
    end = time.time()
    if not quiet:
        if ON_LINUX and os.isatty(1):
            print(f'\r[{end - start}] >> {" | ".join(cmds)}')
    return output.rstrip('\n')


def getlogrange(conf, defaultrange='HEAD', end_only=True):
    commit_range = getcommitrange(conf, defaultrange, end_only)
    if len(conf['start_date']) > 0:
        return '--since="%s" "%s"' % (conf['start_date'], commit_range)
    return commit_range


def getcommitrange(conf, defaultrange='HEAD', end_only=False):
    if len(conf['commit_end']) > 0:
        if end_only or len(conf['commit_begin']) == 0:
            return conf['commit_end']
        return '%s..%s' % (conf['commit_begin'], conf['commit_end'])
    return defaultrange


def getkeyssortedbyvalues(dictionary):
    return [elem[1] for elem in sorted([(el[1], el[0]) for el in dictionary.items()])]


# dict['author'] = { 'commits': 512 } - ...key(dict, 'commits')
def getkeyssortedbyvaluekey(d, key):
    return [elem[1] for elem in sorted([(d[el][key], el) for el in d.keys()])]


def getstatsummarycounts(line):
    numbers = re.findall('\d+', line)
    if len(numbers) == 1:
        # neither insertions nor deletions: may probably only happen for "0 files changed"
        numbers.append(0)
        numbers.append(0)
    elif len(numbers) == 2 and line.find('(+)') != -1:
        numbers.append(0)  # only insertions were printed on line
    elif len(numbers) == 2 and line.find('(-)') != -1:
        numbers.insert(1, 0)  # only deletions were printed on line
    return numbers


def getversion():
    from ._version import get_versions
    __version__ = get_versions()['version']
    del get_versions
    return __version__


def getgitversion():
    return getpipeoutput(['git --version']).split('\n')[0]


def getgnuplotversion():
    return getpipeoutput(['%s --version' % gnuplot_cmd]).split('\n')[0]


def getnumoffilesfromrev(time_rev):
    """
    Get number of files changed in commit
    """
    time_portion, rev = time_rev
    return (int(time_portion), rev, int(getpipeoutput(['git ls-tree -r --name-only "%s"' % rev, 'wc -l']).split('\n')[0]))


def getnumoflinesinblob(ext_blob):
    """
    Get number of lines in blob
    """
    ext, blob_id = ext_blob
    return ext, blob_id, int(getpipeoutput(['git cat-file blob %s' % blob_id, 'wc -l']).split()[0])


