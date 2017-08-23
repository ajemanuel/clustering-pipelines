import glob
import re
import numpy as np
import sys

def load_intan_input_channels(matchString='*'):
	#usage:  [di,ai] = load_intan_input_channels() with ai/di files in the path
	#save digital inputs
	p = re.compile('chan(\d+).di')  #extract digital input channel ids
	channel_ids = set(p.findall(' '.join(sorted(glob.glob(matchString+'.di')))))
	#load in each channel and concatenate.
	digital_inputs = {}
	for ch in channel_ids:
		files = sorted(glob.glob(matchString+'chan' + ch + '.di'))
		for f in files:
			print(f)
			if ch in digital_inputs: #concatenation relies on alphabetical ordering corresponding to temporal order
				digital_inputs[ch] = np.append(digital_inputs[ch],(np.fromfile(f, dtype=np.uint32)))
			else:  #load first array
				digital_inputs[ch] = np.fromfile(f, dtype=np.uint32)
	#save analog inputs
	p = re.compile('chan(\d+).ai')  #extract analog input channel ids
	channel_ids = set(p.findall(' '.join(sorted(glob.glob(matchString+'.ai')))))
	#load in each channel and concatenate.
	analog_inputs = {}
	for ch in channel_ids:
		files = sorted(glob.glob(matchString+'chan' + ch + '.ai'))
		for f in files:
			if ch in analog_inputs: #load first array
				analog_inputs[ch] = np.append(analog_inputs[ch],(np.fromfile(f, dtype=np.float64)))  
			else:  #concatenation relies on alphabetical ordering corresponding to temporal order
				analog_inputs[ch] = np.fromfile(f, dtype=np.float64)
	return digital_inputs, analog_inputs