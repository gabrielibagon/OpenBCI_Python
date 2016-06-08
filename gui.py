import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
#PyQt version 4.11.4
from PyQt4.QtCore import QThread, pyqtSignal, pyqtSlot, SIGNAL
import window
import numpy as np 
import sys
import time

class Gui(QtGui.QMainWindow, window.Ui_MainWindow):
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
		self.number_of_channels = 8
		self.channels_to_display = [True,True,True,True,True,True,True,True]
		# self.channels_to_display = [True,False,False,False,False,False,False,False]

		# INITIALIZE THE GUI
		app = QtGui.QApplication(sys.argv)  		# new instance of QApplication
		super(self.__class__,self).__init__()
		self.setupUi(self)

		# GENERAL SETUP 
		# center the screen
		geometry = self.frameGeometry()
		cp = QtGui.QDesktopWidget().availableGeometry().center()
		geometry.moveCenter(cp)
		self.move(geometry.topLeft())

		# THREADING
		self.STREAMING = False								# Boolean to control pausing/streaming
		streamer.new_data.connect(self.plot_data)			# Threading connect for plotting

		# INITIALIZE THE PLOTS
		self.scroll_initialization()
		self.fft_initialization()


		##################################################################
		# Buttons and Widgets
		self.pushButton.clicked.connect(lambda: self.stream_control())

		#start the GUI
		self.show()
		sys.exit(app.exec_())

	def scroll_initialization(self):
		self.scroll_time_axis = np.linspace(0,-5,250)							# the y axis of the scroll plot
		self.last_data_window = []												# saves last data for smoothing() function
		self.scroll_curves = []
		self.scroll_plotted_data = [[0]*250]*8									# holds the x data of the scroll plot
		scroll_widget = self.scroll_plot

		#setting parameters for Data Scroll Plot
		scroll_widget.setXRange(-5,0, padding=.0001)
		scroll_widget.setYRange(-50,2100)
		scroll_widget.getAxis('left').setWidth((0))
		scroll_widget.setLabel('bottom','Time','Seconds')
		scroll_widget.plot()
		for i in range(self.number_of_channels):
			self.scroll_curves.append(scroll_widget.plot())


	def fft_initialization(self):
		# CONSTANTS
		self.f = np.linspace(0,self.N-1,self.N)*self.fs_Hz/self.N 	# the y axis of FFT plot
		self.fft_channel_curves = []								# holds the curves of scroll plot to be plotted

		# INITIALIZE CANVAS
		fft_canvas = self.fft
		for i in range(self.number_of_channels):
			self.fft_channel_curves.append(fft_canvas.plot())
		
		# PARAMETERS FOR FFT PLOT
		fft_canvas.setLabel('left','Power','uV per bin')
		fft_canvas.setLabel('bottom','Frequency','Hz')
		fft_canvas.setWindowTitle('Magnitude spectrum of the signal')
		fft_canvas.setXRange(0,60,padding=0)
		fft_canvas.setYRange(-1.5,2)
		fft_canvas.setLogMode(y=True)
		fft_canvas.disableAutoRange()

	# Receive controls from the Stream/Pause button
	def stream_control(self):
		PAUSED = False
		if PAUSED:
			self.streamer.resume()
		if not self.STREAMING:
			self.pushButton.setText('Pause')
			self.STREAMING = True
			self.streamer.run()
		else:
			self.pushButton.setText('Resume')
			PAUSED = True
			self.streamer.pause()


	@pyqtSlot('PyQt_PyObject')
	def plot_data(self,data):
		global app
		if self.streamer.FIRST_BUFFER:
			self.plot_scrolling(data)
		else:
			self.plot_fft(data)
			self.plot_scrolling(data)
		app.processEvents()

	def plot_scrolling(self,data):
		# print('RAW DATA', data.raw_data)


		for i,channel in enumerate(data.raw_data):
			temp_scroll_data_buffer = []
			temp_scroll_data_buffer.append(channel[len(channel)-1]) #first spot for newest data point
			# print(temp_scroll_data_buffer)
			

			for j in range(len(self.scroll_plotted_data[0])-1):									#add all of the old data points (until the last) to temp_scroll_data_buffer
				temp_scroll_data_buffer.append(self.scroll_plotted_data[i][j])
			self.scroll_plotted_data[i] = temp_scroll_data_buffer								#make the current scroll_plotted_data the temp_scroll_buffer which includes the new point
			# print('READY CHANNEL ', i, self.scroll_plotted_data[i])
			current_curve = self.scroll_curves[i]
			if self.channels_to_display[i]:
				current_curve.setData(x=self.scroll_time_axis,y=([point+(2000-(300*i)) for point in self.scroll_plotted_data[i]]))
			else:
				current_curve.setData(x=self.scroll_time_axis,y=[0.+(2000-(300*i))]*250)
		# time.sleep(2)

	def plot_fft(self,data):
		fft_data = self.smoothing(data.fft_data)																							#smooth fft data
		for i,channel in enumerate(fft_data):
			if self.channels_to_display[i]:
				self.fft_channel_curves[i].setData(x=self.f[0:60],y=channel[0:60])
			else:
				self.fft_channel_curves[i].setData(x=[0],y=[0])

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



