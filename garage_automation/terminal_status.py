#!/usr/bin/python3

# This class manages non-scrolling output to the terminal
# This allows a better realtime view of voltage and current and sensor state without having to dig
# through lots of debug output in the log, of course all of this data still goes to the log file
# todo set flag to disable this when run as deamon

import threading


class TerminalStatus:
    def update_terminal(sensors, control):
        """
        @type sensors: garage_automation.Sensors
        """

        print('Voltage: ' + str(sensors.actuator_voltage())

            + ' Current: '            + str(round(sensors.actuator_current(), 2))
            + ' bolt sensor: '        + str(sensors.check_bolt_closed_limit_switch())
            + ' door sensor: '        + str(sensors.check_door_sensor())
            + ' Logical door state: ' + control.get_logical_door_state()
            + ' Operational state: '  + str(control.get_operational_state())
            + ' threads: ' + str(threading.active_count())
            + '                ', end='\r')





