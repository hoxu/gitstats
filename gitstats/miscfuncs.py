import logging
import subprocess
import time

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
