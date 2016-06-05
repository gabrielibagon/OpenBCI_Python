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
from recordclass import recordclass

class Plot(QtGui.QMainWindow, window.Ui_MainWindow):
	'Class used to plot EEG data in real time'

	def __init__(self, streamer, parent=None):
		#pyqtgraph setup
		global form
		global new_data
		global app
		self.processed_data = []
		self.streamer = streamer
		self.N = 250
		self.fs_Hz = 250
		self.data = []
		self.f = np.linspace(0,self.N-1,self.N)*self.fs_Hz/self.N #the y axis
		self.scroll_time_axis = np.linspace(0,-5,250)
		self.last_data_window = []
		self.number_of_channels = 8
		self.fft_channel_curves = []
		self.scroll_curves = []
		self.scroll_plotted_data = [[0]*250]*8
		self.channels_to_display = [True,True,True,True,True,True,True,True]

		################################################################
		# INITIALIZE THE GUI
		super(self.__class__,self).__init__()
		self.setupUi(self)


		# GENERAL SETUP 

		# center the screen
		geometry = self.frameGeometry()
		cp = QtGui.QDesktopWidget().availableGeometry().center()
		geometry.moveCenter(cp)
		self.move(geometry.topLeft())

		#resize
		# view = pg.GraphicsView()
		# layout = pg.GraphicsLayout()
		# view.setCentralItem(layout)
		# view.showMaximized()


		#################################################################
		# DATA SCROLL

		# 	if self.channels_to_display[i]:
		scroll_widget = self.scroll_plot
		scroll_widget.setXRange(-5,0, padding=.0001)
		scroll_widget.setYRange(-50,2100)
		# scroll_widget.setLabel('left')
		scroll_widget.getAxis('left').setWidth((0))
		scroll_widget.setLabel('bottom','Time','Seconds')
		scroll_widget.plot()
		for i in range(self.number_of_channels):
			self.scroll_curves.append(scroll_widget.plot())

			# self.scroll_curves.append(scroll_widget.plot())



		#################################################################
		# FFT PLOT
		self.fft_canvas = self.fft #canvas is of the type pyqtplot.PlotWidget
		for i in range(self.number_of_channels):
			self.fft_channel_curves.append(self.fft_canvas.plot())
		# self.p2.setData(x=[10,20,30,40], y=[1,1,1,1])

		# PARAMETERS FOR FFT PLOT
		self.fft_canvas.setLabel('left','Power','uV per bin')
		self.fft_canvas.setLabel('bottom','Frequency','Hz')
		self.fft_canvas.setWindowTitle('Magnitude spectrum of the signal')
		self.fft_canvas.setXRange(0,60,padding=0)
		self.fft_canvas.setYRange(-1.5,2)
		self.fft_canvas.setLogMode(y=True)
		# self.fft_canvas.getAxis('left').setScale(1)
		self.fft_canvas.disableAutoRange()


		streamer.new_fft_data.connect(self.plot_data)

		self.pushButton.clicked.connect(lambda: self.start_streamer())
		
	def start_streamer(self):
		self.streamer.run()

	@pyqtSlot('PyQt_PyObject')
	def plot_data(self,data):
		global app

		# FFT PLOT
		fft_data = self.smoothing(data.fft_data)						#smooth fft data
		for i,channel in enumerate(fft_data):
			# print(self.fft_channel_curves[i])
			if self.channels_to_display[i]:
				self.fft_channel_curves[i].setData(x=self.f[0:60],y=channel[0:60])
			else:
				self.fft_channel_curves[i].setData(x=[0],y=[0])
			i+=1



		# SCROLL PLOT
		for i,channel in enumerate(data.filtered_data):
			temp_scroll_data_buffer = []
			temp_scroll_data_buffer.append(channel[i]) #first spot for new data point
			for j in range(len(self.scroll_plotted_data[0])-1):
				temp_scroll_data_buffer.append(self.scroll_plotted_data[i][j])
			self.scroll_plotted_data[i] = temp_scroll_data_buffer
			current_curve = self.scroll_curves[i]
			if self.channels_to_display[i]:
				current_curve.setData(x=self.scroll_time_axis,y=([point+(300*i) for point in self.scroll_plotted_data[i]]))
			else:
				current_curve.setData(x=[0],y=[0])
			i+=1

		app.processEvents()
		# print("Sup friend")

	# Function used to smooth the fft plot
	def smoothing(self,data):
		last_data_window = self.last_data_window
		# if this is the first data window being plotted
		if len(last_data_window) == 0:
			self.last_data_window = data #set this up for the next window
			return data #return without being smoothed
		#else, average last_data_window with current data
		else:
			self.last_data_window = data

			# ***USING THIS IMPLEMENTATION DEFAULTS TO 50/50 SMOOTHING
			# THAT IS .5 ON THE PROCESSING GUI
			# THIS LOOKS NICE TO ME, BUT POSSIBLY WOULD WANT OPTIONS?
			i = 0
			for channel in data:
				data[i] = np.mean(np.array([channel, last_data_window[i]]), axis=0)
				i+=1
			return data

	def closeEvent(self,event):
		self.streamer.stop()
        
