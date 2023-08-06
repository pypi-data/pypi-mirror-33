# -*- coding: utf-8 -*-
"""
Author: Martin Schröder

helper functions for working with recorded data from the pyscada database

from pyscada.utils.data import read_data
from time import time
a = read_data([226],time()-60*10,time())
"""

import os
import logging
import numpy as np
from time import time
logger = logging.getLogger(__name__)

_DJANGO_SETUP = False


def setup(pyscada_path='/var/www/pyscada/PyScadaServer',project_name=None):
    """
    initialize django for the database adn model access
    :param pyscada_path:
    :param project_name:
    :return:
    """
    global _DJANGO_SETUP
    os.chdir(pyscada_path)
    if project_name is None:
        project_name = pyscada_path.split('/')[-1]
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "%s.settings"%project_name)
    import django
    django.setup()
    _DJANGO_SETUP = True
    return True


def read_values(variable_names,time_from,time_to,mean_value_period=0,no_mean_value=True):
    """
    read data from the database
    :param variable_names:
    :param time_from:
    :param time_to:
    :param mean_value_period:
    :param no_mean_value:
    :return: list of numpy arrays
    """

    if not _DJANGO_SETUP:
        # todo check, throw exception
        if not setup():
            return []

    from pyscada.models import RecordedData, Variable
    # todo check type of variables
    variables = Variable.objects.filter(name__in=variable_names)
    data = RecordedData.objects.get_values_in_time_range(
        variable__in=variables,
        time_min=time_from,
        time_max=time_to,
        query_first_value=True,
        key_is_variable_name=True,
        blow_up=True,
        mean_value_period=mean_value_period if mean_value_period != 0 else 5.0,
        no_mean_value = True if mean_value_period != 0 else no_mean_value
    )

    for key, item in data.items():
        data[key] = np.asarray(item),

    return data


def write_value(variable_name,value,time_start=time(),user=None,blocking=False,timeout=60):
    """

    :param variable_name:
    :param value:
    :param time_start:
    :param user: instance of the writing user, default is None
    :param blocking: wait until write succeeded
    :return:
    """
    if not _DJANGO_SETUP:
        if not setup():
            # todo throw exception
            return False
    from pyscada.models import DeviceWriteTask, Variable
    variable = Variable.objects.filter(name=variable_name).first()
    if not variable:
        # todo throw exception
        return False
    if not variable.writeable:
        # todo throw exception
        return False
    dwt = DeviceWriteTask(variable=variable,value=value,start=time_start,user=user)
    dwt.save()
    if blocking:
        timeout = max(time(),time_start) + timeout
        while timeout < time():
            dwt.refresh_from_db()
            if dwt.done():
                return True
        return False
    else:
        return True
