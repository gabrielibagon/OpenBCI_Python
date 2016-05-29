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

	#set up canvas for fft
	fig = plt.figure()
	fig,ax = fig.add_subplot(1,1)
	ax.hold = True
	f=np.linspace(0,N-1,N)*fs_Hz/N #the y axis
	zeros = np.zeros(N) #the x axis. initially zero

	rw = randomwalk()
	f,zeros = rw.next()

	plt.show(False)
	plt.draw()

	background = fig.canvas.copy_from_bbox(ax.bbox)

	points = ax.plot(f,zeros)






	# f=np.linspace(0,N-1,N)*fs_Hz/N #the y axis
	# zeros = np.zeros(N) #the x axis. initially zeros
	# print(f)
	# print(zeros)
	# #plot the graph initially
	# li, = ax.plot(f[0:60], zeros[0:60])
	# plt.title('Magnitude spectrum of tthe signal')
	# plt.xlabel('Frequency (Hz)')



	# fftplot = plt.plot(f[0:60],zeros)
	# fftfig = plt.figure()
	# plt.show()


	def __init__(self):
		print("initializing..")



	def file_input(self):
		channel_data = []
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
		for sample in channel_data:
			time.sleep(0.004)
			if self.first_buffer is False:
				self.init_buffer(float(sample))
			else:
				self.sample_buffer(float(sample))

		end = time.time()
		print("EEG Time: ", len(channel_data)/250)
		print("Python time: ",end-start)

	def init_buffer(self,sample):
		buffer_holder = self.buffer_holder
		self.buffer_holder = np.append(buffer_holder,sample) #isolate channel of interest (ch1)
		if len(buffer_holder) == 250: #this is the size of the sample buffer
			self.buffer_holder = np.asarray(buffer_holder)
			self.processing(self.buffer_holder)
			self.first_buffer = True

	def sample_buffer(self, sample):
		# Terrible workaround to create a np array for the channel data
		print(self.buffer_holder)
		self.buffer_holder = np.delete(self.buffer_holder, 0)
		self.buffer_holder = np.append(self.buffer_holder,sample)
		self.processing(np.asarray(self.buffer_holder))


	def processing(self,channel_buffer):
		############################################
		############################################
		#    			FILTERING 				   #
		############################################
		############################################
		print(channel_buffer)
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
		# fft1 = np.fft.fft(bandpassed_signal)
		# # plotting the fft of the filtered signal
		# # f=np.linspace(0,N-1,N)*fs_Hz/N
		# # self.fftplot.plt.plot(f[0:60], abs(fft1[0:60]))
		# self.li.set_ydata(fft1[0:60])
		# self.ax.relim() 
		# self.ax.autoscale_view(True,True,True)
		# self.fig.canvas.draw()
		# print("where is the plot")

		self.fig.canvas.restore_region(self.background)
		self.ax.draw_artist(points)

test = Filter_Test()
N = 250
fs_Hz = 250

test.file_input()