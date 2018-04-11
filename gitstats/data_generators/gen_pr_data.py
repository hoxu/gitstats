import csv
import logging
import os

from multiprocessing import Pool

from gitstats import cli, cd
from gitstats.miscfuncs import getlogrange, getpipeoutput, gettimedelta
from gitstats.data import PullRequest


def gen_pr_data(conf, row_processor):
    '''
    Given a configuration, pull revision information. For
    each author, callback to the row_processor passing an PullRequest

    :param conf: configuration (mostly used for date limits)
    :param row_processor: function to receive the callback
    :return: None
    '''

    prs = {} # hash -> PullRequest

    # DBG: git log --all --grep="Merge pull request .* to master" --shortstat --pretty=format:"%H %at %aN" --since="2017-10-01" "HEAD"', 'grep -v ^commit'
    lines = getpipeoutput(
        ['git log --all --grep="Merge pull request .* to master" --shortstat '
         '--pretty=format:"%%H %%at %%aN|%%P" %s' % getlogrange(conf, 'HEAD'),
         'grep -v ^"files changed"']).split('\n')
    for line in lines:
        line = line.strip()
        if line and not 'files changed' in line:
            parts = line.split(' ', 2)
            hash = parts[0]
            try:
                stamp = int(parts[1])
            except ValueError:
                stamp = 0
            (author, parent_hashes) = parts[2].split('|')
            parent_hashes = parent_hashes.split(' ')
            if len(parent_hashes) == 2:
                prs[hash] = PullRequest(stamp, hash, author, parent_hashes)

    keys = prs.keys()
    for pr in prs.values():
        if pr.parent_hashes[0] in keys:
            pr.master_rev = pr.parent_hashes[0]
            if pr.parent_hashes[1] in keys:
                logging.warning(f"Unexpected branching: {pr}")
                pr.invalid_pr = True
            else:
                pr.branch_rev = pr.parent_hashes[1]
        else:
            pr.branch_rev = pr.parent_hashes[0]
            if pr.parent_hashes[1] in keys:
                pr.master_rev = pr.parent_hashes[1]
            else:
                logging.warning(f"Unexpected branching: {pr}")
                pr.invalid_pr = True

    prs_to_query = [(pr.hash, pr.stamp, pr.branch_rev) for pr in prs.values() if not pr.invalid_pr]

    # # todo: consider putting in a cache for this. There was one in the original code
    # # DBG:  git log -n 1 --format=%at "ceb3165b51ae0680724fd71e16a5ff836a0de41e"
    pool = Pool(processes=conf['processes'])
    time_deltas = pool.map(gettimedelta, prs_to_query)
    pool.terminate()
    pool.join()
    for (hash, timedelta) in time_deltas:
        pr = prs[hash]
        pr.duration = timedelta
        if pr.duration.total_seconds() < 0:
            pr.invalid_pr = True
            logging.warning(f"Unexpected. Negative duration: {pr}")
        else:
            row_processor(pr)



if __name__ == "__main__":
    conf, paths, outputpath = cli.get_cli()
    with open(outputpath, 'w', encoding='utf8') as f:
        writer = csv.writer(f)
        writer.writerow(['repo', 'hash', 'stamp', 'masterRev', 'branchRev', 'prMergeDuration', 'prMergeDurationHr'])

        for path in paths:
            repo_name = os.path.split(path)[1]
            with (cd.cd(path)):
                def row_processor(row: PullRequest):
                    writer.writerow([repo_name, row.hash, row.stamp, row.master_rev, row.branch_rev, row.duration.total_seconds(), row.duration])
                gen_pr_data(conf, row_processor)
