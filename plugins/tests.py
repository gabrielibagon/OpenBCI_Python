import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from scipy import signal, fft

import csv
import time
import sys

class Plot():
	'Class used to plot EEG data in real time'

	def __init__():
		#pyqtgraph setup
		app = QtGui.QApplication([]) #initilizes Qt
		w = QtGui.QWidget()
		layout = QtGui.QGridLayout()
		w.setLayout(layout)
		# plotWidget = pg.plot(x=f[0:60], y=zeros[0:60])
		plotWidget.setLabel('left','Amplitude','uV')
		plotWidget.setLabel('bottom','Frequency','Hz')

	def update_plot():


	N = 250
	fs_Hz = 250
	buffer_holder = []
	first_buffer = False

	#SETUP
	f=np.linspace(0,N-1,N)*fs_Hz/N #the y axis
	zeros = np.zeros(N) #the x axis. initially zero
	print("Main window:")
	app.exec_()
	time.sleep(1)

	def __init__(self):
		print("initializing..")
		self.fs_Hz = 250 #sample rate in Hz


class Streamer:
	'Streamer object to simulate EEG data streaming'

	def __init__(self,fs_Hz,processing):
		self.fs_Hz = fs_hz
		self.processing = processing

	def file_input(self):
		channel_data = []
		time_data = []
		with open('sample.txt', 'r') as file:
			reader = csv.reader(file, delimiter=',')
			next(file)
			i=0
			for line in reader:
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

class Filters:
	'Class containing EEG filtering and analysis tools' 

	#To use, instantiate the class with parameters specifying the type of filter and analysisf.
	#Then, call the Filters.data parameter in order to then get the filtered data


	def __init__(self,data,fs_Hz,filter_types):
		self.fs_Hz = fs_Hz #setting the sample rate
		self.data = data #the current data being processed
		
		#determine which filters were called
		for type in filters:
			if type is "fft":
				#notch and bandpass are pre-requisites for fft
				notch_filter(self,data)
				bandpass_filter(self,data)
				fft(self,data)
				break #no more filters are needed if fft is performed
			elif type is "notch":
				notch_filter(self,data)
			elif type is "bandpass":
				bandpass_filter(self,data)


	def notch_filter(self,data,notch_Hz=60):
		notch_Hz = np.array([float(notch_Hz - 1.0), float(notch_Hz + 1.0)])
		b, a = signal.butter(2,notch_Hz/(self.fs_Hz / 2.0), 'bandstop')

		#apply the filter to the stream
		self.data = signal.lfilter(b,a,data)


	def bandpass_filter(self,data,low_cut,high_cut):
		bandpass_frequencies = np.array([low_cut, high_cut])
		b,a = signal.butter(2, bandpass_frequencies/(self.fs_Hz / 2.0), 'bandpass')
		
		#apply filter to stream, update data with filtered signal
		self.data = signal.lfilter(b,a,data)


	####################
	# Hanning Window
	# aka a hanning taper. This is a filter that tries to taper the data to zero at the edges
	# 
	# window = signal.hann()

	def fft(self,data):
		self.data = np.fft.fft(data)/(self.fs_Hz) #fft computation and normalization



test = Filters()
data = test.data()
test.file_input()