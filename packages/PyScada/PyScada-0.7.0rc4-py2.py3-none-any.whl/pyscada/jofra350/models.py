# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Variable, Device

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible
import logging

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class Jofra350Device(models.Model):
    jofra350_device = models.OneToOneField(Device)
    ip_address = models.GenericIPAddressField(default='127.0.0.1')
    port = models.PositiveSmallIntegerField(default=17001)

    def __str__(self):
        return self.jofra350_device.short_name


@python_2_unicode_compatible
class Jofra350Variable(models.Model):
    jofra350_variable = models.OneToOneField(Variable)
    sensor_type_choices = (('INT_RTD', 'Internal Reference Sensor'), ('REF_RTD', 'External Reference Sensor'),)
    sensor_type = models.CharField(default='', max_length=10, choices=sensor_type_choices)
    field_type_choices = (
        ('InputValue', 'InputValue'),
        ('SetFollows', 'SetFollows'),
        ('StabilityRequiredSeconds', 'StabilityRequiredSeconds'),
        ('StabilitySecondsLeft', 'StabilitySecondsLeft'),
        ('StabilityTolerance', 'StabilityTolerance'),
        ('TemperatureValue', 'TemperatureValue'),)
    field_type = models.CharField(default='', max_length=30, choices=field_type_choices)

    def convert_value(self, value):
        if value is None:
            return value
        if self.field_type in ['StabilityRequiredSeconds', 'StabilityTolerance', 'InputValue']:
            return value
        if self.field_type == 'TemperatureValue':
            # convert from K to ° C
            return value - 273.15
        if self.field_type == 'StabilitySecondsLeft':
            return -value
        return value

    def __str__(self):
        return self.jofra350_variable.name

class ExtendedJofra350Device(Device):
    class Meta:
        proxy = True
        verbose_name = 'Jofra350 Device'
        verbose_name_plural = 'Jofra350 Devices'


class ExtendedJofra350Variable(Variable):
    class Meta:
        proxy = True
        verbose_name = 'Jofra350 Variable'
        verbose_name_plural = 'Jofra350 Variables'


@receiver(post_save, sender=Jofra350Variable)
@receiver(post_save, sender=Jofra350Device)
@receiver(post_save, sender=ExtendedJofra350Device)
@receiver(post_save, sender=ExtendedJofra350Variable)
def _reinit_daq_daemons(sender,instance, **kwargs):
    """
    update the daq daemon configuration when changes be applied in the models
    """
    if type(instance) is Jofra350Device:
        post_save.send_robust(sender=Device,instance=instance.jofra350_device)
    elif type(instance) is Jofra350Variable:
        post_save.send_robust(sender=Variable, instance=instance.jofra350_variable)
    elif type(instance) is ExtendedJofra350Variable:
        post_save.send_robust(sender=Variable, instance=Variable.objects.get(pk=instance.pk))
    elif type(instance) is ExtendedJofra350Device:
        post_save.send_robust(sender=Device, instance=Device.objects.get(pk=instance.pk))