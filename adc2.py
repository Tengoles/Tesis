import ADS1115
import time
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, lfilter, freqz, sosfilt
from scipy import signal

ADS1x15_POINTER_CONVERSION     = 0x00 # = 0
ADS1x15_POINTER_CONFIG         = 0x01 # = 1

def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

def butter_highpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def butter_highpass_filter(data, cutoff, fs, order=5):
    b, a = butter_highpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    sos = butter(order, [low, high], btype='band', output='sos')
    #b, a = butter(order, [low, high], btype='band', analog=False)
    return sos


def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    sos = butter_bandpass(lowcut, highcut, fs, order=order)
    y = sosfilt(sos, data)
    return y

def read_adcs(adcECG, adcPO):
    result = adcECG._device.readList(ADS1x15_POINTER_CONVERSION, 2)
    ECGread = adcECG._conversion_value(result[1], result[0])
    result = adcPO._device.readList(ADS1x15_POINTER_CONVERSION, 2)
    POread = adcPO._conversion_value(result[1], result[0])
    return ECGread, POread

def trigger_adcs(adcECG , adcPO):
    adcECG._device.writeList(ADS1x15_POINTER_CONFIG, [0b11000011, 0b11100011])
    adcPO._device.writeList(ADS1x15_POINTER_CONFIG, [0b11000011, 0b11100011])



adcECG = ADS1115.ADS1115()
adcPO = ADS1115.ADS1115(0X49)
#adc._device es un objeto de la clase Device del modulo I2C.py
	
	#adc._device._address es la direccion del i2c en la que esta el adc
	#por defecto es 0x48 eso lo ves en sudo i2cdetect -y 1
	
	#adc._device._bus = Adafruit_PureIO.smbus.SMBus(busnum) es un objeto
	#que tiene los metodos para leer y escribir por i2c



ECG = []
times = []
PO = []
start  = time.time()

while time.time() - start < 5:
	trigger_adcs(adcECG , adcPO)
	times.append(time.time() - start)
	valueECG, valuePO = read_adcs(adcECG, adcPO)
	ECG.append(valueECG)
	PO.append(valuePO)
	
ECGmean = 0
POmean = 0
j = 0
for i in range(len(ECG)):
	ECGmean = ECG[i] + ECGmean
	POmean = PO[i] + POmean
	if j == 3200:
		ECGmean = ECGmean/j
		POmean = POmean/j
		for l in range(j):
			ECG[

ts = []
for i in range(1,len(times),1):
	ts.append(times[i]-times[i-1])

ts = sum(ts)/len(ts)
fs = 1/ts
print "ts = " + str(ts)
print "fs = " + str(fs)

# Filter requirements.
order = 10
cutoff = 10  # desired cutoff frequency of the filter, Hz
lowcut = 1
highcut = 35

# Get the filter coefficients so we can check its frequency response.
#b, a = butter_lowpass(cutoff, fs, order)
#sos = butter_bandpass(lowcut,highcut, fs, 40)
b, a = butter_highpass(cutoff, fs, order)

# Plot the frequency response.
w, h = freqz(b, a, worN=8000)
#w, h = signal.sosfreqz(sos,worN=20000)
plt.subplot(3, 1, 1)
plt.plot(0.5*fs*w/np.pi, np.abs(h), 'b')
plt.plot(cutoff, 0.5*np.sqrt(2), 'ko')
plt.axvline(cutoff, color='k')
plt.xlim(0, 0.5*fs)
#plt.title("Lowpass Filter Frequency Response")
#plt.xlabel('Frequency [Hz]')
plt.grid()

# Filter the data, and plot both the original and filtered signals.
#yECG = butter_lowpass_filter(ECG, cutoff, fs, order)
#yPO = butter_lowpass_filter(PO, cutoff, fs, order)
yECG = butter_highpass_filter(ECG, cutoff, fs, order)
yPO = butter_highpass_filter(PO, cutoff, fs, order)
#yECG = butter_bandpass_filter(ECG, 0.5, 40, fs, order)
#yPO = butter_bandpass_filter(PO, 0.5, 40, fs, order)

ECGmean = sum(yECG)/len(yECG)
ECGmax = np.amax(yECG)
threshold = (ECGmax - ECGmean)*0.6 + ECGmean
Rtimes = []
picos = []

for i in range(len(yECG)-1):
	if yECG[i] > threshold:
		if yECG[i+1] < yECG[i] > yECG[i-1]:
			Rtimes.append(times[i])
			picos.append(yECG[i])
			
timesRR = []
timesRRx = []
timesRRy = []			
for i in range(len(Rtimes)-1):
	timesRR.append(Rtimes[i+1] - Rtimes[i])
			
for i in range(len(timesRR)-1):
	timesRRx.append(timesRR[i])
	timesRRy.append(timesRR[i+1])

#plt.subplot(3, 1, 1)
#plt.plot(timesRRx,timesRRy, 'ko')
#plt.xlim(0.8*min(timesRR),1.2*max(timesRR))
#plt.ylim(0.8*min(timesRR),1.2*max(timesRR))
#plt.title("Poincare")
#plt.grid()

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

datos = open('/home/pi/Tesis/datos_enzo.txt', 'w')
for i in range(len(yPO)):
	datos.write(str(times[i]) + "\t" + str(yECG[i]) + "\t" + str(yPO[i]) + "\n")
