import csv
import logging
import os
import re

from gitstats import cli, cd
from gitstats.miscfuncs import getlogrange, getpipeoutput, getstatsummarycounts
from gitstats.data import LocByDate


def gen_loc_data(conf, row_processor):
    '''
    Given a configuration, pull authorship information. For
    each author, callback to the row_processor passing an AuthorRow

    :param conf: configuration (mostly used for date limits)
    :param row_processor: function to receive the callback
    :return: total lines in repo
    '''

    # line statistics
    # outputs:
    #  N files changed, N insertions (+), N deletions(-)

    # computation of lines of code by date is better done
    # on a linear history.
    extra = ''
    if conf['linear_linestats']:
        extra = '--first-parent -m'

    # DBG: git log --shortstat --first-parent -m --pretty=format:"%at %aN" --since="2017-10-01" "HEAD"'
    lines = getpipeoutput(
        ['git log --shortstat %s --pretty=format:"%%H %%at %%aN" %s' % (extra, getlogrange(conf, 'HEAD'))]).split('\n')
    lines.reverse()
    files = 0
    inserted = 0
    deleted = 0
    total_lines = 0
    for line in lines:
        if len(line) == 0:
            continue

        if re.search('files? changed', line) is None:
            line = line.strip()
            if line:
                try:
                    parts = line.split(' ', 2)
                    (hash, stamp, author) = (parts[0], int(parts[1]), parts[2])
                    row_processor(LocByDate(hash, stamp, files, inserted, deleted, total_lines))
                    files, inserted, deleted = 0, 0, 0
                except ValueError:
                    logging.warning(f'unexpected line "{line}')
            else:
                logging.warning(f'unexpected line "{line}')
        else:
            numbers = getstatsummarycounts(line)

            if len(numbers) == 3:
                (files, inserted, deleted) = map(lambda el: int(el), numbers)
                total_lines += inserted
                total_lines -= deleted
            else:
                logging.warning(f'Failed to handle line "{line}"')
                (files, inserted, deleted) = (0, 0, 0)
    return total_lines


if __name__ == "__main__":
    conf, paths, outputpath = cli.get_cli()
    with open(outputpath, 'w', encoding='utf8') as f:
        writer = csv.writer(f)
        writer.writerow(['repo', 'sha', 'stamp', 'file count', 'lines inserted', 'lines deleted', 'total lines'])

        for path in paths:
            repo_name = os.path.split(path)[1]
            with (cd.cd(path)):

                gen_loc_data(
                    conf,
                    lambda row: writer.writerow([repo_name, row.hash, row.stamp, row.file_count, row.lines_inserted, row.lines_deleted, row.total_lines]))
