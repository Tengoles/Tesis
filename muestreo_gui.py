import time
import matplotlib.pyplot as plt
import numpy as np
import RPi.GPIO as GPIO
from scipy import signal
from Tkinter import *
import Tkinter, Tkconstants, tkFileDialog

def toda_la_magia(tiempo, filename, logs_directory):
	ADS1x15_POINTER_CONVERSION = 0x00  # = 0
	ADS1x15_POINTER_CONFIG = 0x01  # = 1

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

	import Tesis
	adcECG = Tesis.ADS1115()
        adcPO = Tesis.ADS1115(0X49)

	ECG = []
	times = []
	PO = []
	start = time.time()
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
        with open(logs_directory + "/" + filename  + '.csv', 'w') as file:
		file.write("Tiempos" + "," + "ECG" + "," + "PO" + ","  + "Pico EGG" + "," + "Valle PO" + "\n")
                for i in range(len(yPO)):
			if (times[i] in Rtimes):
				indice = Rtimes.index(times[i])
                        	file.write(str(times[i]) + "," + str(yECG[i]) + "," + str(yPO[i]) + "," + str(picos[indice]) + "," + "\n")
			elif (times[i] in timesValles):
				indice = timesValles.index(times[i])
				file.write(str(times[i]) + "," + str(yECG[i]) + "," + str(yPO[i]) + ","  + "," + str(valuesValles[indice])  + "\n")
			else:
				file.write(str(times[i]) + "," + str(yECG[i]) + "," + str(yPO[i]) + "," + "," + "\n")

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

def browse_button():
    # Allow user to select a directory and store it in global var
    # called folder_path
    global logs_directory
    logs_directory = tkFileDialog.askdirectory()
    string_to_display = logs_directory
    label_3["text"] = string_to_display

def process_files():
    tiempo = int(entry_1.get())
    filename = str(entry_2.get())
    toda_la_magia(tiempo, filename, logs_directory)

my_window = Tk()
my_window.wm_title('Digitalizacion de ECG y PO')
#creamos los widgets
label_1 = Label(my_window,text = "Tiempo de muestreo")
entry_1 = Entry(my_window)
label_2 = Label(my_window,text = "Nombre de archivo")
entry_2 = Entry(my_window)
logs_directory = StringVar()
label_3 = Label(my_window)
button_1 = Button(text="Seleccionar carpeta conteniendo logs", command=browse_button)
button_2 = Button(my_window, text = 'Correr programa', command = process_files)
label_4 = Label(my_window)

#ponemos los widgets en la ventana
label_1.grid(row = 0, column = 0)
entry_1.grid(row = 0, column = 1)
label_2.grid(row = 1, column = 0)
entry_2.grid(row = 1, column = 1)
button_1.grid(row = 2, column = 0)
button_2.grid(row = 3, column = 0)
label_3.grid(row = 2, column = 1)
label_4.grid(row = 3, column = 1)

my_window.mainloop()
