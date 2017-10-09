"""Produces files for mountainsort clustering from rhd files."""
import os
import sys
sys.path.append('C:\\Users\\Alan\\Documents\\GitHub\\mountainlab\\packages\\mlpy\\mda')
import mdaio
import read_rhd as rhd
import numpy as np
import glob
from shutil import copy2
import datetime
import subprocess

def prepFiles(dataPath,basename,probe=None):
    """dataPath is a string that points to the folder containing RHD files.
    basename is the common string that this program will use to generate files related to the sorting project.
    probe is a string describing the probe; currently, 'poly2' and None are accepted
    This function generates a raw.mda file in a allData folder that will be the raw input to mountainsort.
    """
    if probe is not None and probe is not 'poly2':
        raise('probe is not valid')
    ## define additional parameters and paths
    UbuntuShareBase = 'C://Users/Alan/Desktop/UbuntuShare/' ## this is a folder that I have set up to share with my Ubuntu virtualbox
    clusteringPath = 'C://Users/Alan/Documents/Github/clustering-pipelines' ## this is the location of the current file
    
    origDir = os.getcwd()
    os.chdir(dataPath)
    
    sys.path.append(clusteringPath)

    ## batch write .rhd to .dat
    
    # sort files by modification time
    files = glob.glob('*.rhd')
    files.sort(key=os.path.getmtime) ## sort files by modification time, WARNING: may be OS sensitive
    numFiles = len(files)
    
    
    ## make recordings, all data organized in a num_channels X num_samples array
    for i, file in enumerate(files):
        print('/n/n/nExtracting file {0} of {1}: {2}\n'.format(i, numFiles, file))
        d = rhd.read_rhd(file)
        if i == 0:
            recordings = d['amplifier_data']
        else:
            recordings = np.concatenate((recordings, d['amplifier_data']),axis=1)
        
        #save digital input streams
        for digitalChannel in range(d['board_dig_in_data'].shape[0]):
            d['board_dig_in_data'][digitalChannel].tofile(os.path.splitext(file)[0] + 'chan' + str(digitalChannel) + '.di')
        # save analog input streams -- kept in separate files because different recordings may have different #s of channels
        if len(d['aux_input_data']) != 0:
            for analogChannel in range(d['aux_input_data'].shape[0]):
                d['aux_input_data'][analogChannel].tofile(os.path.splitext(file)[0] + 'chan' + str(analogChannel) + '.ai')
    
    if not os.path.exists(dataPath+'/alldata'):
        os.mkdir(dataPath+'/alldata')
    mdaio.writemda16ui('recordings,dataPath+/alldata/raw.mda') # write the recordings array to an mda file; will sort on uint16 array
    del recordings
    
    dt = datetime.datetime.now()
    yearMonthDay = dt.strftime('%Y%m%d')

    UbuntuSharePath = UbuntuShareBase + yearMonthDay + '/' + basename + '/'
    
    if not os.path.exists(UbuntuSharePath):
        os.makedirs(UbuntuSharePath)
    copy2(dataPath+'/alldata/raw.mda',UbuntuSharePath) ## oopies rwa.mda to UbuntuShare folder
    
    allData = np.array([])
    numFiles = len(datFiles)
    for i, file in enumerate(datFiles):
        print('on file',i,'of',numFiles)
        allData = np.concatenate((allData, np.fromfile(file)))
    if not os.path.exists(dataPath+'/allData'):
        os.mkdir(dataPath+'/alldata')
    
    allData.tofile(dataPath+'/alldata/raw.dat')
    print('use this as second dimension when converting to mda file using mdaconvert',int(len(allData)/8))
    
    dt = datetime.datetime.now()
    yearMonthDay =     dt.strftime('%Y%m%d')  
    UbuntuSharePath = 'C://Users/Alan/Desktop/UbuntuShare/'+yearMonthDay+'/'+basename+'/'
    
    if not os.path.exists(UbuntuSharePath):
        os.mkdir(UbuntuSharePath)
    copy2(dataPath+'/alldata/raw.dat',UbuntuSharePath) ## copies raw.dat to UbuntuShare folder
    
    if probe == 'poly2':
        ubuntuLocation = writeUbuntuShell(UbuntuSharePath,basename, probe='poly2')
    else:
        ubuntuLocation = writeUbuntuShell(UbuntuSharePath,basename) # assumes there are 32 channels and does not specify geometry
    stdout,stderr = runUbuntuShell(ubuntuSharePath+'ubuntuRun.bat',ubuntuLocation)
    
