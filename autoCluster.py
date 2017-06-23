import findNewRecordings
import RHDtoDATprbPRM
import os
import subprocess
import datetime

def autoCluster():
	
	dt = datetime.datetime.now()
	
	origDir = os.getcwd() #making sure to keep python in original directory if changing direcotry
	workingPaths = findNewRecordings.findNewRecordings() #get the paths that are written within the last day.
	print(workingPaths)
	## writing a .bat file called tempBAT with instructions for clustering
	with open('C:\\users\\Alan\\Documents\\Github\\kwik-tools\\tempBAT.bat','w+') as f:
		#f.write('@echo off\n')
		f.write('title temp bat for clustering\n')
		#f.write('Z:\n') # change to server drive, after which changing directory cd will work.
		f.write('pushd \\\\research.files.med.harvard.edu\\Neurobio\n') #creates temporary directory where drive letter starts at Neurobio
	
	for path, basename in workingPaths:
		if not (os.path.isfile(path+'/'+basename+'.kwik')):
			print(path)
			#sendString = 'cd '+str(path)+';ls'#activate phy; klusta '+str(basename)+'.prm'
			#print(sendString)
			#subprocess.call(['activate phy'],shell=True, cwd=path) #,'activate phy','klusta '+basename+'.prm'],shell=True)
			print(path)
			print(path[path.find('HarveyLab'):])
			with open('C:\\users\\Alan\\Documents\\Github\\kwik-tools\\tempBAT.bat','a+') as f:
				f.write('cd '+path[path.find('HarveyLab'):]+'\n')
				f.write('klusta '+basename+'.prm --overwrite\n')
			with open('C:\\DATA\\autoClusterLogs\\log'+dt.strftime('%Y%m%d')+'.txt','a+') as f2:
				f2.write('New clustering performed.\n')
		else:
			print('already clustered')

			with open('C:\\DATA\\autoClusterLogs\\log'+dt.strftime('%Y%m%d')+'.txt','a+') as f2:
				f2.write('Clustering was performed previously.\nFile: '+path+'\\'+basename+'.kwik\n')
			
	with open('C:\\users\\Alan\\Documents\\Github\\kwik-tools\\tempBAT.bat','a+') as f:
		#f.write('@echo off\n')
		#f.write('deactivate\n') #deactivate the phy environment
		f.write('popd') # escape temp directory
		
	p = subprocess.Popen('C:\\users\\Alan\\Documents\\Github\\kwik-tools\\tempBAT.bat',shell=True) #run the tempBat file.
	stdout, stderr = p.communicate()

def main():
	autoCluster()

if __name__ == '__main__':
	main()	