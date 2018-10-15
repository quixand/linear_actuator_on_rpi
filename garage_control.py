#!/usr/bin/python3


# http://howtomechatronics.com/tutorials/arduino/arduino-dc-motor-control-tutorial-l298n-pwm-h-bridge/
# http://www.instructables.com/id/Arduino-Modules-L298N-Dual-H-Bridge-Motor-Controll/
# export PYTHONPATH=~/.local/lib/python2.7/
# try gpio readall for pinouts
# mount devpi locally
# sshfs -o idmap=user,nonempty pi@192.168.0.41:/home/pi ~/system/configurations/pi/remote/garagedoorpi/
# or for macbbok
# sshfs -o idmap=user,nonempty pi@192.168.0.41:/home/pi /fusemounts/garagedoorpi
# sync to dev pi from local
# while true;do rsync -avh --progress --delete /home/nick/system/configurations/pi/ansible/code/door_control ~/system/configurations/pi/remote/garagedoorpi/;sleep 5;done|grep -vE 'sent|total|sending'
# for macbook
# while true;do rsync -avh --progress --delete /Users/foxnic01/Documents/resillio/MSI-configurations/pi/ansible/code/door_control /fusemounts/garagedoorpi/;sleep 5;done|grep -vE 'sent|total|sending'
# run on remote
# clear; echo "" > /var/log/automation/pi.log ;./garage_control.py
# monitor log on pi
# watch cat /var/log/automation/pi.log
# check threads
# pstree `pidof python3`

# on script start if we don't know the position of the actuator from the limit switch we perform an initial open
# operation when the button is pushed, this safely puts us into a known state

# !! critical !!
# todo - make green LED flash while actuating
# todo - create systemd daemon + set flag to output CLI status info
#   http://blog.scphillips.com/posts/2013/07/getting-a-python-script-to-run-in-the-background-as-a-service-on-boot/
# todo - write a opsview compatible file or SIG to provide status

# improvements
# TODO - create pip requirements doc
# todo - install with ansible
# todo - overcurrent logs but does not seem to trigger error state
# todo - multiple sensor failures are not registered, only the first
# todo - extend status LEDs to outside


# todo check for door or bolt sensor changes outside of operation and trigger alarm
# todo spawn thread for overcurrent detection so its not affected by blocking operations

# import sys
import RPi.GPIO as GPIO
import time
import logging
import garage_automation

# todo - move to file
configs = {
    'over_current_threshold': 1500,  # milliamps
    'actuator_full_stroke_duration': 10,  # seconds
    'led_red_pin': 16,
    'led_green_pin': 18
}

# todo - move to configs
actuator_pin_forwards = 24
actuator_pin_backwards = 26
switch_input = 7
bolts_closed_sensor = 11

door_closed_sensor = 13


# this log path must exist as the logging class can't create it, we need to create on deployment with ansible
# logging.basicConfig(format='%(asctime)s %(message)s', filename='/var/log/automation/pi.log', level=logging.DEBUG)
logging.basicConfig(format='%(asctime)s %(message)s', filename='/var/log/automation/pi.log', level=logging.INFO)
# logging.debug('This message should go to the log file')
logging.info('Script startup')
# logging.warning('And this, too')


try:
    GPIO.setmode(GPIO.BOARD)

    GPIO.setup(switch_input, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(bolts_closed_sensor, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    # GPIO.setup(bolts_open_sensor, GPIO.IN)
    # enable internal pull-down resistor
    GPIO.setup(door_closed_sensor, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    GPIO.setup(actuator_pin_backwards, GPIO.OUT)
    GPIO.setup(actuator_pin_forwards, GPIO.OUT)
    # make sure actuator pins are deactivated
    GPIO.output(actuator_pin_forwards, GPIO.LOW)
    GPIO.output(actuator_pin_backwards, GPIO.LOW)

    GPIO.setup(configs['led_green_pin'], GPIO.OUT)
    GPIO.setup(configs['led_red_pin'], GPIO.OUT)
    # make sure LED's are in default alarm/not ready state
    GPIO.output(configs['led_green_pin'], GPIO.LOW)
    GPIO.output(configs['led_red_pin'], GPIO.HIGH)


except Exception as e:
    logging.error("RuntimeError problem with GPIO init")
    logging.debug("exception:" + str(e))
    GPIO.cleanup()

sensors = None
control = None
indicators = None
try:
    indicators = garage_automation.Indicators(logging, GPIO, configs)
    sensors = garage_automation.Sensors(logging, bolts_closed_sensor, door_closed_sensor, switch_input)
    actuator = garage_automation.Actuator(logging, GPIO, actuator_pin_forwards, actuator_pin_backwards)
    control = garage_automation.Control(logging, actuator, sensors, indicators, configs)
except Exception as e:
    logging.error("ERROR initialising control classes")
    logging.error("exception:" + str(e))
    GPIO.cleanup()


# Use BCM GPIO references
# instead of physical pin numbers
#GPIO.setmode(GPIO.BCM)
# mode = GPIO.getmode()
# print " mode =" + str(mode)

try:
    # on startup, if we don't have a signal from the actuator limit switch we should assume its not fully retracted
    # so to get into a known state we need to retract the actuator on the first action request
    # after that we should always know what state we are in and this makes the rest of the logic much simpler

    while True:
        if control.check_locked():
            break

        if sensors.check_action_button():
            control.on_start_retract()
            break

        time.sleep(0.1)

# Main loop
    while True:
        if sensors.check_action_button():
            control.change_state()
        # no interupts on the pi so we need to monitor the switch pin, better with threads?
        # https://stackoverflow.com/questions/22180915/non-polling-non-blocking-timer
        # http://raspi.tv/2013/how-to-use-interrupts-with-python-on-the-raspberry-pi-and-rpi-gpio-part-3

        control.check_lock_state()
        # todo set flag to enable this as required, debug manual run etc
        # garage_automation.TerminalStatus.update_terminal(sensors, control)
        sensors.log_sensor_state()
        # indicators.heartbeat() kind of annoying
        time.sleep(0.2)

except KeyboardInterrupt as e:
    logging.warning('Cought KeyboardInterrupt' + str(e))
except Exception as e:
    logging.error("ERROR Unhandled exception")
    logging.error("Exception type", e.__class__.__name__)
    exit()

finally:
    GPIO.cleanup()
    logging.info("Garage Automation daemon terminating. GPIO cleaned up")
