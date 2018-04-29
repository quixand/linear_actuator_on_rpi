#!/usr/bin/python3

# see https://docs.python.org/3/library/unittest.html#unittest.TestCase


import unittest
from power_sensor import PowerSensors


class TestPowerSensorObject(unittest.TestCase):

    def setUp(self):
        self.sensors = PowerSensors()

    def tearDown(self):
        pass

    def test_instance(self):
        self.assertIsInstance(self.sensors, PowerSensors)

    def test_voltage(self):
        self.assertRegex(str(self.sensors.voltage()), '\d+')

    def test_current(self):
        self.assertRegex(str(self.sensors.voltage()), '\d+')


if __name__ == '__main__':
    unittest.main()