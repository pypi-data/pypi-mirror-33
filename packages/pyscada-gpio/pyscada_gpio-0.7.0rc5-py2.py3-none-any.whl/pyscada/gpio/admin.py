# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.gpio import PROTOCOL_ID
from pyscada.gpio.models import GPIODevice
from pyscada.gpio.models import GPIOVariable
from pyscada.admin import DeviceAdmin
from pyscada.admin import VariableAdmin
from pyscada.admin import admin_site
from pyscada.models import Device, DeviceProtocol
from pyscada.models import Variable
from django.contrib import admin
import logging

logger = logging.getLogger(__name__)


class ExtendedGPIODevice(Device):
    class Meta:
        proxy = True
        verbose_name = 'GPIO Device'
        verbose_name_plural = 'GPIO Devices'


class GPIODeviceAdminInline(admin.StackedInline):
    model = GPIODevice


class GPIODeviceAdmin(DeviceAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'protocol':
            kwargs['queryset'] = DeviceProtocol.objects.filter(pk=PROTOCOL_ID)
            db_field.default = PROTOCOL_ID
        return super(GPIODeviceAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        """Limit Pages to those that belong to the request's user."""
        qs = super(GPIODeviceAdmin, self).get_queryset(request)
        return qs.filter(protocol_id=PROTOCOL_ID)

    inlines = [
        GPIODeviceAdminInline
    ]


class ExtendedGPIOVariable(Variable):
    class Meta:
        proxy = True
        verbose_name = 'GPIO Variable'
        verbose_name_plural = 'GPIO Variables'


class GPIOVariableAdminInline(admin.StackedInline):
    model = GPIOVariable


class GPIOVariableAdmin(VariableAdmin):
    list_display = ('id', 'name', 'description', 'unit', 'device_name', 'value_class', 'active', 'writeable')
    list_editable = ('active', 'writeable',)
    list_display_links = ('name',)


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'device':
            kwargs['queryset'] = Device.objects.filter(protocol=PROTOCOL_ID)
        return super(GPIOVariableAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        """Limit Pages to those that belong to the request's user."""
        qs = super(GPIOVariableAdmin, self).get_queryset(request)
        return qs.filter(device__protocol_id=PROTOCOL_ID)

    inlines = [
        GPIOVariableAdminInline
    ]


admin_site.register(ExtendedGPIODevice, GPIODeviceAdmin)
admin_site.register(ExtendedGPIOVariable, GPIOVariableAdmin)
