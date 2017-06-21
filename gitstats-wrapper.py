from __future__ import print_function
from __future__ import absolute_import
'''A gitstats wrapper which calls gitstats recursively on directory 
that contains multiple git repositories.

    Usage:
      # python gitstats-wrapper.py source_dir dest_dir
'''
import argparse
import os
import os.path
import time
from gitstats import GitStats


# Initialize a GitStats class
g = GitStats()

# Parse command line arguments, retrieve the source directory
# and the output directory
# Instantiate the parser
parser = argparse.ArgumentParser(description='gitstats wrapper')
# Add required positional argument
parser.add_argument('source_dir', help='The source project folder')
parser.add_argument('dest_dir', help='The output folder')

# Parse the command line arguments
args = parser.parse_args()
source_dir = args.source_dir
dest_dir = args.dest_dir

# Get all intermediate child directories
second_level_dir_list = next(os.walk(source_dir))[1]

# Identify the git repo
for d in second_level_dir_list:
    # This should give you "top_dir/second_dir/.git"
    sub_source_path = source_dir + '/' + d
    sub_target_path = dest_dir + '/' + d
    if os.path.exists(sub_source_path + '/.git'):
        print('Going to run gitstats on {0}'.format(sub_source_path))
        print('Output will be in {0}'.format(sub_target_path))
        time.sleep(5)
        g.run([sub_source_path, sub_target_path])
