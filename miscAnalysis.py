# A collection of analyses that I routinely perform on silicon probe recordings.

import scipy.io
import numpy as np
import re
import glob
import os
import matplotlib.pyplot as plt

def importJRCLUST(filepath, annotation='single'):
    """
    Imports the features of the JrClust output I use most.
    
    inputs:
        filepath - str with path to S0 filename
        annotation - str that indicates which spikes to include 'single' or 'multi'
            -- in the future, increase this functionality
        
    output: Dict with keys
        goodSpikes - ndarray of clusters
        goodSamples - ndarray of spike samples
        sampleRate - int sample rate in Hz
    """
    outDict = {}

    S0 = scipy.io.loadmat(filepath,squeeze_me=True, struct_as_record=False)
    
    spikeAnnotations = S0['S0'].S_clu.csNote_clu
    
    annotatedUnits = np.where(spikeAnnotations == 'single')[0]+1 # +1 to account for 1-indexing of jrclust output; jrc spikes that = 0 are not classified
    
    goodSamples = S0['S0'].viTime_spk
    goodSpikes = S0['S0'].S_clu.viClu
    
    goodSamples = goodSamples[np.isin(goodSpikes,annotatedUnits)]
    goodSpikes = goodSpikes[np.isin(goodSpikes,annotatedUnits)]
    
    outDict['sampleRate'] = S0['S0'].P.sRateHz
    outDict['goodSamples'] = goodSamples
    outDict['goodSpikes'] = goodSpikes
    outDict['goodTimes'] = goodSamples/S0['S0'].P.sRateHz
    
    return outDict
    
    

def importDImat(filepath):
    """
    Imports digital inputs saved as '*DigitalInputs.mat'
    
    input:
        filepath - str with directory containing files
    
    output:
        DI0, ndarray with digital channel 0
        DI1, ndarray with digital channel 1
    """
    
    diFiles = glob.glob(filepath+'*DigitalInputs.mat')
    diFiles.sort(key=os.path.getmtime)
    #diFiles.sort(key=lambda l: grp('[0-9]*D',l)) # regular expression finding string of numbers before D
    
    DI0 = [] ## only two digital inputs with the recording controller, should make this more adaptable in the future
    DI1 = []
    
    for file in diFiles:
        print(file)
        temp = scipy.io.loadmat(file)
        DI0.append(temp['board_dig_in_data'][0])
        DI1.append(temp['board_dig_in_data'][1])
    DI0 = np.concatenate(DI0)
    DI1 = np.concatenate(DI1)
    return DI0, DI1
    
def plotStimRasters(stimulus, samples, spikes, unit, ltime, rtime, save=False, baseline=0, sample_rate=20000, fig_size=(10,4),
        heightRatio=[1,4]):
    """
    Generate plots with stimulus displayed at top and rasters below for individual units.
    
    inputs:
        stimulus - list of ndarrays, stimulus waveform
        samples - list of ndarrays, spike times in samples
        spikes - list of ndarrays, cluster identity for each spike
        unit - int, unit to include in raster
        save - boolean, save plot to disk, default=False
        baseline - float, time before first stimulus in s, default=0.0
        sample_rate - int, sample rate in Hz, default=20000
        fig_size - tuple, ratio of width to length
        heightRatio - list, ratio of heights of stimulus and raster plots
        
    generates a plot; no outputs
    """
    
    # Plot stimulus waveform
    f, (a0, a1) = plt.subplots(2,1,gridspec_kw={'height_ratios':heightRatio},figsize=fig_size)
    xaxis = np.arange(ltime-baseline,rtime-baseline,1/sample_rate)
    for i, sweep in enumerate(stimulus):
        a0.plot(xaxis,sweep[int(sample_rate*ltime):int(sample_rate*rtime)],linewidth=.5,color='gray') # add +5*i to the y axis to get separate traces
    topxlim = a0.get_xlim()
    a0.set_title('Unit '+str(unit))
    a0.set_xticks([])

    # Plot Rasters
    for sweep in range(len(samples)):
        sweepspikes = spikes[sweep][spikes[sweep]==unit]
        sweepsamples = samples[sweep][spikes[sweep]==unit]
        sweepspikes = sweepspikes[(sweepsamples > ltime*sample_rate) & (sweepsamples < rtime*sample_rate)]
        sweepsamples = sweepsamples[(sweepsamples > ltime*sample_rate) & (sweepsamples < rtime*sample_rate)]
        a1.plot(sweepsamples/sample_rate-baseline,(sweepspikes+sweep-unit),'|',color='gray',markersize=2,mew=.5)
    a1.set_xlim(topxlim)
    a1.set_xlabel('Time (s)')
    a1.set_ylabel('Step #')
    plt.tight_layout()

    if save:
        plt.savefig('unit'+str(unit)+'gridSteps.png',transparent=True)
    plt.show()
    plt.close()    
    
