def writeHeaderstoNewTSV(fileName,headers):
	"""
	Writes the headers to the first line of the .tsv file

	Args:
		fileName (String): Name of the destination file, ex: "data.tsv"
		headers (List(String)): Headers to be written, ex: ["header1","header2"....]

	"""
	assert fileName[-4:] ==".tsv", "fileName must be '.tsv' file not '%s'" %(fileName)

	f = open (fileName,"w")
	for headerIndex in range(len(headers)):
		if headerIndex!=len(headers)-1:
			# write header along with\t 
			f.write(headers[headerIndex]+"\t")
		else:
			# write last word along with\n
			f.write(headers[len(headers)-1]+"\n")
	f.close()

writeHeaderstoNewTSV("FlaskTest/static/data/commits_by_author.tsv",["date","author1","author2","author3","author4","author5","author6","author7"])
a= open("FlaskTest/static/data/commits_by_author.tsv","r")
print (a.readlines())




# conversion from space to tsv for fallback if all else fails
# sed 's/ /\t/g' file.dat > file.tsv




# ./gitstats ~/Desktop/tony_gitstats/gitstats/Tools_Portal_TESTING/ ~/Desktop/tony_gitstats/gitstats/output_test
