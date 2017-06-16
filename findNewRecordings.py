import os, sys, time, datetime, glob
from stat import S_ISREG, ST_CTIME, ST_MODE

def findNewRecordings():
	
	serverDir = r'Z:\HarveyLab\Alan\Data' # to map your network drive, open cmd, type 'pushd \\research.files.med.harvard.edu\Neurobio'
	
	entries = (os.path.join(serverDir, fn) for fn in os.listdir(serverDir))
	entries = ((os.stat(path),path) for path in entries)
	entries = ((stat[ST_CTIME], path)
				for stat, path in entries)
	entries2 = []
	for cdate, path in sorted(entries):
		if cdate > (time.time() - (3600*24)): # find directories less than 1 day old
			entries2.append((cdate, path))

	origDir = os.getcwd()
	dirList = []
	for cdate, path in entries2:
		os.chdir(path)
		for subdir, dirs, files in os.walk(path):
			for x in files:
				if x.endswith('.rhd'):
					basename = x[:x.find('_')]
					if (subdir, basename) not in dirList:
						dirList.append((subdir, basename))
	
	os.chdir(origDir)
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