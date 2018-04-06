import csv
import logging
import os
import sys

import multiprocessing_logging

from gitstats import cli
from gitstats.data import AuthorTotals, AuthorRow, File, LocByDate, Revision, Tag
from gitstats.data_generators import gen_author_data, gen_author_totals_data, gen_tag_data, gen_revision_data, \
    gen_file_data, gen_loc_data

exectime_internal = 0.0
exectime_external = 0.0


class _FileHandles:
    def __init__(self, output_dir):
        self.author_info = open(os.path.join(output_dir, 'authors.csv'), 'w', encoding='utf8')
        self.author_info_writer = csv.writer(self.author_info)
        self.author_info_writer.writerow(['Repo', 'CommitHash', 'TimeStamp', 'Author', 'FilesChanged', 'LinesInserted',
                                          'LinesDeleted'])

        self.author_totals_info = open(os.path.join(output_dir, 'author_totals.csv'), 'w', encoding='utf8')
        self.author_totals_info_writer = csv.writer(self.author_totals_info)
        self.author_totals_info_writer.writerow(["Repo", "Author", "Commits"])

        self.tag_info = open(os.path.join(output_dir, 'tags.csv'), 'w', encoding='utf8')
        self.tag_info_writer = csv.writer(self.tag_info)
        self.tag_info_writer.writerow(["Repo", "CommitHash", "Timestamp", "TotalCommits", "Author", "AuthorCommits"])

        self.revision_info = open(os.path.join(output_dir, 'revs.csv'), 'w', encoding='utf8')
        self.revision_info_writer = csv.writer(self.revision_info)
        self.revision_info_writer.writerow(['Repo', 'CommitHash', 'TimeStamp', 'TimeZone', 'Author', 'AuthorEmail',
                                            'Domain', 'FilesChanged'])

        self.files_info = open(os.path.join(output_dir, 'files.csv'), 'w', encoding='utf8')
        self.files_info_writer = csv.writer(self.files_info)
        self.files_info_writer.writerow(['Repo', 'File', 'Ext', 'Size', 'Lines'])

        self.loc_info = open(os.path.join(output_dir, 'loc.csv'), 'w', encoding='utf8')
        self.loc_info_writer = csv.writer(self.loc_info)
        self.loc_info_writer.writerow(['Repo', 'CommitHash', 'TimeStamp', 'FileCount', 'LinesInserted', 'LinesDeleted',
                                       'TotalLines'])

        self.repo_info = open(os.path.join(output_dir, 'repo.csv'), 'w', encoding='utf8')
        self.repo_info_writer = csv.writer(self.repo_info)
        self.repo_info_writer.writerow(['Repo', 'TotalFiles', 'TotalLines'])

    def close(self):
        self.author_info.close()
        self.author_totals_info.close()
        self.tag_info.close()
        self.revision_info.close()
        self.files_info.close()
        self.loc_info.close()
        self.repo_info.close()


class GitCsvGenerator():
    def __init__(self, conf, output_dir):
        self.conf = conf
        self.files: _FileHandles = None
        self.output_dir = output_dir

    def __enter__(self):
        self.files = _FileHandles(self.output_dir)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.files.close()

    def collect(self, dir):
        if len(self.conf['project_name']) == 0:
            self.projectname = os.path.basename(os.path.abspath(dir))
        else:
            self.projectname = self.conf['project_name']

        self.get_total_authors()
        self.get_tags()
        self.get_revision_info()
        self.get_file_info()
        self.get_loc_info()
        self.get_author_info()

    def get_total_authors(self):
        logging.info(f"Getting author totals for {self.projectname}")
        def row_processor(row: AuthorTotals):
            self.files.author_totals_info_writer.writerow([self.projectname, row.author, row.total_commits])
        gen_author_totals_data(self.conf, row_processor)

    def get_tags(self):
        logging.info(f"Getting tag info for {self.projectname}")
        def row_processor(row: Tag):
            for author, commits in row.authors.items():
                self.files.tag_info_writer.writerow([self.projectname, row.hash, row.stamp, row.commits, author, commits])
        gen_tag_data(self.conf, row_processor)

    def get_revision_info(self):
        logging.info(f"Getting rev info for {self.projectname}")
        def row_processor(row: Revision):
            self.files.revision_info_writer.writerow([self.projectname, row.hash, row.stamp, row.timezone, row.author,
                                                      row.email, row.domain, row.file_count])
        gen_revision_data(self.conf, row_processor)

    def get_file_info(self):
        logging.info(f"Getting file info for {self.projectname}")
        def row_processor(row: File):
            self.files.files_info_writer.writerow([self.projectname, row.full_path, row.ext, row.size, row.lines])
        gen_file_data(self.conf, row_processor)

    def get_loc_info(self):
        logging.info(f"Getting LOC info for {self.projectname}")
        def row_processor(row: LocByDate):
            self.files.loc_info_writer.writerow([self.projectname, row.hash, row.stamp, row.file_count,
                                                 row.lines_inserted, row.lines_deleted, row.total_lines])
        total_files, total_lines = gen_loc_data(self.conf, row_processor)
        self.files.repo_info_writer.writerow([self.projectname, total_files, total_lines])

    def get_author_info(self):
        logging.info(f"Getting author info for {self.projectname}")
        def row_processor(row: AuthorRow):
            self.files.author_info_writer.writerow([self.projectname, row.hash, row.stamp, row.author,
                                                    row.files_modified, row.lines_inserted, row.lines_deleted])
        gen_author_data(self.conf, row_processor)

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