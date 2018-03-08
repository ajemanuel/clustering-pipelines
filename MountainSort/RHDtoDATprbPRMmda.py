"""Produces files for klusta and mountainsort clustering from rhd files."""
import os
import sys
import read_rhd as rhd
import numpy as np
import glob
from shutil import copy2
import datetime
import subprocess

def RHDtoDATprbPRM(dataPath,basename,probe=None):
    """dataPath is a string that points to the folder containing RHD files.
    basename is the common string that this program will use to generate new .dat and .kwik files.
    probefile is a string describing the probe; currently, 'A1x32-Poly2-5mm-50s-177-A32.prb' , 'Buzsaki32.prb' , and 
    'ASSY-37W-DBC11A-intan.prb' are accepted.
    This function also generates a raw.dat file in the subfolder alldata that can be used for mda conversion and mountainsort.
    """
    if probe is not None and probe is not 'poly2':
        raise('probe is not valid')
        
    clusteringPath = 'C://Users/Alan/Documents/Github/clustering-pipelines'
    
    origDir = os.getcwd()
    os.chdir(dataPath)
    
    sys.path.append(clusteringPath)
    
    ## batch write .rhd to .dat
    
    # sort files by modification time
    files = glob.glob('*.rhd')
    files.sort(key=os.path.getmtime) ## sort files by modification time
    
    for file in files:
        d = rhd.read_rhd(file)
        recordings = np.transpose(d['amplifier_data'])
        stimulation = ()
        #save amplifier data as .dat
        recordings.tofile(os.path.splitext(file)[0] +'.dat')
        #save digital input streams
        for digitalChannel in range(d['board_dig_in_data'].shape[0]):
            d['board_dig_in_data'][digitalChannel].tofile(os.path.splitext(file)[0] + 'chan' + str(digitalChannel) + '.di')
        if len(d['aux_input_data']) != 0:
            for analogChannel in range(d['aux_input_data'].shape[0]):
                d['aux_input_data'][analogChannel].tofile(os.path.splitext(file)[0] + 'chan' + str(analogChannel) + '.ai')

    #create .prm file and copy .prb file to data directory
    datFiles = glob.glob('*.dat')
    datFiles.sort(key=os.path.getmtime)
    
    # copy .prb files to dataPath
    copy2(clusteringPath+'/'+probefile,dataPath)
    
    with open(basename + '.prm', 'w') as text_file:
        text_file.write('experiment_name = \'{0}\' \n'.format(basename))
        text_file.write('prb_file = \'{0}\'\n'.format(probefile))
        text_file.write('traces = dict( \n')
        text_file.write('\traw_data_files={0},\n'.format(datFiles))
        text_file.write('\tvoltage_gain={0}.0,\n'.format(192))  #from Intan RHD2000 documentation
        text_file.write('\tsample_rate={0},\n'.format(d['frequency_parameters']['amplifier_sample_rate']))
        text_file.write('\tn_channels={0},\n'.format(len(d['amplifier_channels'])))
        text_file.write('\tdtype=\'uint16\'\n')
        text_file.write('\t)\n\n')
        
        text_file.write('spikedetekt = dict(\n')
        text_file.write('\tfilter_low=500.,\n') # low pass filter? (as documented in phy)
        text_file.write('\tfilter_high_factor=0.95 * .5,\n') # high pass filter (as documented in phy)
        text_file.write('\tfilter_butter_order=3,\n') # order of Butterworth Filter
        text_file.write('\n')
        text_file.write('\tfilter_lfp_low=20,\n') # LFP filter low-pass frequency
        text_file.write('\tfilter_lfp_high=0,\n') #LFP filter high-pass frequency
        text_file.write('\n')
        text_file.write('\tchunk_size_seconds=1,\n')
        text_file.write('\tchunk_overlap_seconds=.015,\n')
        text_file.write('\n')
        text_file.write('\tn_excerpts=50,\n')
        text_file.write('\texcerpts_size_seconds=1,\n')
        text_file.write('\tthreshold_strong_std_factor=5.5,\n')
        text_file.write('\tthreshold_weak_std_factor=3.5,\n')
        text_file.write("\tdetect_spikes='negative',\n")
        text_file.write('\n')
        text_file.write('\tconnected_component_join_size=1,\n')
        text_file.write('\n')
        text_file.write('\textract_s_before=16,\n')
        text_file.write('\textract_s_after=16,\n')
        text_file.write('\n')
        text_file.write('\tn_features_per_channel=3,\n') #number of features per channel
        text_file.write('\tpca_n_waveforms_max=10000,\n')
        text_file.write(')\n')
        text_file.write('\n')
        text_file.write('klustakwik2 = dict(\n')
        text_file.write('\tnum_starting_clusters=100,\n')
        text_file.write(')\n')
    
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
    
    if probefile == 'A1x32-Poly2-5mm-50s-177-A32.prb':
        writeUbuntuShell(UbuntuSharePath,basename, probe='poly2')
    else:
        writeUbuntuShell(UbuntuSharePath,basename) # assumes there are 32 channels and does not specify geometry
    
    
