#!/usr/bin/python3

# this file contains a class that controls the actuator
# The actuator is a cheap chinese model, spec:
# 50mm travel (2")
# 12v
# 750n
# 10mm/s
# 3A max
# XYDHA12-50
#
# https://www.sparkfun.com/datasheets/Robotics/L298_H_Bridge.pdf
#
# the actuator has internal mechanical isolation reed switches so we can't burn out the actuator
# just by leaving it switched on too long. However we can damage it and/or the door by opening the lock into the ground
# so its critical to monitor the power draw as the current will go up if the actuator is forced into the concrete
# or otherwise jams. The driver board is also rated at 3A, well below what the actuator is capable of drawing
# so we need to protect that too, it got fucking hot in testing!
#
# we also need to shutdown the actuator after the known time it takes to engage fully closed or open, if the sensors
# fail for any reason we don't want the motor/driver board running too long. This is required for an open operation
# anyway as we dont have any sensors to determine that actuator has fully retracted, so we'll have to background time it

import threading


class Actuator:

    def __init__(self, logger, gpio, forwards_pin, backwards_pin):
        self.gpio = gpio
        self.logger = logger
        self.forwards_pin = forwards_pin
        self.backwards_pin = backwards_pin
        self.shutdown_actuator()
        self.in_motion = False
        self.fail_safe_thread = None

    def open(self):
        self.in_motion = True
        self.reverse()

    def close(self):
        self.in_motion = True
        self.forward()

    def forward(self):
        self.fail_safe_timeout()
        self.gpio.output(self.forwards_pin, self.gpio.HIGH)
        self.logger.info(__name__ + ' forwarding running  motor ')

    def reverse(self):
        self.fail_safe_timeout()
        self.gpio.output(self.backwards_pin, self.gpio.HIGH)
        self.logger.info(__name__ + ' backwards running  motor ')

    def shutdown_actuator(self):
        self.gpio.output(self.backwards_pin, self.gpio.LOW)
        self.gpio.output(self.forwards_pin, self.gpio.LOW)
        self.in_motion = False
        self.logger.debug(__name__ + ' Actuator stopped, pins set low')

    def fail_safe_timeout(self):
        """Shut down actuator after known travel time"""
        self.logger.info(__name__ + "what happens if the button is pushed again while the actuator in in motion?")
        self.fail_safe_thread = threading.Timer(30.0, self.shutdown_actuator)
        self.fail_safe_thread.start()
