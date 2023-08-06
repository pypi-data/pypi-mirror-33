# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pyscada

__version__ = '0.7.0rc5'
__author__ = 'Martin Schröder'

default_app_config = 'pyscada.gpio.apps.PyScadaGPIOConfig'

PROTOCOL_ID = 10

parent_process_list = [{'pk': PROTOCOL_ID,
                        'label': 'pyscada.gpio',
                        'process_class': 'pyscada.gpio.worker.Process',
                        'process_class_kwargs': '{"dt_set":30}',
                        'enabled': True}]