def makeSweepPSTH(bin_size, samples, spikes,sample_rate=20000):
    """
    Use this to convert spike time rasters into PSTHs with user-defined bin
    
    inputs:
        bin_size - float, bin size in seconds
        samples - list of ndarrays, time of spikes in samples
        spikes- list of ndarrays, spike cluster identities
        sample_rate - int, Hz, default = 20000
        
    output: dict with keys:
        psths - ndarray
        bin_size - float, same as input
        sample_rate - int, same as input
        xaxis - ndarray, gives the left side of the bins
        units - ndarray, units included in psth
    """
    
    bin_samples = bin_size * sample_rate
    
    maxBin = max(np.concatenate(samples))/sample_rate    
    
    units = np.unique(np.hstack(spikes))
    numUnits = len(units)
    
    psths = np.zeros([int(np.floor(maxBin/bin_size))+1, numUnits])
    print('psth size is',psths.shape)
    psth_dict = {}
    for i in range(len(samples)):
        for stepSample, stepSpike in zip(samples[i], spikes[i]):
            psths[int(np.floor(stepSample/bin_samples)), np.where(units == stepSpike)[0][0]] += 1
    psth_dict['psths'] = psths/bin_size/len(samples) # in units of Hz
    psth_dict['bin_size'] = bin_size # in s
    psth_dict['sample_rate'] = sample_rate # in Hz
    psth_dict['xaxis'] = np.arange(0,maxBin,bin_size)
    psth_dict['units'] = units
    return psth_dict
    
    
    
    
### functions regarding indentOnGrid

def plotActualPositions(filename, setup='alan', offset=(9,9), labelPositions=True):
    """
    Plot locations of grid indentation.
    
    inputs:
        filename - str, file containing indentOnGrid output
        setup - str, specifies which setup used, specified because some x and y stages are transposed
            current options: 'alan'
        offset - tuple, specifies offset of center points
        labelPositions - boolean, label order of the positions with text annotations
        
    No output, generates plots.
    """
    
    gridIndent = scipy.io.loadmat(filename)
    try:
        gridPosActual = gridIndent['grid_positions_actual']
    except KeyError:
        print('File not from indentOnGrid')
        return -1
    gridPosActual = np.transpose(gridPosActual)
    
    # plotting
    
    if setup == 'alan':
        xmultiplier = -1  ## my stage is transposed in x
        ymultiplier = -1  ## my stage is transposed in y
    else:
        xmultiplier = 1
        ymultiplier = 1
    
    a0 = plt.axes()
    a0.scatter(gridPosActual[0][0]*xmultiplier+offset[0],gridPosActual[0][1]*ymultiplier+offset[1],s=1500,marker='.')
    
    if labelPositions:
        for i,pos in enumerate(np.transpose(gridPosActual[0])):
            #print(pos)
            a0.annotate(str(i+1),(pos[0]-offset[0],pos[1]-offset[0]),
                horizontalalignment='center',
                verticalalignment='center',
                color='white',
                weight='bold')
    
    a0.set_ylabel('mm')
    a0.set_xlabel('mm')
    a0.set_aspect('equal')
    
    
def plotGridResponses(filename, windowOnset, windowDur, samples, spikes, units='all', numRepeats=3, numSteps=1, sampleRate=20000, save=False, force=0, center=True):
    """
    Plots each unit's mechanical spatial receptive field.
    Inputs:
    filename - str, .mat filename produced by indentOnGrid
    windowOnset - time of windowOnset in sweep in s
    windoDur - duration of window in s
    samples - list of samples at which spikes are detected for each sweep
    spikes - list of spike IDs corresponding to samples in goodsamples_sweeps
    units - list of units to plot or str = 'all'
    sampleRate = sample rate in Hz, defaults to 20000
    
    Output is a plot.
    """
    gridIndent = scipy.io.loadmat(filename)
    try:
        gridPosActual = gridIndent['grid_positions_actual'] # 
        gridPosActual = np.transpose(gridPosActual)
        if numRepeats > 1:        
                gridPosActual = gridPosActual[0] # taking the first grid positions here -- perhaps change this in the future
    except KeyError:
        print('File not from indentOnGrid')
        return -1
    offsetx = np.median(gridPosActual[0][0])
    offsety = np.median(gridPosActual[0][1])
    offsets = (offsetx, offsety)
    
    gridSpikes = extractSpikesInWindow(windowOnset, windowDur, samples, spikes, sampleRate=sampleRate)
    
    if type(units) is not str: # untis != 'all'
        for unit in units:
            positionResponses = generatePositionResponses(gridPosActual, gridSpikes, numRepeats=numRepeats, numSteps=numSteps, unit=unit)
            plotPositionResponses(positionResponses, gridPosActual, force=force, save=save, unit=unit, center=center)
    else:
        positionResponses = generatePositionResponses(gridPosActual, gridSpikes, numRepeats=numRepeats, numSteps=numSteps)
        plotPositionResponses(positionResponses, gridPosActual, force=force, save=save, center=center)
    