class Streamer(QThread):
	'Streamer object to simulate EEG data streaming'

	#this creates a record class: mutable named tuple to hold all of the data of one data window
	Data_Return = recordclass('Data_Return', 'raw_data filtered_data rms fft_data')
	data_return = Data_Return([],[],[],[])

	# This defines a signal called 'new_data' that takes a 'Data_Return' type argument
	new_fft_data = pyqtSignal(Data_Return)
	new_scroll_data = pyqtSignal(Data_Return)

	def __init__(self,fs_Hz, filters):
		QThread.__init__(self)
		self.data = []
		self.fs_Hz = fs_Hz
		self.FIRST_BUFFER = True
		self.filters = filters


	# def __del__(self):
	# 	self.wait()

	def run(self):
		self.file_input()

	def stop(self):
		sys.exit()

	def file_input(self):
		global form
		global new_data
		channel_data = []
		with open('sample.txt', 'r') as file:
			reader = csv.reader(file, delimiter=',')
			next(file)
			j = 0
			for line in reader:
				channel_data.append(line[1:]) #list
				j+=1
		start = time.time()
		i=0
		for sample in channel_data:
			i+=1
			print(i)
			# time.sleep(0.0035)
			end = time.time()
			# print("time it should be: ", i/250, " SECONDS")
			# print("My Program time: ",end-start)
			#New array of each sample
			if self.FIRST_BUFFER is True:
				self.init_buffer(sample)
			else:
				self.sample_buffer(sample)
				if i%10 is 0:
					# print("emit")
					self.new_fft_data.emit(self.data_return)
				# self.new_scroll_data.emit(self.data_return)
		# print("EEG Time: ", len(channel_data)/250)


	#Send for processing

	def init_buffer(self,sample):
		self.data.append(sample)
		if len(self.data) == 250: #ths is the size of the sample buffer
			# put the full window of data in data_return
			self.data_return.raw_data = self.data

			#reformat data for processing
			data = np.asarray(list(zip(*self.data))) #change that format of data to [channels, samples] for processed
			data = data.astype(np.float) #change the contents of the data to float for processed
			if FILTER is True:
				self.data_return.filtered_data = self.filters.signal_filters(data)
			self.FIRST_BUFFER = False

	def sample_buffer(self,sample):
		self.data.pop(0)
		self.data.append(sample)

		# put the full window of data in data_return
		self.data_return.raw_data = self.data

		#reformat data for processing
		data = np.asarray(list(zip(*self.data))) #change that format of data to [channels, samples] for processed
		data = data.astype(np.float) #change the contents of the data to float for processed


		# SEND FOR PROCESSING AND ANALYSIS
		if FILTER is True:
			self.data_return.filtered_data = self.filters.signal_filters(data)
		# FFT (used for FFT plot. It is always computed, and uses filtered data)
		self.data_return.fft_data = self.filters.fft(self.data_return.filtered_data)
		# RMS (used for EEG trace. It is always computed, and uses filtered data)
		self.data_return.rms = self.filters.rms(self.data_return.filtered_data)

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


	def signal_filters(self,data):
		# self.data = data
		processed_data = data #processed_data initialized with data, it will then be sent through the filters
		
		# DATA FILTERS
		if self.NOTCH is True:
			processed_data = self.notch_filter(processed_data,60)
		if self.BANDPASS is True:
			processed_data = self.bandpass_filter(processed_data,1,50)
		return data

	def notch_filter(self,data,notch_Hz=60):
		processed_data = np.empty([8,250])

		#set up filter
		notch_Hz = np.array([float(notch_Hz - 1.0), float(notch_Hz + 1.0)])
		b, a = signal.butter(2,notch_Hz/(self.fs_Hz / 2.0), 'bandstop')
		i=0
		#apply the filter to the stream, one channel at a time
		for channel in data:
			processed_data[i] = signal.lfilter(b,a,channel)
			i+=1
		return processed_data


	def bandpass_filter(self,data,low_cut,high_cut):
		processed_data = np.empty([8,250])
		# set up filter
		bandpass_frequencies = np.array([low_cut, high_cut])
		b,a = signal.butter(2, bandpass_frequencies/(self.fs_Hz / 2.0), 'bandpass')
		# apply filter to data window
		i=0
		for channel in data:
			processed_data[i] = signal.lfilter(b,a,channel)
			i+=1
		return processed_data

	def fft(self,data):
		global fft_array
		i=0
		for channel in data:
			#FFT ALGORITHM
			fft_data1 = []
			fft_data2 = []
			fft_data1 = np.fft.fft(channel).conj().reshape(-1, 1)
			fft_data1 = abs(fft_data1/self.fs_Hz) #generate two-sided spectrum
			fft_data2 = fft_data1[0:(250/2)+1]
			fft_data1[1:len(fft_data1)-1] = 2*fft_data1[1:len(fft_data1)-1]
			fft_data1 = fft_data1.reshape(250)
			fft_array[i] = fft_data1
			i+=1
		return fft_array #fft computation and normalization

	#calculates the root mean square, used for the voltage scroll plot
	def rms(self,data):
		# algorithm: x_rms = sqrt((1/n)((x_1)^2 + (x_2)^2 + ...+ (x_n)^2)))
		rms = []
		n = len(data[0]) #length of data
		for channel in data:
			channel_rms = np.sqrt(np.mean(np.square(channel)))
			# print("CHANNEL_RMS",type(channel_rms))
			# print("RMS", type(rms))
			rms.append(np.asscalar(channel_rms))
		# print(rms)
		return rms


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
		sys.exit(app.exec_())				# execute the app
		
	# np.savetxt('fft_python_check.txt', streamer.processed_data,delimiter=',')
	print('ready 2 exit')
	

	print("READY")




if __name__ == '__main__':
	form = None
	app = None
	fft_array = np.empty([8,250])
	main()
