import time


# Register and other configuration values:
ADS1x15_DEFAULT_ADDRESS        = 0x48 # = 1001000
ADS1x15_POINTER_CONVERSION     = 0x00 # = 0
ADS1x15_POINTER_CONFIG         = 0x01 # = 1
ADS1x15_POINTER_LOW_THRESHOLD  = 0x02 # = 10
ADS1x15_POINTER_HIGH_THRESHOLD = 0x03 # = 11
ADS1x15_CONFIG_OS_SINGLE       = 0x8000 # = 1000000000000000
ADS1x15_CONFIG_MUX_OFFSET      = 12 # = 1100
# Maping of gain values to config register values.
ADS1x15_CONFIG_GAIN = {
    2/3: 0x0000,
    1:   0x0200,	
    2:   0x0400,
    4:   0x0600,
    8:   0x0800,
    16:  0x0A00
}
ADS1x15_CONFIG_MODE_CONTINUOUS  = 0x0000
ADS1x15_CONFIG_MODE_SINGLE      = 0x0100
# Mapping of data/sample rate to config register values for ADS1115 (slower).
ADS1115_CONFIG_DR = {
    8:    0x0000,
    16:   0x0020,
    32:   0x0040,
    64:   0x0060,
    128:  0x0080,  
    250:  0x00A0,
    475:  0x00C0,
    860:  0x00E0   #lo mas rapido posible para ambos
}
ADS1x15_CONFIG_COMP_WINDOW      = 0x0010
ADS1x15_CONFIG_COMP_ACTIVE_HIGH = 0x0008
ADS1x15_CONFIG_COMP_LATCHING    = 0x0004
ADS1x15_CONFIG_COMP_QUE = {
    1: 0x0000,
    2: 0x0001,
    4: 0x0002
}
ADS1x15_CONFIG_COMP_QUE_DISABLE = 0x0003


