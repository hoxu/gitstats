import csv
import os

from collections import defaultdict
from typing import Dict

from gitstats import cli, cd
from gitstats.miscfuncs import getpipeoutput
from gitstats.data import AuthorTotals, Tag
from gitstats.data_generators import gen_author_totals_data


def gen_tag_data(conf, row_processor):
    '''
    Given a configuration, pull tag information. For
    each tag, callback to the row_processor passing a Tag

    :param conf: configuration (mostly used for date limits)
    :param row_processor: function to receive the callback
    :return: None
    '''

    # tags
    tags = {} # stamp -> tags
    lines = getpipeoutput(['git show-ref --tags']).split('\n')
    for line in lines:
        if len(line) == 0:
            continue
        (line_hash, tag) = line.split(' ')

        tag = tag.replace('refs/tags/', '')
        output = getpipeoutput(['git log "%s" --pretty=format:"%%at" -n 1' % line_hash])

        stamp = 0
        if len(output) > 0:
            try:
                stamp = int(output.strip())
            except ValueError:
                stamp = 0

        tags[stamp] = Tag(tag, stamp, line_hash, 0, {})

    stamps = sorted(tags.keys())
    prev = None
    for stamp in stamps:
        def process_row(row: AuthorTotals):
            tags[stamp].authors[row.author] = row.total_commits
            tags[stamp].commits += row.total_commits

        revision_tags = tags[stamp].tag
        if prev != None:
            revision_tags += ' "^%s"' % prev

        gen_author_totals_data(conf, process_row, revision_tags)
        row_processor(tags[stamp])

        prev = tags[stamp].tag


if __name__ == "__main__":
    conf, paths, outputpath = cli.get_cli()
    with open(outputpath, 'w', encoding='utf8') as f:
        writer = csv.writer(f)
        writer.writerow(['repo', 'sha', 'stamp', 'commits for tag', 'author', 'commits by author'])

        for path in paths:
            repo_name = os.path.split(path)[1]
            with (cd.cd(path)):

                def process_row(row):
                    for author, commits in row.authors.items():
                        writer.writerow([repo_name, row.hash, row.stamp, row.commits, author, commits])

                gen_tag_data(conf, process_row)
