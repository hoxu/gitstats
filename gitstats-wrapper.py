import libraries

path = './8956n'

# Global DataCollector:
class GlobalDataCollector:
    """Manages data collection from the parent revision control repository."""
    def __init__(self):
        self.global_stamp_created = time.time()
        self.global_cache = {}
        self.global_total_authors = 0
        self.global_activity_by_hour_of_day = {} # hour -> commits
        # All other collector definitions

# Go through each sub directory
directory_content = list_files(path)
cd(path)
for file in directory_content:
    current_path = pwd()
    if type(file) == "directory"
        cd(file)
        if ".git" in current_directory
            data = gitstats()
            get_total_authors(data, global_total_author)
            get_total_line_of_code(data, global_line_of_code)
            ...
    cd(current_path)
    
# Now we should have all the data for 8956n project
cd(current_path)
print 'Generating global report
report = HTMLReportCreator()
report.create(data, outputpath)
