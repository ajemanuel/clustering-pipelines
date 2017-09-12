"""Produces files for klusta clustering from rhd files."""
import os
import sys
import read_rhd as rhd
import numpy as np
import glob
from shutil import copy2

def RHDtoDATprbPRM(dataPath,basename,probefile):
	"""dataPath is a string that points to the folder containing RHD files.
	basename is the common string that this program will use to generate new .dat and .kwik files.
	probefile is a string describing the probe; currently, 'A1x32-Poly2-5mm-50s-177-A32.prb' , 'Buzsaki32.prb' , and 
	'ASSY-37W-DBC11A-intan.prb' are accepted.
	"""
	if probefile != 'A1x32-Poly2-5mm-50s-177-A32.prb' and probefile != 'Buzsaki32.prb' and probefile != 'ASSY-37W-DBC11A-intan.prb':
		print('Probe file is not valid')
		return(-1)
	
	print('Generating .dat and .prm files with probe',probefile)
	
	kwikToolsPath = 'C://Users/Alan/Documents/Github/kwik-tools'
	
	origDir = os.getcwd()
	os.chdir(dataPath)
	
	sys.path.append(kwikToolsPath)
	
	## batch write .rhd to .dat
	
	# sort files by modification time
	files = glob.glob('*.rhd')
	files.sort(key=os.path.getmtime)
	
	for file in files:
		d = rhd.read_rhd(file)
		recordings = np.transpose(d['amplifier_data'])
		stimulation = ()
		#save amplifier data as .dat
		recordings.tofile(os.path.splitext(file)[0] +'.dat')
		#save digital input streams
		for digitalChannel in range(d['board_dig_in_data'].shape[0]):
			d['board_dig_in_data'][digitalChannel].tofile(os.path.splitext(file)[0] + 'chan' + str(digitalChannel) + '.di')
		for analogChannel in range(d['aux_input_data'].shape[0]):
			d['aux_input_data'][analogChannel].tofile(os.path.splitext(file)[0] + 'chan' + str(analogChannel) + '.ai')

	#create .prm file and copy .prb file to data directory
	datFiles = glob.glob('*.dat')
	datFiles.sort(key=os.path.getmtime)
	
	# copy .prb files to dataPath
	copy2(kwikToolsPath+'/'+probefile,dataPath)
	
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
		
def main():
	RHDtoDATprbPRM(sys.argv[1],sys.argv[2],sys.argv[3])
	
if __name__ == '__main__':
	main()