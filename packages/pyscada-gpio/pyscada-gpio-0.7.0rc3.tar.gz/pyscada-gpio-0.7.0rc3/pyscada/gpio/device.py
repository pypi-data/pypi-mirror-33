# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pyscada

try:
    import RPi.GPIO as GPIO
    _DRIVER_RPI_OK = True
except ImportError:
    _DRIVER_RPI_OK = False

from math import isnan, isinf
from time import time
import sys


import logging

logger = logging.getLogger(__name__)
_debug = 1


class Device:
    """
    GPIO device
    """

    class Device:
        def __init__(self, device):
            self.variables = []
            self.device = device
            for var in device.variable_set.filter(active=1):
                if not hasattr(var, 'gpiovariable'):
                    continue
                self.variables.append(var)
                if var.gpiovariable.gpio_mode_choices == 'input_pull_up':
                    GPIO.setup(int(var.gpiovariable.gpio_pin), GPIO.IN, pull_up_down=GPIO.PUD_UP)
                elif var.gpiovariable.gpio_mode_choices == 'input_pull_down':
                    GPIO.setup(int(var.gpiovariable.gpio_pin), GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
                elif var.gpiovariable.gpio_mode_choices == 'input':
                    GPIO.setup(int(var.gpiovariable.gpio_pin), GPIO.IN)
                elif var.gpiovariable.gpio_mode_choices == 'output':
                    GPIO.setup(int(var.gpiovariable.gpio_pin), GPIO.OUT)

            if _DRIVER_RPI_OK:
                GPIO.setmode(GPIO.BOARD)
            #todo add cleanup

        def request_data(self):
            if not _DRIVER_RPI_OK:
                return None
            output = []
            for item in self.variables:
                timestamp = time()
                #value = None

                value = GPIO.input(int(item.gpiovariable.gpio_pin))
                if value is not None and item.update_value(value, timestamp):
                    output.append(item.create_recorded_data_element())

            return output

        def write_data(self, variable_id, value):
            """
            write value to single gpio pin
            """
            if not self.variables[variable_id].writeable:
                return False

            if not self.variables[variable_id].gpiovariable.gpio_mode_choices == 'output':
                return False

            GPIO.output(int(self.variables[variable_id].gpiovariable.gpio_pin), value)
            return True

