import numpy as np

import csv
import time
import sys
import threading




data = []
with open('sample.txt', 'r') as file:
	reader = csv.reader(file, delimiter=',')
	next(file)
	for line in reader:
		data.append(line[1])

# fft_data1 = []
# fft_data2 = []
# fft_data1 = abs(np.fft.fft(data)/(250)) #generate two-sided spectrum
# fft_data2 = fft_data1[0:(250/2)+1]
# fft_data1[1:len(fft_data1)-1] = 2*fft_data1[1:len(fft_data1)-1]

fft_data1 = (np.fft.fft(data))
print(fft_data1) #fft computation and normalization