def extractSpikesInWindow(windowOnset, windowDur, samples, spikes, sampleRate=20000):
    """
    Inputs:
    windowOnset = time of windowOnset in sweep in s
    windoDur = duration of window in s
    samples = list of samples at which spikes are detected for each sweep
    spikes = list of spike IDs corresponding to samples in goodsamples_sweeps
    sampleRate = sample rate in Hz, defaults to 20000
    
    Returns:
    spikesOut - list of spikes in that window for each sweep
    
    """
    windowOnsetinSamples = windowOnset*sampleRate # in samples
    windowDurinSamples =  windowDur*sampleRate # in samples
    spikesOut = []
    i = 0
    for spikeSample, spike in zip(samples,spikes):
        i += 1
        spikesOut.append((spikeSample[(spikeSample > windowOnsetinSamples) & (spikeSample < windowOnsetinSamples + windowDurinSamples)],
                         spike[(spikeSample > windowOnsetinSamples) &  (spikeSample < windowOnsetinSamples + windowDurinSamples)]))
        #plt.plot(spikeSample[(spikeSample > windowOnsetinSamples) & (spikeSample < windowOnsetinSamples + windowDurinSamples)],
        #         spike[(spikeSample > windowOnsetinSamples) & (spikeSample < windowOnsetinSamples + windowDurinSamples)],'|')
    return spikesOut
    
def generatePositionResponses(gridPosActual, spikes, numRepeats=3, numSteps = 1, unit=None):

    gridPosActualAll = np.transpose(gridPosActual)
    gridPosActualAll = np.matlib.repmat(gridPosActualAll,numRepeats,1)

    positionIndex = np.arange(len(np.transpose(gridPosActual)))
    positionIndex = np.matlib.repmat(positionIndex,numSteps,numRepeats)
    
    if numSteps > 1:
        positionIndex = np.transpose(positionIndex)
        positionIndex = positionIndex.reshape(positionIndex.shape[0]*positionIndex.shape[1])
    
            
    positionResponse = {}

    if unit:
        print('Extracting position responses for unit {0}'.format(unit))
        for sweep, index in zip(spikes,positionIndex):
            positionResponse[index] = positionResponse.get(index,0) + len(sweep[1][sweep[1]==unit])
            #print('\n position {0}'.format(index))
    else:
        print('Extracting position responses for all units')
        for sweep, index in zip(spikes, positionIndex):
            #print('\n position {0}'.format(index))
            #print('newspikes:',len(sweep[1]))
            #print('oldspikes:',positionResponse.get(index,0))
            positionResponse[index] = positionResponse.get(index,0) + len(sweep[1]) #[sweep[1]==unit])
                
    positionResponses = []
    for index in positionResponse.keys():
        positionResponses.append([index, positionResponse[index]])

    return positionResponses


def plotPositionResponses(positionResponses, gridPosActual, maxSpikes=None, force=0, save=False, unit=None, setup='alan', center=True):
    """
    plotting function for spatial receptive fields
    
    inputs
    positionResponses (from generatePositionResponses)
    force in mN for titling and savename of graph
    
    output: plot
    f0 is the plot handle
    """
    if setup == 'alan': # my axes are transposed
        xmultiplier = -1
        ymultiplier = -1
    else:
        xmultiplier = 1
        ymultiplier = 1
    if center:
        xOffset = int(round(np.median(gridPosActual[0])))
        #print('xOffset = {0}'.format(xOffset))
        yOffset = int(round(np.median(gridPosActual[1])))
        #print('yOffset = {0}'.format(yOffset))
    
    f0 = plt.figure()
    a0 = plt.axes()
    sc = a0.scatter(gridPosActual[0]*xmultiplier+xOffset,gridPosActual[1]*ymultiplier+yOffset,c=np.transpose(positionResponses)[1], s=300, cmap='viridis', vmin=0,vmax=maxSpikes)
    a0.set_aspect('equal')
    a0.set_xlabel('mm')
    a0.set_ylabel('mm')
    if unit:
        a0.set_title('Unit %d, %d mN'%(unit, force))
    else:
        a0.set_title('{0} mN'.format(force))
    cb = f0.colorbar(sc)
    cb.set_label('spikes')
    f0.tight_layout()
    if save: plt.savefig('positionResponse{0}mN.png'.format(force),transparent=True)


    
    
### helper functions below

def grp(pat, txt):
    r = re.search(pat, txt)
    return r.group(0) if r else '%'