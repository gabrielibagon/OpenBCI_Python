import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
#PyQt version 4.11.4
from PyQt4.QtCore import QThread, pyqtSignal, pyqtSlot, SIGNAL
import window
from scipy import signal, fft

import csv
import time
import sys
import threading


class Plot(QtGui.QMainWindow, window.Ui_MainWindow):
	'Class used to plot EEG data in real time'

	def __init__(self, streamer, parent=None):
		#pyqtgraph setup
		global form
		global new_data
		self.processed_data = []
		self.streamer = streamer
		self.N = 250
		self.fs_Hz = 250
		self.data = []
		self.f = np.linspace(0,self.N-1,self.N)*self.fs_Hz/self.N #the y axis		
		self.last_data_window = []


		# SETUP THE GUI
		# initialization
		super(self.__class__,self).__init__()
		self.setupUi(self)
		self.canvas = self.graphicsView #canvas is of the type pyqtplot.PlotWidget
		self.p1 = self.canvas.plot()

		# PARAMETERS FOR PLOT
		self.canvas.setLabel('left','Amplittude','uV')
		self.canvas.setLabel('bottom','Frequency','Hz')
		self.canvas.setWindowTitle('Magnitude spectrum of the signal')
		self.canvas.setXRange(0,60)
		self.canvas.setYRange(-1.5,2)
		self.canvas.setLogMode(y=True)
		self.canvas.disableAutoRange()


		streamer.new_data.connect(self.plot_data)

		self.pushButton.clicked.connect(lambda: self.start_streamer())
		
	def start_streamer(self):
		self.streamer.run()

	@pyqtSlot(np.ndarray)
	def plot_data(self,data):
		global app
		print(data)
		data = self.smoothing(data)
		print(data)
		self.p1.setData(x=self.f[0:60],y=data[0:60])
		app.processEvents()
		print("Sup friend")

	# Function used to smooth the fft plot
	def smoothing(self,data):
		last_data_window = self.last_data_window
		# if this is the first data window being plotted
		if len(last_data_window) == 0:
			self.last_data_window = data #set this up for the next window
			print("wot")
			return data #return without being smoothed
		#else, average last_data_window with current data
		else:
			self.last_data_window = data
			# ***USING THIS IMPLEMENTATION DEFAULTS TO 50/50 SMOOTHING
			# THAT IS .5 ON THE PROCESSING GUI
			# THIS LOOKS NICE TO ME, BUT POSSIBLY WOULD WANT OPTIONS?
			data = np.mean(np.array([data, last_data_window]), axis=0)
			return data


		





class Streamer(QThread):
	'Streamer object to simulate EEG data streaming'
	new_data = pyqtSignal(np.ndarray)

	def __init__(self,fs_Hz, filters):
		QThread.__init__(self)
		self.data = []
		self.fs_Hz = fs_Hz
		self.FIRST_BUFFER = True
		self.filters = filters

	def __del__(self):
		self.wait()

	def run(self):
		self.file_input()

	def file_input(self):
		global form
		global new_data
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
			print(i)
			time.sleep(0.0035)
			end = time.time()
			# print("Recorded TIME: ", i/250, " SECONDS")
			# print("Program time: ",end-start)
			if self.FIRST_BUFFER is True:
				self.init_buffer(float(sample))
			else:
				self.sample_buffer(float(sample))
				if i%10 is 0:
					print("emit")
					self.new_data.emit(self.processed_data)
		# print("EEG Time: ", len(channel_data)/250)


	#Send for processing

	def init_buffer(self,sample):
		self.data = np.append(self.data,sample) #isolate channel of interest (ch1)
		if len(self.data) == 250: #ths is the size of the sample buffer
			if FILTER is True:
				self.processed_data = self.filters.receive_data(self.data)
			self.FIRST_BUFFER = False
			# thread = DataThread()


	def sample_buffer(self,sample):
		# print("initial 2nd buffer")
		# print(self.data)
		self.data = np.delete(self.data, 0)
		self.data = np.append(self.data,sample)
		# print('new second buffer')
		# print(self.data)
		# time.sleep(5)
		if FILTER is True:
			self.processed_data = self.filters.receive_data(self.data)
			# print("DATAAAA",self.data)

class Filters:
	'Class containing EEG filtering and analysis tools' 

	#To use, instantiate the class with parameters specifying the type of filter and analysisf.
	#Then, call the Filters.data parameter in order to then get the filtered data


	def __init__(self,fs_Hz,filter_types):
		self.fs_Hz = fs_Hz #setting the sample rate
		self.processed_data = [] #creating an array for filtered data
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
		processed_data = data #processed_data initialized with data, it will then be sent through the filters
		if self.NOTCH is True:
			processed_data = self.notch_filter(processed_data,60)
		if self.BANDPASS is True:
			processed_data = self.bandpass_filter(processed_data,1,50)
		if self.FFT is True:
			processed_data = self.fft(processed_data)
			# print(processed_data.shape)
			# print("before", processed_data)
			processed_data = np.reshape(processed_data,250)
			# print("after", processed_data)
			# time.sleep(5)
		return processed_data

	def notch_filter(self,data,notch_Hz=60):
		notch_Hz = np.array([float(notch_Hz - 1.0), float(notch_Hz + 1.0)])
		b, a = signal.butter(2,notch_Hz/(self.fs_Hz / 2.0), 'bandstop')

		#apply the filter to the stream
		processed_data = signal.lfilter(b,a,data)
		return processed_data


	def bandpass_filter(self,data,low_cut,high_cut):
		bandpass_frequencies = np.array([low_cut, high_cut])
		b,a = signal.butter(2, bandpass_frequencies/(self.fs_Hz / 2.0), 'bandpass')
		
		#apply filter to stream, update data with filtered signal
		processed_data = signal.lfilter(b,a,data)
		return processed_data


	####################
	# Hanning Window
	# aka a hanning taper. This is a filter that tries to taper the data to zero at the edges
	# 
	# window = signal.hann()

	def fft(self,data):
		global fft_array



		#FFT ALGORITHM
		fft_data1 = []
		fft_data2 = []
		fft_data1 = np.fft.fft(data).conj().reshape(-1, 1)
		fft_data1 = abs(fft_data1/self.fs_Hz) #generate two-sided spectrum
		fft_data2 = fft_data1[0:(250/2)+1]
		fft_data1[1:len(fft_data1)-1] = 2*fft_data1[1:len(fft_data1)-1]
		fft_array.append(fft_data1)
		return fft_data1 #fft computation and normalization

def main():
	global FILTER
	global form
	global app
	FILTER = True
	PLOT = True
	if FILTER is True:
		filters = Filters(250,['fft'])
	streamer = Streamer(250,filters)
	if PLOT is True:
		app = QtGui.QApplication(sys.argv)  # new instance of QApplication
		form = Plot(streamer)				# set form to be Plot()
		form.show()							# Show the form
		# form.start_streamer()
		app.exec_()							# execute the app
	np.savetxt('fft_python_check.txt', streamer.processed_data,delimiter=',')

	print("READY")




if __name__ == '__main__':
	form = None
	app = None
	fft_array = []

	main()

# display_plot = Plot()


# display_plot.show()


# test.file_input()