import time

# Import the ADS1x15 module.
import Adafruit_ADS1x15
import matplotlib.pyplot as plt


# Create an ADS1115 ADC (16-bit) instance.
adc = Adafruit_ADS1x15.ADS1115()
#adc1 = Adafruit_ADS1x15.ADS1115()

a0 = []
a1 = []

times0 = [0]
times1 = [0]

tiempo = int(raw_input("Tiempo:"))
#init0 = adc0._read(0 + 0x04, 2, 860, 0x0000)
#time.sleep(0.5)
#init1 = adc1._read(1 + 0x04, 2, 860, 0x0000)
#time.sleep(0.5)

a0.append(adc._read(0 + 0x04, 2, 860, 0x0000))
a1.append(adc._read(1 + 0x04, 2, 860, 0x0000))

start_time = time.time()

while time.time() - start_time < tiempo:
	a0.append(adc._read(0 + 0x04, 2, 860, 0x0000))
	times0.append(time.time() - start_time)
	#time.sleep(0.05)
	a1.append(adc._read(1 + 0x04, 2, 860, 0x0000))
	times1.append(time.time() - start_time)
	#time.sleep(0.05)

#ts=[]
#adc0.stop_adc()
#adc1.stop_adc()
#for i in range(1,len(times),1):
#	ts.append(times[i]-times[i-1])
#promedio = 1/(sum(ts)/len(ts))
#print ("el promedio de fs es: " + str(promedio))
plt.plot(times0,a0)
plt.plot(times1,a1)
plt.show()