class ADS1115(object):
    """Base functionality for ADS1115 analog to digital converter."""

    def __init__(self, address=ADS1x15_DEFAULT_ADDRESS, i2c=None, **kwargs):
        if i2c is None:
            import Adafruit_GPIO.I2C as I2C
            i2c = I2C     
        self._device = i2c.get_i2c_device(address, **kwargs)
         
    def readA0(self):
        self._device.writeList(ADS1x15_POINTER_CONFIG, [0b11000011, 0b11100011])
		#time.sleep(1.0/860+0.0001)
		#time.sleep(1.0/859.0)
		#for i in range(0,8000):
		#	pass
		result = self._device.readList(ADS1x15_POINTER_CONVERSION, 2)
		return self._conversion_value(result[1], result[0])
    def readECG(self):
		self._device.writeList(ADS1x15_POINTER_CONFIG, [0b11000011, 0b11100011])
		#time.sleep(1.0/860+0.0001)
		#time.sleep(1.0/859.0)
		#for i in range(0,1000):
		#	pass
		result = self._device.readList(ADS1x15_POINTER_CONVERSION, 2)
		return self._conversion_value(result[1], result[0])
    
    def readPO(self):
		self._device.writeList(ADS1x15_POINTER_CONFIG, [0b11110011, 0b11100011])
		#time.sleep(1.0/860+0.0001)
		#time.sleep(1.0/859.0)
		for i in range(0,1000):
			pass
		result = self._device.readList(ADS1x15_POINTER_CONVERSION, 2)
		return self._conversion_value(result[1], result[0])
    
    def _conversion_value(self, low, high):
		# Convert to 16-bit signed value.
		value = ((high & 0xFF) << 8) | (low & 0xFF)
		# Check for sign bit and turn into a negative value if set.
		if value & 0x8000 != 0:
			value -= 1 << 16
		return value
	  
    def _read(self, mux, data_rate, mode):
        """Perform an ADC read with the provided mux, gain, data_rate, and mode
        values.  Returns the signed integer result of the read.
        """
        config = ADS1x15_CONFIG_OS_SINGLE  # Go out of power-down mode for conversion. config = 1000000000000000
        
        # Specify mux value.
        config |= (mux & 0x07) << ADS1x15_CONFIG_MUX_OFFSET #mux puede valer 0b100 0b101 para leer las entradas 0 1 4 respectivamente
        #config = 1100 0000 0000 0000 o 1101 0000 0000 0000 o 1111 0000 0000 0000
        
        #vamos a usar siempre gain 1 (0x0200)
        config |= ADS1x15_CONFIG_GAIN[1] 
        #config = 1100 0010 0000 0000 o 1101 0010 0000 0000 o 1111 0010 0000 0000
         
        # Set the mode (continuous or single shot). #ADS1x15_CONFIG_MODE_SINGLE      = 0x0100
        config |= mode 
        #config = 1100 0011 0000 0000 o 1100 0011 0000 0000 o 1111 0011 0000 0000
		
		#Set data rate
        config |= data_rate 	#data_rate queremos que sea 1110 0000 (860 kbps) o 1000 0000 (128 kbps) o 1100 0000 (475 kbps)
        #config = 1100 0011 1110 0000 o 1101 0011 1110 0000 o 1111 0011 1110 0000 (860 kbps)
        #config = 1100 0011 1100 0000 o 1101 0011 1100 0000 o 1111 0011 1100 0000 (475 kbps)
        
        config |= ADS1x15_CONFIG_COMP_QUE_DISABLE  # Disable comparator mode.
        #config = 1100 0011 1110 0011 o 1101 0011 1110 0011 o 1111 0011 1110 0011 (860 kbps)
        #config = 1100 0011 1100 0011 o 1101 0011 1100 0011 o 1111 0011 1100 0011 (475 kbps)
        #config = 0b11000011 0b11100011 o 0b11010011 0b11100011 o 0b11110011 0b11100011 (860 kbps)
        #config = 0b11000011 0b11000011 o 0b11010011 0b11000011 o 0b11110011 0b11000011 (475 kbps)
        
        # Send the config value to start the ADC conversion.
        # Explicitly break the 16-bit value down to a big endian pair of bytes.
        self._device.writeList(ADS1x15_POINTER_CONFIG, [(config >> 8) & 0xFF, config & 0xFF])
        # Wait for the ADC sample to finish based on the sample rate plus a
        # small offset to be sure (0.1 millisecond).
        time.sleep(1.0/data_rate+0.0001)
        # Retrieve the result.
        result = self._device.readList(ADS1x15_POINTER_CONVERSION, 2)
        return self._conversion_value(result[1], result[0])

    def start_adc(self, channel, gain=1, data_rate=None):
        """Start continuous ADC conversions on the specified channel (0-3). Will
        return an initial conversion result, then call the get_last_result()
        function to read the most recent conversion result. Call stop_adc() to
        stop conversions.
        """
        assert 0 <= channel <= 3, 'Channel must be a value within 0-3!'
        # Start continuous reads and set the mux value to the channel plus
        # the highest bit (bit 3) set.
        return self._read(channel + 0x04, gain, data_rate, ADS1x15_CONFIG_MODE_CONTINUOUS)

    def stop_adc(self):
        """Stop all continuous ADC conversions (either normal or difference mode).
        """
        # Set the config register to its default value of 0x8583 to stop
        # continuous conversions.
        config = 0x8583
        self._device.writeList(ADS1x15_POINTER_CONFIG, [(config >> 8) & 0xFF, config & 0xFF])

    def get_last_result(self):
        """Read the last conversion result when in continuous conversion mode.
        Will return a signed integer value.
        """
        # Retrieve the conversion register value, convert to a signed int, and
        # return it.
        result = self._device.readList(ADS1x15_POINTER_CONVERSION, 2)
        return self._conversion_value(result[1], result[0])

