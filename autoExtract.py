import findNewRecordings
import RHDtoDATprbPRM
import os

def autoExtract():
	workingPaths = findNewRecordings.findNewRecordings()
	for path, basename in workingPaths:
		if not(os.path.isfile(path+'/'+basename+'.prm')):
			RHDtoDATprbPRM.RHDtoDATprbPRM(path, basename, 'A1x32-Poly2-5mm-50s-177-A32.prb') # hard coded the poly2 probe for now. This could be improved in the future.


def main():
	autoExtract()

if __name__ == '__main__':
	main()	