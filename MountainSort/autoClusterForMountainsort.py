import findNewRecordings
import mountainsort
import os
import datetime

def autoCluster():
    workingPaths = findNewRecordings.findNewRecordings()
    dt = datetime.datetime.now()
    
    if len(workingPaths) == 0:
        with open('C:\\DATA\\autoClusterLogs\\log'+dt.strftime('%Y%m%d')+'.txt','a') as f2:
            f2.write('No new files found')
    
    for path, basename in workingPaths:
        print(path, basename)
        if not(os.path.isfile(path+'/alldata/raw.mda')):
            mountainsort.prepFiles(path, basename, 'poly2') # This is 'A1x32-Poly2-5mm-50s-177-A32' -- hard-coded
            
            with open('C:\\DATA\\autoClusterLogs\\log'+dt.strftime('%Y%m%d')+'.txt','a') as f2:
                f2.write('New clustering performed: %s %s.\n' % (path, basename))
        else:
            print('already extracted')
            dt = datetime.datetime.now()
            with open('C:\\DATA\\autoClusterLogs\\log'+dt.strftime('%Y%m%d')+'.txt','a') as f2:
                f2.write('Extraction was performed previously.\n')

def main():
    autoCluster()

if __name__ == '__main__':
    main()