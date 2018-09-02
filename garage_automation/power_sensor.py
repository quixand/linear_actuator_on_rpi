#!/usr/bin/python3

# this file contains a class that interacts with the INA219 voltage/current sensor over I2C
# https://github.com/chrisb2/pi_ina219
# sudo pip3 install pi-ina219


from ina219 import INA219


class PowerSensors:
    """ docblock """

    def __init__(self):
        # setup voltage/current sensor
        self.ina = INA219(shunt_ohms=0.1,
                          max_expected_amps=3.0,
                          address=0x40)

        self.ina.configure(voltage_range=self.ina.RANGE_16V,
                           gain=self.ina.GAIN_AUTO,
                           bus_adc=self.ina.ADC_128SAMP,
                           shunt_adc=self.ina.ADC_128SAMP)

    def voltage(self):
        return self.ina.voltage()

    def current(self):
        return self.ina.current()

    def power(self):
        return self.ina.power()


# def read_ina219():
#     try:
#         print('Shunt Voltage: {0:0.2f}mV\n'.format(ina.shunt_voltage()))
#     except Exception as e:
#         print('Current out of device range with specified shunt resister')
#         print(e)
#         shutdown_actuator()
#         sys.exit()
