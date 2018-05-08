import Tesis
import time
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, lfilter, freqz, sosfilt
from scipy import signal

ADS1x15_POINTER_CONVERSION = 0x00  # = 0
ADS1x15_POINTER_CONFIG = 0x01  # = 1

adcECG = Tesis.ADS1115()
adcPO = Tesis.ADS1115(0X49)
#adc._device es un objeto de la clase Device del modulo I2C.py
	
	#adc._device._address es la direccion del i2c en la que esta el adc
	#por defecto es 0x48 eso lo ves en sudo i2cdetect -y 1
	
	#adc._device._bus = Adafruit_PureIO.smbus.SMBus(busnum) es un objeto
	#que tiene los metodos para leer y escribir por i2c

ECG = []
times = []
PO = []
start = time.time()

while time.time() - start < 5:
    Tesis.trigger_adcs(adcECG, adcPO)
    times.append(time.time() - start)
    valueECG, valuePO = Tesis.read_adcs(adcECG, adcPO)
    ECG.append(valueECG)
    PO.append(valuePO)

ts = []
for i in range(1,len(times),1):
    ts.append(times[i]-times[i-1])

ts = sum(ts)/len(ts)
fs = 1/ts
print "ts = " + str(ts)
print "fs = " + str(fs)

# Filter requirements.
order = 10
lowcut = 0.8
highcut = 35

# Get the filter coefficients so we can check its frequency response.
sos = butter_bandpass(lowcut,highcut, fs, order)
w, h = signal.sosfreqz(sos,worN=20000)
plt.subplot(3, 1, 1)
plt.plot(0.5*fs*w/np.pi, np.abs(h), 'b')
plt.plot(cutoff, 0.5*np.sqrt(2), 'ko')
plt.axvline(cutoff, color='k')
plt.xlim(0, 0.5*fs)
plt.title("Bandpass Filter Frequency Response")
plt.xlabel('Frequency [Hz]')
plt.grid()

yECG = Tesis.butter_highpass_filter(ECG, cutoff, fs, order)
yPO = Tesis.butter_highpass_filter(PO, cutoff, fs, order)

Rtimes, picos = RRs(times, fs, yECG)
maxDerivsTimes, PO_MaxDerivs = maxDerivs(times, fs, yPO)
timesValles, valuesValles = valles(yPO,times,maxDerivsTimes)

plt.subplot(3, 1, 2)
#plt.plot(times, ECG, 'b-', label='ECG')
plt.plot(times, yECG, 'g-', linewidth=2, label='ECG filtered data')
plt.plot(Rtimes, picos,'ro', linewidth=2, label='picos')
plt.xlabel('Time [sec]')
plt.grid()
plt.legend()

plt.subplot(3, 1, 3)
#plt.plot(times, PO, 'b-', label='PO')
plt.plot(times, yPO, 'g-', linewidth=2, label='PO filtered data')
plt.xlabel('Time [sec]')
plt.grid()
plt.legend()
plt.subplots_adjust(hspace=0.35)
plt.show()

#datos = open('/home/pi/Tesis/datos_enzo.txt', 'w')
#for i in range(len(yPO)):
#	datos.write(str(times[i]) + "," + str(yECG[i]) + "," + str(yPO[i]) + ",")
