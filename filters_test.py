import numpy as np
from scipy import signal
from matplotlib import pyplot as plt

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    sos = signal.butter(order, [low, high], btype='band', output='sos')
    return sos

fs = 1000
sos = butter_bandpass(0.8, 20, fs, order=100)
w, h = signal.sosfreqz(sos, worN=20000)

plt.subplot(2, 1, 1)
plt.semilogx((fs * 0.5 / np.pi) * w, abs(h), label=None)
plt.grid(True)

plt.subplot(2, 1, 2)
plt.semilogx((fs * 0.5 / np.pi) * w, np.angle(h), label=None)
plt.grid(True)
plt.show()