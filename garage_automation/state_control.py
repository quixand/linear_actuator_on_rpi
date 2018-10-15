#!/usr/bin/python3


from time import sleep
import threading


class Control:

    door_closed = False
    state_change_button_activated = False
    open_thread = None
    unexpected_door_sensors_open = None
    unexpected_door_actuator_open = None

    def __init__(self, logging, actuator, sensors, indicators, configs):
        """

        """
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
            self.actuator.shutdown_actuator()
            self.state_change_button_activated = False
            self.open_thread.cancel()
            self.indicators.user_warning(8)
            return

        self.logger.info("************ change state called *************")
        self.state_change_button_activated = True

        # lets give the human time to release the button before we perform any logic
        self.wait_for_action_button_release()

        if self.door_closed:
            self.logger.info("door status: closed.. opening")
            # start thread to trigger door open state as we have no sensors
            # to explicitly state the mechanism is fully open, we must guess
            # we will probably need this for the electronic door opener though
            self.logger.debug("Setting failsafe timeout thread")
            self.open_thread = threading.Timer(self.configs['actuator_full_stroke_duration'], self.set_door_open)
            self.open_thread.start()
            self.actuator.open()
        elif 'Closed' == self.sensors.check_door_sensor():
            self.logger.info("door ready to lock according to sensors")
            self.actuator.close()
        else:
            self.indicators.user_warning(4)
            self.indicators.happy()
            self.logger.warning("Warning: cannot lock door while door sensors disengaged.")
            self.state_change_button_activated = False

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
        if 'Open' == self.sensors.check_door_sensor() and self.door_closed and not self.state_change_button_activated:
            self.indicators.sad()
            if not self.unexpected_door_sensors_open:
                self.logger.warning('********* UNEXPECTED DOOR SENSORS OPEN DETECTED *********: ' + str(self.door_closed))
                self.unexpected_door_sensors_open = True

        # check if actuator sensor has unexpectedly disengaged
        if 'Locked' != self.sensors.check_bolt_closed_limit_switch() and self.door_closed and not self.state_change_button_activated:
            self.indicators.sad()
            if not self.unexpected_door_actuator_open:
                self.logger.warning('********* UNEXPECTED DOOR ACTUATOR OPEN DETECTED *********: ' + str(self.door_closed))
                self.unexpected_door_actuator_open = True

        # check if door has opened during actuator close operation
        if 'Open' == self.sensors.check_door_sensor() and self.actuator.actuator_closing:
            self.actuator.shutdown_actuator()
            self.logger.info('********* DOOR OPEN DETECTED WHILE CLOSING, shutting down actuator *********: ' + str(self.door_closed))
            self.indicators.user_warning(6)
            self.indicators.sad()
            self.state_change_button_activated = False

        # check if door is closed-locked
        self.check_locked()

    def check_locked(self):
        if 'Locked' == self.sensors.check_bolt_closed_limit_switch() and \
                'Closed' == self.sensors.check_door_sensor():
            self.door_closed = True
            self.unexpected_door_sensors_open = False
            self.indicators.happy()
            return True

    def set_door_open(self):
        self.door_closed = False
        self.logger.info(__name__ + "" + str(self.door_closed))
        self.actuator.shutdown_actuator()
        self.state_change_button_activated = False
        self.indicators.happy()

    def on_start_retract(self):
        if 'Unlocked' == self.sensors.check_bolt_closed_limit_switch() or \
                'Open' == self.sensors.check_door_sensor():
            self.logger.warning("Warning: Startup action door appears to be open... retracting")
            self.open_thread = threading.Timer(self.configs['actuator_full_stroke_duration'], self.set_door_open)
            self.open_thread.start()
            self.actuator.open()
            self.indicators.user_warning(14)

    # todo - move this to thread to avoid blocking operations
    def check_for_overcurrent(self):
        """ shut down if current too high, door probably jammed.
            Don't do anything at this point we don't want to open the
            door or try to continue the operation. wait for user input """
        if int(self.sensors.actuator_current()) > int(self.configs['over_current_threshold']):
            self.logger.error('ERROR Over current detected. Current: ' + str(self.sensors.actuator_current()))
            self.actuator.shutdown_actuator()
            self.state_change_button_activated = False
            self.door_closed = True
            self.indicators.sad()

    def wait_for_action_button_release(self):
        self.logger.info("checking for action button release")
        while bool(self.sensors.check_action_button()):
            self.logger.info("Waiting for action button release: " + str(self.sensors.check_action_button()))
            sleep(0.5)

    def get_logical_door_state(self):
        state = "Closed" if self.door_closed else "Open"
        return state

    def get_operational_state(self):
        return self.state_change_button_activated
