# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pyscada

__version__ = pyscada.__version__
__author__ = pyscada.__author__

default_app_config = 'pyscada.jofra350.apps.PyScadaJofra350Config'

PROTOCOL_ID = 9

parent_process_list = [{'pk': PROTOCOL_ID,
                        'label': 'pyscada.jofra350',
                        'process_class': 'pyscada.jofra350.worker.Process',
                        'process_class_kwargs': '{"dt_set":30}',
                        'enabled': True}]