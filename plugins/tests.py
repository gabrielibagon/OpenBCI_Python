import numpy as np
import matplotlib.pyplot as plt
from scipy import signal, fft

import csv
import time
import sys

class Filter_Test():
	N = 250
	fs_Hz = 250
	buffer_holder = []
	first_buffer = False

	#SETUP
	fig = plt.figure()
	ax = fig.add_subplot(111)
	plt.ylim([0,50])
	plt.title('Magnitude spectrum of the signal')
	plt.xlabel('Frequency (Hz)')
	plt.ylabel('Amplitude')
	# plt.yscale('log') #log scale for the y axis
	f=np.linspace(0,N-1,N)*fs_Hz/N #the y axis
	zeros = np.zeros(N) #the x axis. initially zero
	zeros[0] = 1
	li, = ax.plot(f[0:60],zeros[0:60])
	fig.canvas.draw()
	plt.ion()
	plt.show()
	




	# f=np.linspace(0,N-1,N)*fs_Hz/N #the y axis
	# zeros = np.zeros(N) #the x axis. initially zeros
	# print(f)
	# print(zeros)
	# #plot the graph initially
	# li, = ax.plot(f[0:60], zeros[0:60])




	# fftplot = plt.plot(f[0:60],zeros)
	# fftfig = plt.figure()
	# plt.show()


	def __init__(self):
		print("initializing..")



	def file_input(self):
		channel_data = []
		time_data = []
		with open('sample.txt', 'r') as file:
			reader = csv.reader(file, delimiter=',')
			next(file)
			i=0
			for line in reader:
				# print(line[1])
				# print(i)
				# i+=1
				channel_data.append(line[1])
		print("EEG Time: ", len(channel_data)/250)
		start = time.time()
		i=0
		for sample in channel_data:
			i+=1
			end = time.time()
			print("EEG TIME: ", i/250, " SECONDS")
			print("Real time: ",end-start)
			if self.first_buffer is False:
				self.init_buffer(float(sample))
			else:
				self.sample_buffer(float(sample))
		print("EEG Time: ", len(channel_data)/250)

	def init_buffer(self,sample):
		buffer_holder = self.buffer_holder
		self.buffer_holder = np.append(buffer_holder,sample) #isolate channel of interest (ch1)
		if len(buffer_holder) == 250: #this is the size of the sample buffer
			self.buffer_holder = np.asarray(buffer_holder)
			self.processing(self.buffer_holder)
			self.first_buffer = True

	def sample_buffer(self, sample):
		self.buffer_holder = np.delete(self.buffer_holder, 0)
		self.buffer_holder = np.append(self.buffer_holder,sample)
		self.processing(np.asarray(self.buffer_holder))


	def processing(self,channel_buffer):
		############################################
		############################################
		#    			FILTERING 				   #
		############################################
		############################################
		# print(channel_buffer)
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
		fft1 = np.fft.fft(bandpassed_signal)/N #fft computation and normalization
		# # plotting the fft of the filtered signal
		# # f=np.linspace(0,N-1,N)*fs_Hz/N
		# # self.fftplot.plt.plot(f[0:60], abs(fft1[0:60]))
		# self.li.set_ydata(fft1[0:60])
		# self.ax.relim() 
		# self.ax.autoscale_view(True,True,True)
		# self.fig.canvas.draw()
		# print("where is the plot")

		self.li.set_ydata(fft1[0:60])
		self.fig.canvas.show()
		plt.pause(0.00000001)
test = Filter_Test()
N = 250
fs_Hz = 250

test.file_input()