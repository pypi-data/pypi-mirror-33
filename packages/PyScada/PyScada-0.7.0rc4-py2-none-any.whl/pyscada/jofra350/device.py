# -*- coding: utf-8 -*-
from __future__ import unicode_literals

try:
    from .ametek import Jofra350
    driver_ok = True
except ImportError:
    driver_ok = False

from time import time
import logging

logger = logging.getLogger(__name__)


class Device:
    def __init__(self, device):
        self.variables = []
        self.device = device
        for var in device.variable_set.filter(active=1):
            if not hasattr(var, 'jofra350variable'):
                continue
            self.variables.append(var)

    def request_data(self):
        """

        """
        if not driver_ok:
            return None
        # read in a list of device devices from w1 master
        dev = Jofra350(self.device.jofra350device.ip_address, self.device.jofra350device.port)
        response = dev.get_request(request_type='SensorManager.LiveSensors', seq=58, retries=6)
        output = []
        if response is False or response is None:
            return output

        for item in self.variables:
            timestamp = time()
            value = None
            if item.jofra350variable.sensor_type.upper() in response.keys():
                if response[item.jofra350variable.sensor_type.upper()][item.jofra350variable.field_type] is not None:
                    value = item.jofra350variable.convert_value( \
                        response[item.jofra350variable.sensor_type.upper()][item.jofra350variable.field_type])
            # update variable
            if value is not None and item.update_value(value, timestamp):
                output.append(item.create_recorded_data_element())

        return output