def writeUbuntuShell(UbuntuSharePath,basename, probe=None, num_channels=32):
    '''
    UbuntuSharePath is path of path that is shared with Ubuntu Virtualbox
    basename is the string of the containing folder
    probe is shorthand for a probe: 'poly2' for A1x32-Poly2-5mm-50s-177-A32
    
    Returns: string of Ubuntu location of shell
    '''
    mdaconvertpath = '/home/alan/mountainlab/bin/mdaconvert'
    prvcreatepath = '/home/alan/mountainlab/bin/prv-create'
    
    
    oldpath = os.getcwd()
    os.chdir(UbuntuSharePath)
    if probe == 'poly2': # if A1x32-Poly2-5mm-50s-177-A32
        copy2('C://Users/Alan/Documents/Github/kwik-tools/poly2Geom.csv',UbuntuSharePath)
        num_channels=32
    dt = datetime.datetime.now()
    yearMonthDay =     dt.strftime('%Y%m%d')  
    sortDir = '/home/alan/data/sortProjects/'+yearMonthDay
    sortDirFull = sortDir+'/datasets/'+basename ## make folder for sortProject with folder name as current date and basename as dataset


    with open('datasets%s.txt' % (yearMonthDay) ,'w+') as datasetFile:
        datasetFile.write(basename+' /datasets/'+basename+'\n')
    
    with open('pipelines'+yearMonthDay+'.txt','w+') as pipelineFile:
        pipelineFile.write('ms2alan ms2_alan.pipeline') # default mountainsort pipeline file
    
    with open('params%s.json' % (yearMonthDay) ,'w+') as paramFile:
        if probe == None:
            paramFile.write('{"samplerate":20000,"sign":-1}') # default sample rate is 20 kHz and usually see negative spikes
        elif probe == 'poly2':
            paramFile.write('{"samplerate":20000,"sign":-1,"adjacency_radius":100}')
    with open('tempShell.sh', 'w+',newline='\n') as shellfile:
        shellfile.write('#! /bin/bash\n')
        shellfile.write('mkdir -p '+sortDirFull+'\n')
        
        ## convert .dat to .mda, create prv, and copy to datasets
        shellfile.write('cd /media/sf_UbuntuShare/%s/%s\n' % (yearMonthDay,basename)) #directory of shared folder in Ubuntu Virtualbox
        shellfile.write('%s raw.dat raw.mda --dtype=uint16 --input_format=raw_timeseries --num_channels=%d\n' % (mdaconvertpath, num_channels)) # convert .dat to .mda
        shellfile.write('%s raw.mda\n' % (prvcreatepath))
        shellfile.write('cp /media/sf_UbuntuShare/%s/%s/raw.mda.prv %s\n' % (yearMonthDay, basename, sortDirFull))
        
        ## copy params.json file to sortDirFull
        
        shellfile.write('cp params%s.json %s/params.json\n' % (yearMonthDay,sortDirFull))
        
        if probe == 'poly2':
            shellfile.write('cp poly2Geom.csv %s/geom.csv\n' % (sortDirFull))

        ## copy datasets.txt and pipelines.txt to sortDir
        shellfile.write('cp datasets%s.txt %s/datasets.txt\n' % (yearMonthDay,sortDir))
        shellfile.write('cp pipelines%s.txt %s/pipelines.txt' % (yearMonthDay,sortDir))
    os.chdir(oldpath)
    return '/media/sf_UbuntuShare/%s/%s/tempShell.sh' % (yearMonthDay, basename)

def runUbuntuShell(UbuntuShell):
    '''
    UbuntuShell is str with linux style directory of shell file
        this directory is returned from the writeUbuntuShell function
    For alan, that is something like /media/sf_UbuntuShare/DATE/DATABASE/shelltorun.sh
    '''
    with open('ubuntuRun.bat','w+') as file:
        ## change directory to that with share folder
        pathToVBOXmanage = '"C:/Program Files/Oracle/VirtualBox/VBoxManage.exe"'
        file.write('title run ubuntu shell\n')
        ## start virtual box
        file.write('call %s startvm "Ubuntu"\n' %(pathToVBOXmanage))
        ## i set up the virtualbox to set the RDONLYHOST property on setup
        ## this wait command waits for that property to change before proceeding
        file.write('call %s guestproperty wait "Ubuntu" RDONLYHOST\n' %(pathToVBOXmanage))
        ## executes the script UbuntuShell
        file.write('call %s guestcontrol "Ubuntu" run --username alan --password 123ubuntubox --exe %s\n' % (pathToVBOXmanage, UbuntuShell))
    p = subprocess.Popen('ubuntuRun.bat',shell=True) #run the BAT file.
    stdout, stderr = p.communicate()
    
    
def main():
    RHDtoDATprbPRM(sys.argv[1],sys.argv[2],sys.argv[3])
    
if __name__ == '__main__':
    main()