import csv
import os
import re

from multiprocessing import Pool

from gitstats import cli, cd
from gitstats.miscfuncs import getcommitrange, getpipeoutput, getnumoflinesinblob
from gitstats.data import File


def gen_file_data(conf, row_processor):
    '''
    Given a configuration, pull authorship information. For
    each author, callback to the row_processor passing an AuthorRow

    :param conf: configuration (mostly used for date limits)
    :param row_processor: function to receive the callback
    :return: None
    '''

    # extensions and size of files

    # DBG: git ls-tree -r -l -z HEAD
    lines = getpipeoutput(['git ls-tree -r -l -z %s' % getcommitrange(conf, 'HEAD', end_only=True)]).split(
        '\000')
    blobs_to_read = {} # blob_id -> File
    for line in lines:
        if len(line) == 0:
            continue
        parts = re.split('\s+', line, 4)
        if parts[0] == '160000' and parts[3] == '-':
            # skip submodules
            continue
        blob_id = parts[2]
        size = int(parts[3])
        fullpath = parts[4]
        _, ext = os.path.splitext(fullpath)
        blobs_to_read[blob_id] = File(fullpath, ext, size)

    # DBG: git cat-file blob e4f17a621893811250be96c8ef9c37b5e97a1df7', 'wc -l'
    pool = Pool(processes=conf['processes'])
    blob_linecount = pool.map(getnumoflinesinblob, blobs_to_read.keys())
    pool.terminate()
    pool.join()
    # Update cache and write down info about number of number of lines
    for (blob_id, linecount) in blob_linecount:
        file_data = blobs_to_read[blob_id]
        file_data.lines = linecount
        row_processor(file_data)


if __name__ == "__main__":
    conf, paths, outputpath = cli.get_cli()
    with open(outputpath, 'w', encoding='utf8') as f:
        writer = csv.writer(f)
        writer.writerow(['repo', 'file', 'ext', 'size', 'line_count'])

        for path in paths:
            repo_name = os.path.split(path)[1]
            with (cd.cd(path)):

                gen_file_data(
                    conf,
                    lambda row: writer.writerow([repo_name, row.full_path, row.ext, row.size, row.lines]))
