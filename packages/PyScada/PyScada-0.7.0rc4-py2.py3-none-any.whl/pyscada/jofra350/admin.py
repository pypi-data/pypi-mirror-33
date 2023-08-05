# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.jofra350.models import Jofra350Variable, Jofra350Device, ExtendedJofra350Device, ExtendedJofra350Variable
from pyscada.jofra350 import PROTOCOL_ID
from pyscada.admin import admin_site
from pyscada.admin import DeviceAdmin
from pyscada.admin import VariableAdmin
from pyscada.models import Device, DeviceProtocol

from django.contrib import admin
import logging

logger = logging.getLogger(__name__)


class Jofra350DeviceAdminInline(admin.StackedInline):
    model = Jofra350Device

class Jofra350DeviceAdmin(DeviceAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'protocol':
            kwargs['queryset'] = DeviceProtocol.objects.filter(pk=PROTOCOL_ID)
            db_field.default = PROTOCOL_ID
        return super(Jofra350DeviceAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        """Limit Pages to those that belong to the request's user."""
        qs = super(Jofra350DeviceAdmin, self).get_queryset(request)
        return qs.filter(protocol_id=PROTOCOL_ID)

    inlines = [
        Jofra350DeviceAdminInline
    ]


class Jofra350VariableAdminInline(admin.StackedInline):
    model = Jofra350Variable


class Jofra350VariableAdmin(VariableAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'device':
            kwargs['queryset'] = Device.objects.filter(protocol=PROTOCOL_ID)
        return super(Jofra350VariableAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        """Limit Pages to those that belong to the request's user."""
        qs = super(Jofra350VariableAdmin, self).get_queryset(request)
        return qs.filter(device__protocol_id=PROTOCOL_ID)

    inlines = [
        Jofra350VariableAdminInline
    ]

admin_site.register(ExtendedJofra350Device, Jofra350DeviceAdmin)
admin_site.register(ExtendedJofra350Variable, Jofra350VariableAdmin)
