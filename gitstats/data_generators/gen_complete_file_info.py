import csv
import os

from gitstats import cli, cd
from gitstats.miscfuncs import getpipeoutput
from gitstats.data import FileInfo, Revision, RevisionGraph
from gitstats.data_generators import gen_revision_graph


def gen_complete_file_info(graph: RevisionGraph):
    '''
    Given a dictionary of revisions on the master branch, collect all file info
    using tokei for that revision

    :param: master_rev - a dictionary of commit hash to Revision object for revisions on the master branch

    :return: None. As a side effect, compliete file info by language type will be added to all
    revisions in master_rev
    '''

    # use tokei to gather detailed file info for each revision on master
    for revision in graph.master_revs:
        getpipeoutput([f'git checkout {revision}'])
        # for some reason if we combine these, tokei gives incorrect results!!!!
        lines = getpipeoutput(['tokei']).split('\n')
        for line in lines[3:-3] + [lines[-2]]:
            line = line.strip()
            file_info = FileInfo(*line.rsplit(maxsplit=5))
            graph.revisions[revision].file_infos[file_info.language] = file_info

    getpipeoutput(['git checkout master'])

    # run through master revisions and calculate delta with previous master revision
    for revision in graph.master_revs:
        master_parent = graph.revisions[revision].master_parent
        if master_parent in graph.master_revs:
            current = graph.revisions[revision].file_infos
            previous = graph.revisions[master_parent].file_infos
            for lang, cur_file_info in current.items():
                if lang in previous:
                    graph.revisions[revision].delta[lang] = cur_file_info - previous[lang]
                else:
                    graph.revisions[revision].delta[lang] = cur_file_info


if __name__ == "__main__":
    conf, paths, outputpath = cli.get_cli()

    with open(outputpath, 'w', encoding='utf8') as f:
        writer = csv.writer(f)
        writer.writerow(['repo', 'hash', 'stamp', 'author', 'language', 'files', 'lines', 'code', 'comments', 'blanks'])

        for path in paths:
            repo_name = os.path.split(path)[1]
            with (cd.cd(path)):
                graph = gen_revision_graph()
                gen_complete_file_info(graph)

                for rev in graph.master_revs:
                    revision: Revision = graph.revisions[rev]
                    for lang, file_info in revision.delta.items():
                        if file_info.file_count or \
                                file_info.line_count or \
                                file_info.code_line_count or \
                                file_info.comment_line_count or \
                                file_info.blank_line_count:
                            writer.writerow([repo_name,
                                             revision.hash,
                                             revision.stamp,
                                             graph.revisions[revision.branch_parent].author,
                                             lang,
                                             file_info.file_count,
                                             file_info.line_count,
                                             file_info.code_line_count,
                                             file_info.comment_line_count,
                                             file_info.blank_line_count])
