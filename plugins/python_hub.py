import plugin_interface as plugintypes

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal, fft

class PluginPrint(plugintypes.IPluginExtended):
	sample_buffer = []
	fs_Hz = 250.0
	last_mean = 0 #for the processing part
	def activate(self):
		print "Print activated"

		#Globals
		nchan = 8 #default number of channels

		upper_threshold = 25 #default uV upper threshold value
		lower_threshold = 0 #default uV lower threshold value
		average_period = 250 #number of data packs to average over
		threshold_period = 1250 # number of data packets


	
	# called with each new sample
	def __call__(self, sample):
		if sample:
			sample_string = "ID: %f\n%s\n%s" %(sample.id, str(sample.channel_data)[1:-1], str(sample.aux_data)[1:-1])
			#print sample.id
			#sample has the following attributes:
			## sample.id
			## sample.channel_data
			## sample.aux_data

			#Put each sample in a buffer to be analyzed
			self.buffer_holder(sample)

	#holds 250 samples in an array to perform analysis on
	def buffer_holder(self, sample):
		self.sample_buffer.append(sample)
		#if 250 samples have been stored in the buffer, send for analysis
		if len(self.sample_buffer) == 250: #this is the size of the sample buffer
			#EEG_processing(sample_buffer) #send to EEG_processing function
			self.processing(self.sample_buffer)
			self.sample_buffer = [] #clear out the buffer

	def processing(self,sample_buffer):
		fs_Hz = self.fs_Hz
		print fs_Hz


		# Terrible workaround to create a np array for the channel data
		channel_buffer = []
		for sample in sample_buffer:
			channel_buffer.append(sample.channel_data[2]) #isolate channel of interest (ch1)
		channel_buffer = np.asarray(channel_buffer)
		############################################
		############################################
		#    			FILTERING 				   #
		############################################
		############################################

		N = 250 # number of samples we are dealing with

		#############
		# ANALYZE THE FILTERS USING signal.freqz
		#
		# -notch
		# -bandpass

		#############
		# IIR NOTCH FILTER
		#
		# 60 Hz notch filter
		# Sample Rate = 250 Hz
		notch_stop_Hz = np.array([59.0,61.0])
		b, a = signal.butter(2,notch_stop_Hz/(fs_Hz / 2.0), 'bandstop')

		#apply the filter to the stream
		# b,a = output of signa.butter [the numerator and denominator coefficients of the filter]
		# x = input array [the stream]
		notched_signal = signal.lfilter(b,a,channel_buffer)


		# ##############
		# # BANDPASS FILTER
		# # Bandpass for 1-50Hz
		low_cut = 5  #low cut Hz
		high_cut = 25 #high cut Hz
		bandpass_frequencies = np.array([low_cut, high_cut])
		b,a = signal.butter(2, bandpass_frequencies/(fs_Hz / 2.0), 'bandpass')
		bandpassed_signal = signal.lfilter(b,a,channel_buffer)


		# ####################
		# # Hanning Window
		# # aka a hanning taper. This is a filter that tries to taper the data to zero at the edges
		# # 
		# # window = signal.hann()

		####################
		# FFT
		###################
		print("why")
		fft1 = np.fft.fft(bandpassed_signal)
		# plotting the fft of the filtered signal
		f=np.linspace(0,N-1,N)*fs_Hz/N
		plt.clf()
		plt.plot(f[0:60], abs(fft1[0:60]))
		plt.title('Magnitude spectrum of tthe signal')
		plt.xlabel('Frequency (Hz)')
		plt.savefig('hey.png')
		plt.show()
		print("where is the plot")







		# compute the frequency response
		# signal.freqz(b,a,N)
		# Computes the frequency response of a digital filter
		# 	b, a = output of the butterworth function
		#	
		# output:
		#	w = the normalized frequencies at which h was computed, in radians/sample
		#	h = the frequency response
		# w, h = signal.freqz(b,a,1000)
		# f = w * fs_Hz / (2*np.pi)             # convert from rad/sample to Hz
		



		# last_mean = self.last_mean
		# channel_buffer = []
		# current_mean = np.mean(channel_buffer)
		# standard_dev = np.std(channel_buffer) #size of buffer
		# print "Current Mean ", current_mean
		# print "last mean ", last_mean
		# print "variance", standard_dev
		# if np.abs(last_mean - current_mean) > standard_dev:
		# 	print "TRIGGER"
		# self.last_mean = current_mean



	# 	#FFT
	# 	N = 250 #number of sample points
	# 	T = 1.0 / 250 #sample spacing -> 250 samples in 1 second
	# 	x = np.linspace(0.0, N*T, N)
	# 	y = np.sin(50.0*2*np.pi*x) + 0.5*np.sin(80.0 * 2.0*np.pi*x)
	# 	xf = np.linspace(0.0, 1.0/(2.0*T), N/2)
	# 	yf = scipy.fftpack.fft(y)

	# 	fig, ax = plt.subplots()
	# 	ax.plot(xf, 2.0/N * np.abs(yf[:N/2]))
	# 	plt.show()






