# Simple demo of reading each analog input from the ADS1x15 and printing it to
# the screen.
# Author: Tony DiCola
# License: Public Domain
import time

# Import the ADS1x15 module.
import Adafruit_ADS1x15
import matplotlib.pyplot as plt

# Create an ADS1115 ADC (16-bit) instance.
adc = Adafruit_ADS1x15.ADS1115()
period = 0.00125
# Note you can change the I2C address from its default (0x48), and/or the I2C
# bus by passing in these optional parameters:
#adc = Adafruit_ADS1x15.ADS1015(address=0x49, busnum=1)

# Choose a gain of 1 for reading voltages from 0 to 4.09V.
# Or pick a different gain to change the range of voltages that are read:
#  - 2/3 = +/-6.144V
#  -   1 = +/-4.096V
#  -   2 = +/-2.048V
#  -   4 = +/-1.024V
#  -   8 = +/-0.512V
#  -  16 = +/-0.256V
# See table 3 in the ADS1015/ADS1115 datasheet for more info on gain.
GAIN = 1
values = []
times = [0]
values.append(adc.read_adc(0, gain=1,data_rate=860))
start_time = time.time()

try:
	while True:
    # Read all the ADC channel values in a list.
		a0 = adc.read_adc(0, gain=1,data_rate=860)
    		times.append(time.time() - start_time)
		values.append(a0)
        	# Read the specified ADC channel using the previously set gain value.
        	# Note you can also pass in an optional data_rate parameter that controls
        	# the ADC conversion time (in samples/second). Each chip has a different
        	# set of allowed data rate values, see datasheet Table 9 config register
        	# DR bit values.
        	#values[i] = adc.read_adc(i, gain=GAIN, data_rate=128)
        	# Each value will be a 12 or 16 bit signed integer value depending on the
        	# ADC (ADS1015 = 12-bit, ADS1115 = 16-bit).
    		# Print the ADC values.
    		print a0
    		#elapsed_time = time.time() - start_time
    		#if elapsed_time >= period:
		#	pass
    		#else:
		#	time.sleep(period - elapsed_time)

except KeyboardInterrupt:
	ts=[]
	#ts.append(times[1]-times[0])
	for i in range(1,len(times),1):
		ts.append(times[i]-times[i-1])
	promedio = sum(ts)/len(ts)
	print ("el promedio de ts es: " + str(promedio))
	
	plt.plot(times,values)
	plt.show()
	pass