def writeUbuntuShell(UbuntuSharePath,basename, probe=None, num_channels=32):
    '''
    Inputs:
    UbuntuSharePath is path of path that is shared with Ubuntu Virtualbox
    basename is the string of the containing folder
    probe is shorthand for a probe: 'poly2' for A1x32-Poly2-5mm-50s-177-A32
    
    Returns:
    string of Ubuntu location of shell
    '''
    oldpath = os.getcwd()
    os.chdir(UbuntuSharePath)
    if probe == 'poly2': # if A1x32-Poly2-5mm-50s-177-A32
        copy2('C://Users/Alan/Documents/Github/clustering-pipelines/poly2Geom.csv',UbuntuSharePath)
        num_channels=32
    dt = datetime.datetime.now()
    yearMonthDay =     dt.strftime('%Y%m%d')  
    sortDir = '/home/alan/data/sortProjects/'+yearMonthDay
    sortDirFull = sortDir+'/datasets/'+basename ## make folder for sortProject with folder name as current date and basename as dataset
    rawMdaLoc = sortDirFull+'/raw.mda'

    with open('datasets%s.txt' % (yearMonthDay) ,'w+') as datasetFile:
        datasetFile.write(basename+' /datasets/'+basename+'\n')
    
    with open('pipelines'+yearMonthDay+'.txt','w+') as pipelineFile:
        pipelineFile.write('ms2alan ms2_alan.pipeline') # default mountainsort pipeline file
    
    with open('params%s.json' % (yearMonthDay) ,'w+') as paramFile:
        if probe == None:
            paramFile.write('{"samplerate":20000,"sign":-1}') # default sample rate is 20 kHz and usually see negative spikes
        elif probe == 'poly2':
            paramFile.write('{"samplerate":20000,"sign":-1,"adjacency_radius":100}')
    with open('tempShell.sh', 'w+', newline='\n') as shellfile: # newline=\n necessary for linux
        shellfile.write('#! /bin/bash -i\n') # including the -i makes the script interactive and this allows for use of default PATH on SSH
        shellfile.write('mkdir -p '+sortDirFull+'\n')
        
        ## convert .dat to .mda, create prv, and copy to datasets
        shellfile.write('cd /media/sf_UbuntuShare/%s/%s\n' % (yearMonthDay,basename)) #directory of shared folder in Ubuntu Virtualbox
        #shellfile.write('/home/alan/mountainlab/bin/mdaconvert raw.dat raw.mda --dtype=uint16 --input_format=raw_timeseries --num_channels=%d\n' % (num_channels)) # convert .dat to .mda
        shellfile.write('/home/alan/mountainlab/bin/prv-create2 raw.mda\n')
        shellfile.write('cp /media/sf_UbuntuShare/%s/%s/raw.mda.prv %s\n' % (yearMonthDay,basename,sortDirFull))
        
        ## copy params.json file to sortDirFull
        
        shellfile.write('cp params%s.json %s/params.json\n' % (yearMonthDay,sortDirFull))
        
        if probe == 'poly2':
            shellfile.write('cp poly2Geom.csv %s/geom.csv\n' % (sortDirFull))

        ## copy datasets.txt and pipelines.txt to sortDir
        shellfile.write('cp datasets%s.txt %s/datasets.txt\n' % (yearMonthDay,sortDir))
        shellfile.write('cp pipelines%s.txt %s/pipelines.txt\n' % (yearMonthDay,sortDir))
        
        ## move to sortDir and run sorting project
        shellfile.write('cd %s\n' % (sortDir))
        shellfile.write('/home/alan/mountainlab/bin/kron-run ms2alan %s --_nodaemon\n' % (basename))
    os.chdir(oldpath)
    return '/media/sf_UbuntuShare/%s/%s/tempShell.sh' % (yearMonthDay, basename)

def runUbuntuShell(batFile, UbuntuShell):
    '''
    UbuntuShell is str with linux style directory of shell file
        this directory is returned from the writeUbuntuShell function
    For alan, that is something like /media/sf_UbuntuShare/DATE/DATABASE/shelltorun.sh
    '''
    pathToVBOXmanage = '"C:/Program Files/Oracle/VirtualBox/VBoxManage.exe"'
    
    with open(batFile,'w+') as file:
        ## change directory to that with share folder
        
        file.write('title run ubuntu shell\n')
        ## start virtual box
        #file.write('call %s startvm "Ubuntu"\n' %(pathToVBOXmanage))
        ## I set up the virtualbox to set the RDONLYHOST property on setup
        ## this wait command waits for that property to change before proceeding
        #file.write('call %s guestproperty wait "Ubuntu" RDONLYHOST\n' %(pathToVBOXmanage))
        
        ## executes the script UbuntuShell
        file.write('call %s guestcontrol "Ubuntu" run --username alan --password 123ubuntubox --exe %s -- --text\n' % (pathToVBOXmanage, UbuntuShell))
        
    p = subprocess.Popen(batFile,shell=True) #run the BAT file.
    stdout, stderr = p.communicate()
    return stdout, stderr
    
    
def main():
    prepFiles(sys.argv[1],sys.argv[2],sys.argv[3])


    
if __name__ == '__main__':
    main()