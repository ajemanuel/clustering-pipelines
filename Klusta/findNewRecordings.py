import os, sys, time, datetime, glob
from stat import S_ISREG, ST_CTIME, ST_MODE

def findNewRecordings():
	
	#serverDir = r'Z:\HarveyLab\Alan\Data' # map your network drive before running, can do so by typing 'net use Z: \\research.files.med.harvard.edu\Neurobio' into cmd
	serverDir = r'\\research.files.med.harvard.edu\Neurobio\HarveyLab\Alan\Data' #use this and pushd/popd to access the server
	
	entries = (os.path.join(serverDir, fn) for fn in os.listdir(serverDir))
	entries = ((os.stat(path),path) for path in entries)
	entries = ((stat[ST_CTIME], path) for stat, path in entries)
    
	entries2 = []
	for cdate, path in sorted(entries):
		if cdate > (time.time() - (1*3600*24)): # find and extract directories less than 1 day old
			entries2.append((cdate, path))

	origDir = os.getcwd()
	dirList = []
	for cdate, path in entries2:
		os.chdir(path)
		for subdir, dirs, files in os.walk(path):
			for x in files:
				if x.endswith('.rhd'):
					#basename = x[:x.find('_')] ## use this to extract the first part of the filenamme as the basename
					basename = os.path.basename(subdir) ## use this to extract the folder as the basename rather than the filename
					
					if (subdir, basename) not in dirList:
						dirList.append((subdir, basename))
	
	os.chdir(origDir)
	for d in dirList: print(d)
	return dirList

def get_information(directory):
    file_list = []
    for i in os.listdir(directory):
        a = os.stat(os.path.join(directory,i))
        file_list.append([i,time.ctime(a.st_atime),time.ctime(a.st_ctime)]) #[file,most_recent_access,created]
    return file_list
	
def main():
	findNewRecordings()

if __name__ == '__main__':
	main()	