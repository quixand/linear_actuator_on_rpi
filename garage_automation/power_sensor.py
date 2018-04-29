#!/usr/bin/python3

# this file contains a class that interacts with the INA219 voltage/current sensor over I2C
# https://github.com/chrisb2/pi_ina219
# sudo pip3 install pi-ina219


from ina219 import INA219


class PowerSensors:
    """ docblock """

    def __init__(self):
        # self.logger = logging
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


# v = ina.voltage()
# i = ina.current()
# p = ina.power()
# print ("ina.voltage(V): " + str(v) + " ina.current(mA): " + str(i) + " ina.power(mW): " + str(p))
# sleep(1)
# except KeyboardInterrupt:
    # print ("\nCtrl-C pressed.  Program exiting...")


# def read_ina219():
#     try:
#         v = ina.voltage()
#         i = ina.current()
#         p = ina.power()
#         print ("ina.voltage(V): " + str(v) + " ina.current(mA): " + str(i) + " ina.power(mW): " + str(p))
#         # print('Bus Voltage: {0:0.2f}V'.format(ina.voltage()))
#         # print('Bus Current: {0:0.2f}mA'.format(ina.current()))
#         # print('Power: {0:0.2f}mW'.format(ina.power()))
#         print('Shunt Voltage: {0:0.2f}mV\n'.format(ina.shunt_voltage()))
#     except Exception as e:
#         print('Current out of device range with specified shunt resister')
#         print(e)
#         shutdown_actuator()
#         sys.exit()