import datetime
import logging
import os
import re
import subprocess
import time

os.environ['LC_ALL'] = 'C'

# By default, gnuplot is searched from path, but can be overridden with the
# environment variable "GNUPLOT"
gnuplot_cmd = 'gnuplot'
if 'GNUPLOT' in os.environ:
    gnuplot_cmd = os.environ['GNUPLOT']


def getpipeoutput(cmds):
    start = time.time()
    p = subprocess.Popen(cmds[0], stdout=subprocess.PIPE, shell=True)
    processes = [p]
    for x in cmds[1:]:
        p = subprocess.Popen(x, stdin=p.stdout, stdout=subprocess.PIPE, shell=True)
        processes.append(p)
    output = p.communicate()[0].decode('utf-8')
    for p in processes:
        p.wait()
    end = time.time()
    logging.info(f'\r[{end - start:.4f}] >> {" | ".join(cmds)}')
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


def getnumoffilesfromrev(tree_hash):
    """
    Get number of files changed in commit
    """
    # DBG: git ls-tree -r --name-only "ceb3165b51ae0680724fd71e16a5ff836a0de41e"' | 'wc -l'
    return (tree_hash, int(getpipeoutput(['git ls-tree -r --name-only "%s"' % tree_hash, 'wc -l']).split('\n')[0]))


def getnumoflinesinblob(blob_id):
    """
    Get number of lines in blob
    """

    # DBG: git cat-file blob e4f17a621893811250be96c8ef9c37b5e97a1df7', 'wc -l'
    return blob_id, int(getpipeoutput(['git cat-file blob %s' % blob_id, 'wc -l']).split()[0])

def gettimedelta(sha_tuple):
    """
    Get the time delta between the time stamp passed in the tuple ([1]) and the sha of the second rev in the tuple ([2])
    return the result, keyed by the sha of the first rev in the tuple ([0])
    """
    # DBG:  git log -n 1 --format=%at "ceb3165b51ae0680724fd71e16a5ff836a0de41e"'
    timestamp_branch = int(getpipeoutput([' git log -n 1 --format=%%at "%s"' % sha_tuple[2]]).split('\n')[0])
    delta = datetime.datetime.utcfromtimestamp(sha_tuple[1]) - datetime.datetime.utcfromtimestamp(timestamp_branch)

    return (sha_tuple[0], delta)


