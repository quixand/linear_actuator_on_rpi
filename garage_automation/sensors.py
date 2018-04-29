#!/usr/bin/python3

from garage_automation.power_sensor import PowerSensors
import RPi.GPIO as GPIO

# todo
# on script start if position is limbo, don't do anything, next state change should be 'open' operation


class Sensors:
    """ static methods to read the sensors """

    def __init__(self, logging, bolts_closed_sensor):
        self.logger = logging
        self.bolts_closed_sensor = bolts_closed_sensor
        self.power_sensors = PowerSensors()

    def actuator_voltage(self):
        return self.power_sensors.voltage()

    def actuator_current(self):
        return self.power_sensors.current()

    def check_bolt_closed_limit_switch(self):
        return GPIO.input(self.bolts_closed_sensor)
