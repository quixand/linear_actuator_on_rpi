#!/usr/bin/python3


from time import sleep
import threading

# todo
# - check for door or bolt sensor changes outside of operation and trigger alarm
# - investigate thread termination when door operation interrupted
# - integrate door sensors
# - make sure everything is non-blocking to allow for things like overcurrent detection
# on script start if position is limbo, don't do anything, default state should be 'closed'
# so that user switch trigger will perform 'open' operation


class Control:

    door_closed = False
    state_change_button_activated = False
    open_thread = None

    def __init__(self, logging, actuator, sensors, indicators, configs):
        self.actuator = actuator
        self.logger = logging
        self.sensors = sensors
        self.indicators = indicators
        self.configs = configs

    def change_state(self):
        """Handle multiple button pushes"""
        if self.state_change_button_activated:
            self.logger.info(__name__ + ' Button push detected, but we\'re already doing something. '
                                        'assuming emergency stop requested')
            self.door_closed = True
            self.actuator.shutdown_actuator()
            self.state_change_button_activated = False
            self.open_thread.cancel()
            self.indicators.sad()
            return

        self.logger.info("************ change state called *************")
        self.state_change_button_activated = True

        # lets give the requester time to release the button before we perform any logic
        sleep(2)

        if self.door_closed:
            self.logger.debug("door closed according to sensors")
            # start thread to trigger door open state as we have no sensors
            # to explicitly state the mechanism is fully open
            # we will probably need this for the electronic door opener though
            self.logger.debug("Setting failsafe timeout thread")
            self.open_thread = threading.Timer(self.configs['actuator_full_stroke_duration'], self.set_door_open)
            self.open_thread.start()
            self.actuator.open()
        else:
            self.logger.debug("door open according to sensors")
            self.actuator.close()

    def check_lock_state(self):
        """ verify all sensor inputs to determine state of door
            the door can be
             - open-unlocked
             - closed-locked
             - closed-Unlocked

            If sensors indicate door is open after successful close status then either the sensors have failed
            or the door has been forced open, raise alarm.
        """
        self.check_for_overcurrent()

        # if door is trying to close(in operation) and bolt has engaged and door sensors engaged,
        # door is now closed-locked
        if self.state_change_button_activated and \
                'Locked' == self.sensors.check_bolt_closed_limit_switch() and \
                not self.door_closed:
            self.door_closed = True
            self.logger.info('self.door_closed: ' + str(self.door_closed))
            self.actuator.shutdown_actuator()
            self.state_change_button_activated = False
            self.indicators.happy()

        # check if door is open when it shouldn't be
        if 'Open' == self.sensors.check_door_sensor() and self.door_closed:
            self.door_closed = False
            self.indicators.sad()
            self.logger.info('********* DOOR OPEN DETECTED *********: ' + str(self.door_closed))

    def startup_check(self):
        # on startup state is unknown unless these sensors indicate door is closed-locked
        if 'Locked' == self.sensors.check_bolt_closed_limit_switch() and \
                'Closed' == self.sensors.check_door_sensor():
            self.door_closed = True
            self.indicators.happy()

    def set_door_open(self):
        self.door_closed = False
        self.logger.info(__name__ + str(self.door_closed))
        self.actuator.shutdown_actuator()
        self.state_change_button_activated = False
        self.indicators.happy()

    def check_for_overcurrent(self):
        """ shut down if current too high, door probably jammed.
            Don't do anything at this point we don't want to open the
            door or try to continue the operation. wait for user input """
        if int(self.sensors.actuator_current()) > int(self.configs['over_current_threshold']):
            # self.logger.error('BACON ERROR Over current detected. Current: ' + str(self.sensors.actuator_current()))
            self.actuator.shutdown_actuator()
            self.state_change_button_activated = False
            self.indicators.sad()

    def get_logical_door_state(self):
        return self.door_closed

    def get_operational_state(self):
        return self.state_change_button_activated
