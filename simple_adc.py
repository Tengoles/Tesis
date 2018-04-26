# Simple demo of reading each analog input from the ADS1x15 and printing it to
# the screen.
# Author: Tony DiCola
# License: Public Domain
import time
from savitzky_golay import savitzky_golay
import numpy as np
# Import the ADS1x15 module.
import Adafruit_ADS1x15
import matplotlib.pyplot as plt


# Create an ADS1115 ADC (16-bit) instance.
adc = Adafruit_ADS1x15.ADS1115()
adc.start_adc(0, gain=1)
GAIN = 1
values = []
times = [0]
channel = int(raw_input("Canal:"))
tiempo = int(raw_input("Tiempo:"))
#values.append(adc.read_adc(channel, gain = GAIN, data_rate = 860))
values.append(adc.get_last_result())
start_time = time.time()
time2 = start_time
flag = False
while time.time() - start_time < tiempo:
# Read all the ADC channel values in a list.
	#a0 = adc.read_adc(channel, gain = GAIN, data_rate = 860)
	a0 = adc.get_last_result()
	times.append(time.time() - start_time)
	values.append(a0)
	#print a0
	#elapsed_time = time.time() - time2
	#print elapsed_time*1000
	#time2 = time.time()
	#time.sleep(period)
	#for i in range(7000):
	#	i=i+1
	#i=0

if flag is not True:
	ts=[]
	adc.stop_adc()
	for i in range(1,len(times),1):
		ts.append(times[i]-times[i-1])
	promedio = 1/(sum(ts)/len(ts))
	print ("el promedio de fs es: " + str(promedio))
	#values2 = savitzky_golay(np.array(values),41,7)
	#plt.plot(times,values2)
	plt.plot(times,values)
	plt.show()
