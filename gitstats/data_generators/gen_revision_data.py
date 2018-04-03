import csv
import os

from multiprocessing import Pool

from gitstats import cli, cd
from gitstats.miscfuncs import getlogrange, getpipeoutput, getnumoffilesfromrev
from gitstats.data import Revision


def gen_revision_data(conf, row_processor):
    '''
    Given a configuration, pull revision information. For
    each author, callback to the row_processor passing an Revision

    :param conf: configuration (mostly used for date limits)
    :param row_processor: function to receive the callback
    :return: Number of commits
    '''

    revisions = {} # tree_hash -> Revision
    # Collect revision statistics
    # Outputs "<stamp> <date> <time> <timezone> <author> '<' <mail> '>'"

    # DBG: git rev-list --pretty=format:"%at %ai %aN <%aE>" --since="2017-10-01" "HEAD"', 'grep -v ^commit'
    lines = getpipeoutput(
        ['git rev-list --pretty=format:"%%T %%H %%at %%ai %%aN <%%aE>" %s' % getlogrange(conf, 'HEAD'),
         'grep -v ^commit']).split('\n')
    for line in lines:
        parts = line.split(' ', 6)
        tree_hash = parts[0]
        sha = parts[1]
        try:
            stamp = int(parts[2])
        except ValueError:
            stamp = 0
        timezone = parts[5]
        author, mail = parts[6].split('<', 1)
        author = author.strip()
        mail = mail.rstrip('>')
        domain = '?'
        if mail.find('@') != -1:
            domain = mail.rsplit('@', 1)[1]
            domain.rstrip('>')
        revisions[tree_hash] = Revision(sha, stamp, timezone, author, mail, domain)

    # todo: consider putting in a cache for this. There was one in the original code
    # DBG: git ls-tree -r --name-only "ceb3165b51ae0680724fd71e16a5ff836a0de41e"', 'wc -l'
    pool = Pool(processes=conf['processes'])
    rev_count = pool.map(getnumoffilesfromrev, revisions.keys())
    pool.terminate()
    pool.join()
    # Update cache with new revisions and append then to general list
    for (rev, count) in rev_count:
        revision = revisions[rev]
        revision.file_count = count
        row_processor(revision)

    return len(lines)


if __name__ == "__main__":
    conf, paths, outputpath = cli.get_cli()
    with open(outputpath, 'w', encoding='utf8') as f:
        writer = csv.writer(f)
        writer.writerow(['repo', 'sha', 'stamp', 'timezone', 'author', 'email', 'domain', 'files_changed'])

        for path in paths:
            repo_name = os.path.split(path)[1]
            with (cd.cd(path)):
                def row_processor(row: Revision):
                    writer.writerow([repo_name, row.hash, row.stamp, row.timezone, row.author, row.email,
                                     row.domain, row.file_count])
                gen_revision_data(conf, row_processor)
