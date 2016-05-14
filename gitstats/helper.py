import os
import platform
import subprocess
import sys
import time

# By default, gnuplot is searched from path, but can be overridden with the
# environment variable "GNUPLOT"
gnuplot_cmd = 'gnuplot'
if 'GNUPLOT' in os.environ:
    gnuplot_cmd = os.environ['GNUPLOT']


def is_linux():
    return platform.system() == 'Linux'




def getpipeoutput(cmds, quiet=False):
    start = time.time()
    if not quiet and is_linux() and os.isatty(1):
        print('>> ' + ' | '.join(cmds), end=' ')
        sys.stdout.flush()
    p = subprocess.Popen(cmds[0], stdout=subprocess.PIPE, shell=True)
    processes = [p]
    for x in cmds[1:]:
        p = subprocess.Popen(x, stdin=p.stdout, stdout=subprocess.PIPE, shell=True)
        processes.append(p)
    output = p.communicate()[0].decode()
    for p in processes:
        p.wait()
    end = time.time()
    if not quiet:
        if is_linux() and os.isatty(1):
            print('\r', end=' ')
        print('[%.5f] >> %s' % (end - start, ' | '.join(cmds)))
    # exectime_external += (end - start)
    return output.rstrip('\n')
