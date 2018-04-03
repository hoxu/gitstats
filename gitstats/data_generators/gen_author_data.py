import csv
import logging
import os
import re

from gitstats import cli, cd
from gitstats.miscfuncs import getlogrange, getpipeoutput, getstatsummarycounts
from gitstats.data import AuthorRow


def gen_author_data(conf, row_processor):
    '''
    Given a configuration, pull authorship information. For
    each author, callback to the row_processor passing an AuthorRow

    :param conf: configuration (mostly used for date limits)
    :param row_processor: function to receive the callback
    :return: None
    '''

    # DBG: git log --shortstat --date-order --pretty=format:"%H %at %aN" --since="2017-10-01" "HEAD"
    # Results are in the form of
    #
    # 3c16756701d264619db0b309f42ebdc713b29827 1522513256 Dan Rapp
    # 524ee0d32ffbbb8bb82966b769bbf7dbc1d87a68 1522480979 Michael Wright
    # 1 file changed, 6 insertions(+)
    #
    # If there are two (or more) lines,
    # The first line(s) is the merge to master or other branch
    # The last line is the commit on the branch
    lines = getpipeoutput(
        ['git log --shortstat --date-order --pretty=format:"%%H %%at %%aN" %s' % (
            getlogrange(conf, 'HEAD'))]).split('\n')
    lines.reverse()

    files = 0
    inserted = 0
    deleted = 0
    stamp = 0
    for line in lines:
        if len(line) == 0:
            continue

        # <stamp> <author>
        if re.search('files? changed', line) is None:
            if files + inserted + deleted > 0:  # this case indicates we've already processed the line
                pos = line.find(' ')
                if pos != -1:
                    try:
                        oldstamp = stamp
                        tokens = line.split()
                        sha = tokens[0]
                        stamp = int(tokens[1])
                        author = ' '.join(tokens[2:])
                        if oldstamp > stamp:
                            # clock skew, keep old timestamp to avoid having ugly graph
                            stamp = oldstamp
                        row_processor(AuthorRow(sha, stamp, author, files, inserted, deleted))
                        # Since subsequent lines are (generally) reflections of merging into a branch
                        # don't provide "credit" to the author did the merge
                        (files, inserted, deleted) = 0, 0, 0
                    except ValueError:
                        logging.warning(f'unexpected line "{line}')
                else:
                    logging.warning(f'unexpected line "{line}')
        else:
            numbers = getstatsummarycounts(line)

            if len(numbers) == 3:
                (files, inserted, deleted) = map(lambda el: int(el), numbers)
            else:
                logging.warning(f'Failed to handle line "{line}"')
                (files, inserted, deleted) = (0, 0, 0)

if __name__ == "__main__":
    conf, paths, outputpath = cli.get_cli()
    with open(outputpath, 'w', encoding='utf8') as f:
        writer = csv.writer(f)
        writer.writerow(['repo', 'sha', 'stamp', 'author', 'files changed', 'lines inserted', 'lines deleted'])

        for path in paths:
            repo_name = os.path.split(path)[1]
            with (cd.cd(path)):
                def row_processor(row: AuthorRow):
                    writer.writerow([repo_name, row.hash, row.stamp, row.author, row.files_modified,
                                     row.lines_inserted, row.lines_deleted])
                gen_author_data(conf, row_processor)
