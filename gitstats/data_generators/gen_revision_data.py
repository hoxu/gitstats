import csv
import os

from multiprocessing import Pool

from gitstats import cli, cd
from gitstats.miscfuncs import getnumoffilesfromrev
from gitstats.data import Revision, RevisionGraph
from gitstats.data_generators.gen_revision_graph import gen_revision_graph


def gen_revision_data(conf, row_processor, graph: RevisionGraph):
    '''
    Given a configuration, pull revision information. For
    each author, callback to the row_processor passing an Revision

    :param conf: configuration (mostly used for date limits)
    :param row_processor: function to receive the callback
    :return: None
    '''

    # todo: consider putting in a cache for this. There was one in the original code
    # DBG: git ls-tree -r --name-only "ceb3165b51ae0680724fd71e16a5ff836a0de41e"', 'wc -l'
    pool = Pool(processes=conf['processes'])
    rev_count = pool.map(getnumoffilesfromrev, graph.revisions.keys())
    pool.terminate()
    pool.join()
    # Update cache with new revisions and append then to general list
    for (rev, count) in rev_count:
        revision = graph.revisions[rev]
        revision.file_count = count
        row_processor(revision)


if __name__ == "__main__":
    conf, paths, outputpath = cli.get_cli()
    begin, end = cli.get_begin_end_timestamps(conf)
    with open(outputpath, 'w', encoding='utf8') as f:
        writer = csv.writer(f)
        writer.writerow(['repo', 'sha', 'stamp', 'timezone', 'author', 'email', 'domain', 'files_changed'])

        for path in paths:
            rev_by_tree_hash, _, _, _ = gen_revision_graph(begin, end)
            repo_name = os.path.split(path)[1]
            with (cd.cd(path)):
                def row_processor(row: Revision):
                    writer.writerow([repo_name, row.hash, row.stamp, row.timezone, row.author, row.email,
                                     row.domain, row.file_count])
                gen_revision_data(conf, row_processor, rev_by_tree_hash)
