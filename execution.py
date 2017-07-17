import os
import sys
import glob
from xml.etree import ElementTree

# NOTE: this files needs to be in same directory as gitstats executable
# python execution.py <source_folder> <output_folder>

def generateGitstatsOnFolders (): 
	#  root location
	source_folder = sys.argv[1]
	# final destination
	output_folder_path = sys.argv[2]
	print (source_folder)

	dirs_name=[]
	subdir_name=''
	
	for subdir, dirs, files in os.walk(source_folder):
		dirs_name=dirs
		subdir_name=subdir
		# weirdly keeps looping...
		break;
	# print (dirs_name)
	for directory in dirs_name:
		fullPath=(os.path.join(subdir_name, directory))
		os.system("./gitstats "+fullPath+" "+output_folder_path+"/"+directory)


def gitDirectoryExists(path):
	'''Checks if .git directory exists in <path> directory

	Returns True if there is .git directory, else False
	'''
	assert (os.path.isdir(path)), "This directory doesnt exist!" 

	search_path=os.path.join(path,".git")
	pos_git_directory = glob.glob(search_path)
	print ("\nSearching for .git directories in %s" %(path))

	if pos_git_directory==[search_path]:
		print ("\n.git Directory found at %s" %(search_path) )
		return True
	else: 
		print ("\nNo .git directory found in  %s" %(path) )
		return False

def parseXML(manifestPath):
	'''Parse manifest.xml and return and array of git repos'''
	with open(manifestPath, 'rt') as f:
	    tree = ElementTree.parse(f)

	gitPaths=[]
	for node in tree.iter('project'):
	    git_path = node.attrib.get('path')
	    print (git_path)
	    gitPaths.append(git_path)

	for path in gitPaths:
		runGitstats(path, "bleh")


def runGitstats(pathsArr):
	''' Runs gitstats on each of <pathsArr>, into output directory <output>
	This file should be in the same directory as the gitstats executable'''
	output_dir=sys.argv[2]
	for path in pathsArr:
		if gitDirectoryExists(path):
			os.system("./gitstats "+os.path.join("/home/gschultz/8956n/.repo/projects",path)+" "+output_dir)

	os.system("./gitstats " +path)


def repoController(manifest_path):
	gitPaths=parseXML(manifest_path)

if __name__ == "__main__":
	manifest_location=sys.argv[1] 
	repoController(manifest_location)
	# parseXML()
	# gitDirectoryExists("C:\Users\GSCHULTZ\Desktop\gitstats\output")
	# generateGitstatsOnFolders()






