#! /usr/bin/env python3
import csv
import logging
import os
import sys

import multiprocessing_logging

from collections import defaultdict

from gitstats.cd import cd

from gitstats import cli
from gitstats.data import PullRequest, Revision
from gitstats.data_generators import gen_pr_data, gen_revision_graph, gen_complete_file_info

exectime_internal = 0.0
exectime_external = 0.0


class _FileHandles:
    def __init__(self, output_dir):
        self.author_totals_info = open(os.path.join(output_dir, 'author_totals.csv'), 'w', encoding='utf8')
        self.author_totals_info_writer = csv.writer(self.author_totals_info)
        self.author_totals_info_writer.writerow(["Repo", "Author", "Commits"])

        self.revision_info = open(os.path.join(output_dir, 'revs.csv'), 'w', encoding='utf8')
        self.revision_info_writer = csv.writer(self.revision_info)
        self.revision_info_writer.writerow(['Repo', 'CommitHash', 'TimeStamp', 'TimeZone', 'Author', 'AuthorEmail',
                                            'Domain'])

        self.loc_info = open(os.path.join(output_dir, 'loc.csv'), 'w', encoding='utf8')
        self.loc_info_writer = csv.writer(self.loc_info)
        self.loc_info_writer.writerow(['Repo', 'CommitHash', 'TimeStamp', 'Language', 'Files', 'Lines', 'Code',
                                       'Comments', 'Blanks'])

        self.loc_delta = open(os.path.join(output_dir, 'loc_delta.csv'), 'w', encoding='utf8')
        self.loc_delta_writer = csv.writer(self.loc_delta)
        self.loc_delta_writer.writerow(['Repo', 'CommitHash', 'TimeStamp', 'Author', 'Language', 'Files', 'Lines',
                                        'Code', 'Comments', 'Blanks'])

        self.repo_info = open(os.path.join(output_dir, 'repo.csv'), 'w', encoding='utf8')
        self.repo_info_writer = csv.writer(self.repo_info)
        self.repo_info_writer.writerow(['Repo', 'Language', 'Files', 'Lines',
                                        'Code', 'Comments', 'Blanks'])

        self.prs_info = open(os.path.join(output_dir, 'prs.csv'), 'w', encoding='utf8')
        self.prs_info_writer = csv.writer(self.prs_info)
        self.prs_info_writer.writerow(['Repo', 'CommitHash', 'TimeStamp', 'ParentHashMaster', 'ParentHashBranch',
                                       'PrMergeDuration'])

    def close(self):
        self.author_totals_info.close()
        self.revision_info.close()
        self.loc_info.close()
        self.loc_delta.close()
        self.repo_info.close()
        self.prs_info.close()

class GitCsvGenerator():
    def __init__(self, conf, output_dir):
        self.conf = conf
        self.files: _FileHandles = None
        self.output_dir = output_dir
        self.begin, self.end = cli.get_begin_end_timestamps(conf)

    def __enter__(self):
        self.files = _FileHandles(self.output_dir)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.files.close()

    def collect(self, dir):

        with cd(dir):
            if len(self.conf['project_name']) == 0:
                self.projectname = os.path.basename(os.path.abspath(dir))
            else:
                self.projectname = self.conf['project_name']

            graph = gen_revision_graph()
            gen_complete_file_info(graph)

            self.extract_total_authors(graph)
            self.extract_pr_info(graph)
            self.extract_code_info(graph)
            self.extract_revision_info(graph)
            # self.get_revision_info(graph)
            # self.get_tags()
            # self.get_file_info()
            # self.get_loc_info()
            # self.get_author_info()

    def extract_total_authors(self, graph):
        logging.info(f"Getting author totals for {self.projectname}")

        authors = defaultdict(int)
        for rev in graph.revisions.values():
            # don't include merge to master as a commit in counting total author
            # commits.
            if rev.stamp >= self.begin and rev.stamp <= self.end and rev.master_pr == 0:
                authors[rev.author] += 1

        for author, total_commits in authors.items():
            self.files.author_totals_info_writer.writerow([self.projectname, author, total_commits])

    def extract_pr_info(self, graph):
        logging.info(f"Getting pull request info for {self.projectname}")
        def row_processor(row: PullRequest):
            if row.stamp >= self.begin and row.stamp <= self.end:
                self.files.prs_info_writer.writerow([self.projectname, row.hash, row.stamp, row.master_rev,
                                                        row.branch_rev, row.duration.total_seconds()])
        gen_pr_data(row_processor, graph)

    def extract_code_info(self, graph):
        rev_max: Revision = None
        for rev in graph.master_revs:
            revision: Revision = graph.revisions[rev]
            if not rev_max or revision.stamp > rev_max.stamp:
                rev_max = revision
            if revision.stamp >= self.begin and revision.stamp <= self.end:
                for lang, file_info in revision.delta.items():
                        if file_info.file_count or \
                                file_info.line_count or \
                                file_info.code_line_count or \
                                file_info.comment_line_count or \
                                file_info.blank_line_count:

                            if revision.branch_parent in graph.revisions:
                                parent = revision.branch_parent
                            else:
                                parent = revision.master_parent
                            if parent:
                                self.files.loc_delta_writer.writerow([self.projectname,
                                                 revision.hash,
                                                 revision.stamp,
                                                 graph.revisions[parent].author,
                                                 lang,
                                                 file_info.file_count,
                                                 file_info.line_count,
                                                 file_info.code_line_count,
                                                 file_info.comment_line_count,
                                                 file_info.blank_line_count])
                for lang, file_info in revision.file_infos.items():
                        if file_info.file_count or \
                                file_info.line_count or \
                                file_info.code_line_count or \
                                file_info.comment_line_count or \
                                file_info.blank_line_count:
                            self.files.loc_info_writer.writerow([self.projectname,
                                             revision.hash,
                                             revision.stamp,
                                             lang,
                                             file_info.file_count,
                                             file_info.line_count,
                                             file_info.code_line_count,
                                             file_info.comment_line_count,
                                             file_info.blank_line_count])

        for file_info in rev_max.file_infos.values():
            self.files.repo_info_writer.writerow([self.projectname,
                                                  file_info.language,
                                                  file_info.file_count,
                                                  file_info.line_count,
                                                  file_info.code_line_count,
                                                  file_info.comment_line_count,
                                                  file_info.blank_line_count])

    def extract_revision_info(self, graph):
        for revision in graph.revisions.values():
            if revision.stamp >= self.begin and revision.stamp <= self.end:
                self.files.revision_info_writer.writerow([self.projectname,
                                                          revision.hash,
                                                          revision.stamp,
                                                          revision.timezone,
                                                          revision.author,
                                                          revision.email,
                                                          revision.domain])

def gen_csv():
    conf, paths, outputpath = cli.get_cli()

    for path in paths:
        if not os.path.isdir(path):
            logging.fatal(f'Input path {path} does not exist')
            sys.exit(1)

    logging.basicConfig(level=conf['logging'], format='%(message)s')
    multiprocessing_logging.install_mp_handler()
    try:
        os.makedirs(outputpath)
    except OSError:
        pass
    if not os.path.isdir(outputpath):
        logging.fatal('Output path is not a directory or does not exist')
        sys.exit(1)

    logging.info(f'Output path: {outputpath}')

    data = GitCsvGenerator(conf, outputpath)
    with data:
        for gitpath in paths:
            logging.info(f'Git path: {gitpath}')

            prevdir = os.getcwd()
            os.chdir(gitpath)

            logging.info('Collecting data...')
            data.collect(gitpath)

            os.chdir(prevdir)

if __name__ == '__main__':
    gen_csv()