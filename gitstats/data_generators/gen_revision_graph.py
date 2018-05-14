import logging
import os
import re

from typing import Dict
from gitstats import cli, cd
from gitstats.miscfuncs import getpipeoutput
from gitstats.data import Revision, RevisionGraph


def gen_revision_graph() -> RevisionGraph:
    '''
    Given beginning and ending time stamp, get all revisions from the repo within that range,
    key them by tree_hash, commit_hash as well as create a graph of revisions and a list
    of revisions merging to master

    :return: RevisionGraph
    '''

    # this match string for PRs merged to master is particular to BitBucket
    # probably should come from configuration
    prog = re.compile(r'Merge pull request #([0-9]*) in.*to master')

    graph = RevisionGraph({}, set(), {})

    lines = getpipeoutput(
        [f'git rev-list --pretty="%T|%H|%at|%ai|%aN|%aE|%P|%s" "HEAD"',
         'grep -v ^commit']).split('\n')
    for line in lines:
        line = line.strip()
        if line:
            graph.add_revision_to_graph(*get_revision_from_line(line, prog))

    new_masters = set()
    for rev in graph.master_revs:
        parents = graph.linkage[rev]
        revision: Revision = graph.revisions[rev]
        for parent in parents:
            if parent in graph.master_revs:
                if revision.master_parent:
                    logging.warning(f"{rev} has multiple master parents")
                    revision.valid_pr = False
                revision.master_parent = parent
            else:
                if revision.branch_parent:
                    if not revision.master_parent:
                        # we likely have a merge into master in a branch that didn't use
                        # bitbucket conventions... arbitrarily choose the oldest parent
                        # revision as the master branch (we could back chain both and find
                        # which branch exists in the ancestry of the other, but for now,
                        # this will suffice
                        if graph.revisions[parent].stamp < graph.revisions[revision.branch_parent].stamp:
                            revision.master_parent = parent
                            new_masters.add(parent)
                        else:
                            revision.master_parent = revision.branch_parent
                            new_masters.add(revision.branch_parent)
                            revision.branch_parent = parent
                    else:
                        logging.warning(f"{rev} has multiple branch parents")
                        revision.valid_pr = False
                else:
                    revision.branch_parent = parent
    graph.master_revs.update(new_masters)

    # validate masters based on git log --first-parent
    lines = getpipeoutput(
        ['git log --first-parent --pretty="%T|%H|%at|%ai|%aN|%aE|%P|%s"',
         'grep -v ^commit']).split('\n')
    for line in lines:
        line = line.strip()
        if line:
            graph.add_revision_to_graph(*get_revision_from_line(line, prog), is_master=True)

    # update master branch as appropriate
    for rev in graph.master_revs:
        if not graph.revisions[rev].master_parent:
            parents = graph.linkage[rev]
            if len(parents) == 1 and parents[0]:
                graph.revisions[rev].master_parent = parents[0]
            else:
                if parents[0]:
                    logging.warning(f"{rev} has no master parent info. {parents}")

    return graph


def get_revision_from_line(line, prog):
    tree_hash, sha, stamp, time, author, mail, parents, comments = line.split('|', 7)
    try:
        stamp = int(stamp)
    except ValueError:
        stamp = 0
    timezone = time.split(' ')[2]
    domain = '?'
    if mail.find('@') != -1:
        domain = mail.rsplit('@', 1)[1]
    parents = parents.split(' ')
    revision = Revision(sha, stamp, timezone, author, mail, domain, comments)
    match = prog.search(comments)
    if match:
        revision.master_pr = int(match.group(1))
    return revision, parents


if __name__ == "__main__":
    conf, paths, outputpath = cli.get_cli()
    graphs: Dict[str, RevisionGraph] = {}
    for path in paths:
        repo_name = os.path.split(path)[1]
        with (cd.cd(path)):
            graphs[repo_name] = gen_revision_graph()
    for k, v in graphs.items():
        print(f"{k}: {len(v.revisions)} revisions, {len(v.master_revs)} revisions on master")
