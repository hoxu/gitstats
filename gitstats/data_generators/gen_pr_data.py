import csv
import logging
import os

from datetime import datetime

from gitstats import cli, cd
from gitstats.data import Revision, PullRequest, RevisionGraph
from gitstats.data_generators import gen_revision_graph


def gen_pr_data(row_processor, graph: RevisionGraph):
    '''
    Given a configuration, pull revision information. For
    each author, callback to the row_processor passing an PullRequest

    As a side effect, every revision in the master_rev dictionary will be updated
    with it's branch_parent and master_parent

    :param row_processor: function to receive the callback
    :return: None
    '''

    for rev in graph.master_revs:
        revision = graph.revisions[rev]
        if revision.valid_pr and revision.branch_parent in graph.revisions:
            branch_rev: Revision = graph.revisions[revision.branch_parent]
            delta = datetime.utcfromtimestamp(revision.stamp) - datetime.utcfromtimestamp(branch_rev.stamp)
            if delta.total_seconds() < 0:
                logging.warning(f"Unexpected. Negative duration: {rev}")
                revision.valid_pr = False
            else:
                row_processor(PullRequest(revision.stamp, revision.hash, revision.author,
                                          graph.linkage[rev], revision.branch_parent, rev, delta))


if __name__ == "__main__":
    conf, paths, outputpath = cli.get_cli()
    begin, end = cli.get_begin_end_timestamps(conf)
    with open(outputpath, 'w', encoding='utf8') as f:
        writer = csv.writer(f)
        writer.writerow(['repo', 'hash', 'stamp', 'masterRev', 'branchRev', 'prMergeDuration', 'prMergeDurationHr'])

        for path in paths:
            repo_name = os.path.split(path)[1]
            with (cd.cd(path)):
                graph = gen_revision_graph()

                def row_processor(row: PullRequest):
                    if row.stamp >= begin and row.stamp <= end:
                        writer.writerow([repo_name, row.hash, row.stamp, row.master_rev, row.branch_rev, row.duration.total_seconds(), row.duration])
                gen_pr_data(row_processor, graph)
