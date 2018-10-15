#!/usr/bin/python3

# this file contains a class that controls LEDs

import time


class Indicators:
    def __init__(self, logger, gpio, configs):
        self.gpio = gpio
        self.logger = logger
        self.configs = configs
        self.indicator_thread = None

        # set default state red on, green off
        self.gpio.output(self.configs['led_green_pin'], self.gpio.LOW)
        self.gpio.output(self.configs['led_red_pin'], self.gpio.HIGH)

    def happy(self):
        self.gpio.output(self.configs['led_green_pin'], self.gpio.HIGH)
        self.gpio.output(self.configs['led_red_pin'], self.gpio.LOW)

    def sad(self):
        self.gpio.output(self.configs['led_red_pin'], self.gpio.HIGH)
        self.gpio.output(self.configs['led_green_pin'], self.gpio.LOW)

    def heartbeat(self):
        self.gpio.output(self.configs['led_green_pin'], self.gpio.LOW)
        time.sleep(0.1)
        self.gpio.output(self.configs['led_green_pin'], self.gpio.HIGH)

    def user_warning(self, pulses=6):
        self.sad()
        i = 1
        while i < pulses:
            self.gpio.output(self.configs['led_red_pin'], self.gpio.HIGH)
            time.sleep(0.5)
            self.gpio.output(self.configs['led_red_pin'], self.gpio.LOW)
            time.sleep(0.5)
            i += 1

    # def in_motion(self ):
