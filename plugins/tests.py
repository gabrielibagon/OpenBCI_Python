import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from scipy import signal, fft

import csv
import time
import sys
import threading

class Plot():
	'Class used to plot EEG data in real time'

	def __init__(self):
		#pyqtgraph setup
		N = 250
		fs_Hz = 250

		app = QtGui.QApplication([]) #initilizes Qt
		w = QtGui.QWidget()
		layout = QtGui.QGridLayout()
		w.setLayout(layout)
		pg.setConfigOptions(antialias=True)

		f=np.linspace(0,N-1,N)*fs_Hz/N #the y axis
		zeros = np.zeros(N) #the x axis. initially zero

		plotWidget = pg.plot(x=f[0:60], y=zeros[0:60])

		plotWidget.setLabel('left','Amplitude','uV')
		plotWidget.setLabel('bottom','Frequency','Hz')
		plotWidget.show()
		Filter.data
		self.update_plot(plotWidget,newData)
		# app.exec_()

	def update_plot(self,plotWidget,fft):
		plotWidget.plot(x=f[0:60],y=self.fft[0:60])



	# buffer_holder = []
	# first_buffer = False

	# #SETUP
	# print("Main window:")
	# app.exec_()
	# time.sleep(1)

	# def __init__(self):
	# 	print("initializing..")
	# 	self.fs_Hz = 250 #sample rate in Hz


class Streamer:
	'Streamer object to simulate EEG data streaming'

	def __init__(self,fs_Hz):
		self.fs_Hz = fs_Hz
		self.buffer_holder = []
		self.FIRST_BUFFER = True

	def file_input(self):
		channel_data = []
		time_data = []
		with open('sample.txt', 'r') as file:
			reader = csv.reader(file, delimiter=',')
			next(file)
			for line in reader:
				channel_data.append(line[1])

		start = time.time()
		i=0
		for sample in channel_data:
			i+=1
			end = time.time()
			print("EEG TIME: ", i/250, " SECONDS")
			print("Real time: ",end-start)

			if self.FIRST_BUFFER is True:
				self.init_buffer(float(sample))
			else:
				self.sample_buffer(float(sample))
			print("test")
		print("EEG Time: ", len(channel_data)/250)


	#Send for processing

	def init_buffer(self,sample):
		self.buffer_holder = np.append(self.buffer_holder,sample) #isolate channel of interest (ch1)
		if len(self.buffer_holder) == 250: #this is the size of the sample buffer
			# self.buffer_holder = np.asarray(buffer_holder)
			if FILTER is True:
				self.data = filters.receive_data(self.buffer_holder)
			self.FIRST_BUFFER = False

	def sample_buffer(self,sample):
		self.buffer_holder = np.delete(self.buffer_holder, 0)
		self.buffer_holder = np.append(self.buffer_holder,sample)
		if FILTER is True:
			self.data = filters.receive_data(self.buffer_holder)

class Filters:
	'Class containing EEG filtering and analysis tools' 

	#To use, instantiate the class with parameters specifying the type of filter and analysisf.
	#Then, call the Filters.data parameter in order to then get the filtered data


	def __init__(self,fs_Hz,filter_types):
		self.fs_Hz = fs_Hz #setting the sample rate		
		#determine which filters were called
		for type in filter_types:
			if type is "fft":
				#notch and bandpass are pre-requisites for fft
				self.NOTCH = True
				self.BANDPASS = True
				self.FFT = True
			elif type is "notch":
				self.NOTCH = True
			elif type is "bandpass":
				self.BANDPASS = True

	def receive_data(self,data):
		# self.data = data
		if self.NOTCH is True:
			self.notch_filter(data,60)
		if self.BANDPASS is True:
			self.bandpass_filter(data,1,50)
		if self.FFT is True:
			self.fft(data)
		return self.data

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


#Threading
class Thread(pg.QtCore.QThread):
    newData = pg.QtCore.Signal(object)
    def run(self):
        while True:
            data = pg.np.random.normal(size=100)
            # do NOT plot data from here!
            self.newData.emit(data)
            time.sleep(0.05)

# thread = Thread()
# thread.newData.connect(update)
# thread.start()


# lock = threading.Lock() #the Lock object
# PLOTTING = True #check if graph should continue plotting
FILTER = True
streamer = Streamer(250)
filters = Filters(250,['fft'])
streamer.file_input()

# display_plot = Plot()


# display_plot.show()


# test.file_input()