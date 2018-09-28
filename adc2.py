import Tesis
import time
import matplotlib.pyplot as plt
import numpy as np
import RPi.GPIO as GPIO
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

ctrl0 = 5
GPIO.setmode(GPIO.BCM) # GPIO05 COMO  SALIDA EN HIGH (MULTIPLEXOR)
GPIO.setup(ctrl0, GPIO.OUT)
GPIO.output(ctrl0, GPIO.LOW)

ctrl1 = 6
GPIO.setmode(GPIO.BCM) # GPIO06 COMO SALIDA EN LOW (MULTIPLEXOR)
GPIO.setup(ctrl1, GPIO.OUT)
GPIO.output(ctrl1, GPIO.LOW)

ECG_shutdown_pin = 12
GPIO.setmode(GPIO.BCM) # GPIO12 COMO SALIDA EN HIGH
GPIO.setup(ECG_shutdown_pin, GPIO.OUT)
GPIO.output(ECG_shutdown_pin, GPIO.HIGH)

PO_LED = 13
GPIO.setmode(GPIO.BCM) # GPIO12 COMO SALIDA EN HIGH
GPIO.setup(PO_LED, GPIO.OUT)
GPIO.output(PO_LED, GPIO.HIGH)

LEAD_OFF_DETECTIONplus = 19
LEAD_OFF_DETECTIONminus = 26
GPIO.setmode(GPIO.BCM) # GPIO19 Y 26 COMO ENTRADA
GPIO.setup(LEAD_OFF_DETECTIONplus, GPIO.IN)
GPIO.setup(LEAD_OFF_DETECTIONminus, GPIO.IN)

print "LOD+ " + str(GPIO.input(LEAD_OFF_DETECTIONplus))
print "LOD- " + str(GPIO.input(LEAD_OFF_DETECTIONminus))


ECG = []
times = []
PO = []
start = time.time()
tiempo = 15
foos = GPIO.input(LEAD_OFF_DETECTIONplus)
ro = GPIO.input(LEAD_OFF_DETECTIONminus)

while time.time() - start < tiempo:
    Tesis.trigger_adcs(adcECG, adcPO) #SE HACE TRIGGER A AMBOS ADCS
    times.append(time.time() - start) #SE GUARDA EL TIEMPO EN EL QUE SE HIZO EL TRIGGER A LOS ADCS
    valueECG, valuePO = Tesis.read_adcs(adcECG, adcPO) #SE LEE EL VALOR EN AMBOS ADCS Y SE LUEGO SE GUARDAN CADA UNO EN UNA LISTA
    ECG.append(valueECG)
    PO.append(valuePO)

ts = []
for i in range(1,len(times),1):
    ts.append(times[i]-times[i-1])

ts = sum(ts)/len(ts)  #SE CALCULA EL PROMEDIO DE TIEMPOS DE MUESTREO
fs = 1/ts
print "ts = " + str(ts)
print "fs = " + str(fs)

times = times[int(2*fs):]
ECG = ECG[int(2*fs):]
PO = PO[int(2*fs):]
# Filter requirements.
order = 10
lowcut = 0.8
highcut = 35

# Get the filter coefficients so we can check its frequency response.
sos = Tesis.butter_bandpass(lowcut,highcut, fs, order)
w, h = signal.sosfreqz(sos,worN=20000)
#plt.subplot(3, 1, 1)
#plt.semilogx(0.5*fs*w/np.pi, np.abs(h), 'b')
#plt.xlim(0, 0.5*fs)
#plt.title("Bandpass Filter Frequency Response")
#plt.xlabel('Frequency [Hz]')
#plt.grid()

yECG = Tesis.butter_bandpass_filter(np.asarray(ECG), lowcut, highcut, fs, order)
yPO = Tesis.butter_bandpass_filter(np.asarray(PO), lowcut, highcut, fs, order)
#yPO_opuesta = yPO*-1

Rtimes, picos = Tesis.RRs(times, fs, yECG)
maxDerivsTimes, PO_MaxDerivs = Tesis.maxDerivs(times, fs, yPO)
timesValles, valuesValles = Tesis.valles(yPO,times,maxDerivsTimes)

#for t in timesValles:
#	print t

plt.subplot(2, 1, 1)
plt.plot(times, ECG, 'b-', label='ECG')
plt.plot(times, yECG, 'g-', linewidth=2, label='ECG filtered data')
plt.plot(Rtimes, picos,'ro', linewidth=1, label='picos')
plt.xlabel('Time [sec]')
plt.grid()
plt.legend()

plt.subplot(2, 1, 2)
#plt.plot(maxDerivsTimes, PO_MaxDerivs, 'b-', label='PO')
plt.plot(times, PO, 'b-', label='PO')
plt.plot(times, yPO, 'g-', linewidth=2, label='PO filtered data')
plt.plot(timesValles, valuesValles, 'ro', linewidth=1, label='valles')
plt.xlabel('Time [sec]')
plt.grid()
plt.legend()
plt.subplots_adjust(hspace=0.35)
plt.show()
GPIO.output(PO_LED, GPIO.LOW)
GPIO.cleanup()
#datos = open('/home/pi/Tesis/datos_enzo.txt', 'w')
#for i in range(len(yPO)):
#	datos.write(str(times[i]) + "," + str(yECG[i]) + "," + str(yPO[i]) + ",")
