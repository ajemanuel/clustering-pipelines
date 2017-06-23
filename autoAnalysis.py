import matplotlib.pyplot as plt
import h5py
import glob
import numpy as np
import scipy.io
import sys
import os
sys.path.append(r'C:\Users\Alan\Documents\Github\kwik-tools')
import read_rhd as rhd
import klusta
import load_intan_input_channels as liic
from klusta.kwik import KwikModel

def autoAnalysis(kwik_fullpath):
	model = KwikModel(kwik_fullpath)
	kwikPath,kwikFile = os.path.split(kwik_fullpath) 
	allsamples = []
	allspikes = []
	for j in model.channel_groups: # for statement walks through different channel_groups (i.e., those on different shanks)
		model.channel_group = j

		samples = model.spike_samples
		spikes = model.spike_clusters
		
		for i,n in enumerate(spikes):
			allsamples.append(samples[i])
			allspikes.append(spikes[i])

	alltimes = np.array(allsamples)/model.sample_rate
	allspikes = np.array(allspikes)
	
	
	#plt.figure(figsize=(15,5))
	#plt.plot(alltimes, allspikes, '|',mew=.5,color=[.5,.5,.5])
	#plt.savefig(kwikPath+'\\allSpikes.png')
	
	[di, ai] = liic.load_intan_input_channels()
	intan_trigger = di['0'][:]
	intan_camera = di['1'][:]
	
	intan_transitions = np.where(intan_trigger[:-1] != intan_trigger[1:])[0]
	
	adjustmentAmount = (intan_transitions[0])
	
	[matlab_trigger, matlab_triggerCMD, matlab_brush] = loadMatlabFile(adjustmentAmount)
	
	plt.figure(figsize=(15,10))
	plt.subplot(211)
	plt.plot(alltimes, allspikes, '|',color =[.5,.5,.5],markersize=5,mew=.4)
	plt.ylabel('unit')
	topxlim = plt.xlim()
	plt.xlim(topxlim)
	plt.subplot(212)
	plt.plot(np.arange(0,len(matlab_brush)/20000,1/20000),matlab_brush,color = [.5,.5,.5],linewidth=.5)
	plt.savefig(kwikPath+'\\brushSpikes.png')
	
	
	
def loadMatlabFile(adjlist):
	
	matlab_sync = []
	matlab_cameraTrigger = []
	matlab_trigger = []
	matlab_triggerCMD = []
	
	matlabFiles = glob.glob('acquire*.mat')
	for file in matlabFiles:
		temp = scipy.io.matlab.loadmat(file)
		if temp['stimulus'] == 'acquireIntanBrush':
			matlab_trigger.append(np.zeros(adjlist[i]))
			matlab_triggerCMD.append(np.zeros(adjlist[i]))
			matlab_brush.append(np.zeros(adjlist[i]))
			
			matlab_trigger.append(temp['data'][:,0])
			matlab_triggerCMD.append(temp['trigger'][:,0])
			matlab_brush.append(temp['data'][:,1])
			
			matlab_trigger = np.concatenate(matlab_trigger)
			matlab_triggerCMD = np.concatenate(matlab_triggerCMD)
			matlab_brush = np.concatenate(matlab_brush)
			
			return [matlab_trigger, matlab_triggerCMD, matlab_brush]
			
		if temp['stimulus'] == 'acquireIntanBrushCamera':
			matlab_trigger.append(np.zeros(adjlist[i]))
			matlab_triggerCMD.append(np.zeros(adjlist[i]))
			matlab_brush.append(np.zeros(adjlist[i]))
			matlab_cameraTrigger.append(np.zeros(adjlist[i]))
			
			matlab_trigger.append(temp['data'][:,0])
			matlab_triggerCMD.append(temp['trigger'][:,0])
			matlab_brush.append(temp['data'][:,1])
			matlab_cameraTrigger.append(temp['cameratrigger'][:,0])
			
			matlab_trigger = np.concatenate(matlab_trigger)
			matlab_triggerCMD = np.concatenate(matlab_triggerCMD)
			matlab_brush = np.concatenate(matlab_brush)			
			matlab_cameraTrigger = np.concatenate(matlab_cameraTrigger)
			
			
			matlab_cameraTrigger[matlab_cameraTrigger < 1.5] = 0
			matlab_cameraTrigger[matlab_cameraTrigger > 1.5] = 1
			
			return [matlab_trigger, matlab_triggerCMD, matlab_brush, matlab_cameraTrigger]
			
			
			
def main():
	autoAnalysis(sys.argv[1])
	
if __name__ == '__main__':
	main()