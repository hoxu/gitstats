import os
import sys

# python execution.py <source folder> <output folder>

def generateGitstatsOnFolders (): 
	# print (sys.argv)

	#  root location
	source_folder = sys.argv[1]
	# final destination
	output_folder = sys.argv[2]
	print (source_folder)

	dirs_name=[]
	subdir_name=''
	
	for subdir, dirs, files in os.walk(source_folder):
		dirs_name=dirs
		subdir_name=subdir
		# weirdly keeps looping...
		break;
	# print (dirs_name)
	for direct in dirs_name:
		fullPath=(os.path.join(subdir_name, direct))
		os.system("./gitstats "+fullPath+" "+output_folder+direct)


if __name__ == "__main__":
	generateGitstatsOnFolders()