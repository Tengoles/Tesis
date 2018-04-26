import ADS1115
import time
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, lfilter, freqz

def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

def trigger_adcs(adcECG , adcPO):
	ECG._device.writeList(ADS1x15_POINTER_CONFIG, [0b11000011, 0b11100011])
	PO._device.writeList(ADS1x15_POINTER_CONFIG, [0b11000011, 0b11100011])
	
def read_adcs(adcECG, adcPO)
	result = ECG._device.readList(ADS1x15_POINTER_CONVERSION, 2)
	ECGread = ECG._conversion_value(result[1], result[0])
	result = PO._device.readList(ADS1x15_POINTER_CONVERSION, 2)
    POread = PO._conversion_value(result[1], result[0])
    return ECGread, POread

adcECG = ADS1115.ADS1115()
adcPO = ADS1115.ADS1115(0X49)
#adc._device es un objeto de la clase Device del modulo I2C.py
	
	#adc._device._address es la direccion del i2c en la que esta el adc
	#por defecto es 0x48 eso lo ves en sudo i2cdetect -y 1
	
	#adc._device._bus = Adafruit_PureIO.smbus.SMBus(busnum) es un objeto
	#que tiene los metodos para leer y escribir por i2c


start  = time.time()
ECG = []
ECG.append(adcECG.readA0())
timesECG = []
timesECG.append(time.time() - start)
PO = []
PO.append(adcPO.readA0())
timesPO = []
timesPO.append(time.time() - start)

while time.time() - start < 5:
	ECG.append(adcECG.readA0())
	timesECG.append(time.time() - start)
	
	PO.append(adcPO.readA0())
	timesPO.append(time.time() - start)
	
tsPO = []
tsECG = []	
for i in range(1,len(timesPO),1):
	tsPO.append(timesPO[i]-timesPO[i-1])

for i in range(1,len(timesECG),1):
	tsECG.append(timesECG[i]-timesECG[i-1])

tsPO = sum(tsPO)/len(tsPO)
tsECG = sum(tsECG)/len(tsECG)
fsECG = 1/tsECG
fsPO = 1/tsPO
print "tsPO = " + str(tsPO)
print "fsPO = " + str(fsPO)
print "tsECG = " + str(tsECG)
print "fsECG = " + str(fsECG)

# Filter requirements.
order = 10
fs = fsECG       # sample rate, Hz
cutoff = 40  # desired cutoff frequency of the filter, Hz

# Get the filter coefficients so we can check its frequency response.
b, a = butter_lowpass(cutoff, fs, order)

# Plot the frequency response.
w, h = freqz(b, a, worN=8000)
plt.subplot(2, 1, 1)
plt.plot(0.5*fs*w/np.pi, np.abs(h), 'b')
plt.plot(cutoff, 0.5*np.sqrt(2), 'ko')
plt.axvline(cutoff, color='k')
plt.xlim(0, 0.5*fs)
plt.title("Lowpass Filter Frequency Response")
plt.xlabel('Frequency [Hz]')
plt.grid()

# Filter the data, and plot both the original and filtered signals.
yECG = butter_lowpass_filter(ECG, cutoff, fs, order)
yPO = butter_lowpass_filter(PO, 15, fs, order)

plt.subplot(3, 1, 2)
plt.plot(timesECG, ECG, 'b-', label='ECG')
plt.plot(timesECG, yECG, 'g-', linewidth=2, label='ECG filtered data')
plt.xlabel('Time [sec]')
plt.grid()
plt.legend()

plt.subplot(3, 1, 3)
plt.plot(timesPO, PO, 'b-', label='PO')
plt.plot(timesPO, yPO, 'g-', linewidth=2, label='PO filtered data')
plt.xlabel('Time [sec]')
plt.grid()
plt.legend()


plt.subplots_adjust(hspace=0.35)
plt.show()
#plt.plot(timesECG, ECG)
#plt.plot(timesPO, PO)
#plt.show()






	





