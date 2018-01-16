# Simple demo of reading each analog input from the ADS1x15 and printing it to
# the screen.
# Author: Tony DiCola
# License: Public Domain
import time

# Import the ADS1x15 module.
import Adafruit_ADS1x15
import matplotlib.pyplot as plt

apo=[1,-9.29947181593672,38.9391678696675,-96.6770341442587,157.607191169145,-176.284279849734,137.001526731779,-73.0486978595247,25.5738665509684,-5.30835180952627,0.496083157598912]
bpo=[1.73601583211395e-13,1.73601583211395e-12,7.81207124451280e-12,2.08321899853675e-11,3.64563324743931e-11,4.37475989692717e-11,3.64563324743931e-11,2.08321899853675e-11,7.81207124451280e-12,1.73601583211395e-12,1.73601583211395e-13]

# Create an ADS1115 ADC (16-bit) instance.
adc = Adafruit_ADS1x15.ADS1115()
period = 0.004
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
sdjhsd=adc._read(0 + 0x04, 1, 860, 0x0000)
values.append(adc.get_last_result())
start_time = time.time()

try:
	while True:
    # Read all the ADC channel values in a list.
		a0 = adc.get_last_result()
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
    		#print a0
    		elapsed_time = time.time() - start_time
    		if elapsed_time >= period:
			pass
    		else:
			time.sleep(period - elapsed_time)

except KeyboardInterrupt:
	ts=[]
	for i in range(1,len(times),1):
		ts.append(times[i]-times[i-1])
	promedio = 1/(sum(ts)/len(ts))
	print ("el promedio de fs es: " + str(promedio))
	
	plt.plot(times,values)
	plt.show()
	pass
