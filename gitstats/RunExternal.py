import os
import platform
import subprocess
import sys
import time


class RunExternal(object):
    exectime_external = 0.0

    @staticmethod
    def is_linux():
        return platform.system() == 'Linux'

    @staticmethod
    def execute(cmds, quiet=False):
        start = time.time()
        if not quiet and RunExternal.is_linux() and os.isatty(1):
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
            if RunExternal.is_linux() and os.isatty(1):
                print('\r', end=' ')
            print('[%.5f] >> %s' % (end - start, ' | '.join(cmds)))
        RunExternal.exectime_external += (end - start)
        return output.rstrip('\n')
