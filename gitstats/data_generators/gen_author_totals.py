import csv
import os

from gitstats import cli, cd
from gitstats.miscfuncs import getlogrange, getpipeoutput
from gitstats.data import AuthorTotals


def gen_author_totals_data(conf, row_processor=None, revision_range=None):
    '''
    Given configuration, pull total commit per author. For
    each "row" callback to the row_processor passing an AuthorTotals

    :param conf: configuration (mostly used for date limits)
    :param row_processor: function to receive the callback
    :return: count of the number of authors
    '''

    # DBG: git shortlog -s --since="2017-10-01" "HEAD"
    if not revision_range:
        revision_range = getlogrange(conf)
    lines = getpipeoutput(['git shortlog -s %s' % revision_range]).split('\n')
    count = 0
    for line in lines:
        line = line.strip()
        if not line:
            continue
        count += 1
        if row_processor:
            tokens = line.split()
            commit_count = int(tokens[0])
            author = ' '.join(tokens[1:])
            row_processor(AuthorTotals(author, commit_count))
    return count

if __name__ == "__main__":
    conf, paths, outputpath = cli.get_cli()
    with open(outputpath, 'w', encoding='utf8') as f:
        writer = csv.writer(f)
        writer.writerow(['repo', 'author', 'commits'])

        for path in paths:
            repo_name = os.path.split(path)[1]
            with (cd.cd(path)):
                def row_processor(row: AuthorTotals):
                    writer.writerow([repo_name, row.author, row.total_commits])
                gen_author_totals_data(conf, row_processor)
