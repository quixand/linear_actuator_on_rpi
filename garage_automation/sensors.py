#!/usr/bin/python3

from garage_automation.power_sensor import PowerSensors
import RPi.GPIO as GPIO


class Sensors:

    def __init__(self, logging, bolts_closed_sensor, door_closed_sensor, switch_input):
        self.logger = logging
        self.bolts_closed_sensor = bolts_closed_sensor
        self.power_sensors = PowerSensors()
        self.door_closed_sensor = door_closed_sensor
        self.switch_input = switch_input

    def actuator_voltage(self):
        return self.power_sensors.voltage()

    def actuator_current(self):
        return self.power_sensors.current()

    def check_bolt_closed_limit_switch(self):
        if 1 == GPIO.input(self.bolts_closed_sensor):
            return 'Locked'
        else:
            return 'Unlocked'

    def check_action_button(self):
        return GPIO.input(self.switch_input)

    def check_door_sensor(self):
        if 1 == GPIO.input(self.door_closed_sensor):
            return 'Closed'
        else:
            return 'Open'

    # todo - we should only log booleans when they change to reduce log spam
    # todo - only log voltage and current during operational state changes, but keep debug logging
    def log_sensor_state(self):
        self.logger.debug("Voltage: " + str(self.actuator_voltage()))
        self.logger.debug("Current: " + str(self.actuator_current()))
        self.logger.debug("door bolt locked: " + str(self.check_bolt_closed_limit_switch()))
        self.logger.debug("door sensors: " + str(self.check_door_sensor()))
