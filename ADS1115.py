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
    860:  0x00E0
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

    def _read(self, mux, gain, data_rate, mode):
        """Perform an ADC read with the provided mux, gain, data_rate, and mode
        values.  Returns the signed integer result of the read.
        """
        config = ADS1x15_CONFIG_OS_SINGLE  # Go out of power-down mode for conversion. 0x8000 = 1000000000000000
        # Specify mux value.
        config |= (mux & 0x07) << ADS1x15_CONFIG_MUX_OFFSET 
        # Validate the passed in gain and then set it in the config.
        if gain not in ADS1x15_CONFIG_GAIN:
            raise ValueError('Gain must be one of: 2/3, 1, 2, 4, 8, 16')
        config |= ADS1x15_CONFIG_GAIN[gain]
        # Set the mode (continuous or single shot).
        config |= mode
        # Get the default data rate if none is specified (default differs between
        # ADS1015 and ADS1115).
        if data_rate is None:
            data_rate = self._data_rate_default()
        # Set the data rate (this is controlled by the subclass as it differs
        # between ADS1015 and ADS1115).
        config |= self._data_rate_config(data_rate)
        config |= ADS1x15_CONFIG_COMP_QUE_DISABLE  # Disble comparator mode.
        # Send the config value to start the ADC conversion.
        # Explicitly break the 16-bit value down to a big endian pair of bytes.
        self._device.writeList(ADS1x15_POINTER_CONFIG, [(config >> 8) & 0xFF, config & 0xFF])
        # Wait for the ADC sample to finish based on the sample rate plus a
        # small offset to be sure (0.1 millisecond).
        time.sleep(1.0/data_rate+0.0001)
        # Retrieve the result.
        result = self._device.readList(ADS1x15_POINTER_CONVERSION, 2)
        return self._conversion_value(result[1], result[0])

    def read_adc(self, channel, gain=1, data_rate=None):
        """Read a single ADC channel and return the ADC value as a signed integer
        result.  Channel must be a value within 0-3.
        """
        assert 0 <= channel <= 3, 'Channel must be a value within 0-3!'
        # Perform a single shot read and set the mux value to the channel plus
        # the highest bit (bit 3) set.
        return self._read(channel + 0x04, gain, data_rate, ADS1x15_CONFIG_MODE_SINGLE)

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

