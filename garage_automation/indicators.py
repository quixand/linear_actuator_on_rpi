#!/usr/bin/python3

# this file contains a class that controls LEDs


class Indicators:
    def __init__(self, logger, gpio, configs):
        self.gpio = gpio
        self.logger = logger
        self.configs = configs

        # set default state red on, green off
        self.gpio.output(self.configs['led_green_pin'], self.gpio.LOW)
        self.gpio.output(self.configs['led_red_pin'], self.gpio.HIGH)

    def happy(self):
        self.gpio.output(self.configs['led_green_pin'], self.gpio.HIGH)
        self.gpio.output(self.configs['led_red_pin'], self.gpio.LOW)

    def sad(self):
        self.gpio.output(self.configs['led_red_pin'], self.gpio.HIGH)
        self.gpio.output(self.configs['led_green_pin'], self.gpio.LOW)
