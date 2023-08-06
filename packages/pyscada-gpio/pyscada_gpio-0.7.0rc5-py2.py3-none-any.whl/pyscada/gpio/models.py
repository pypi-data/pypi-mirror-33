# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Device
from pyscada.models import Variable

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible
import logging

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class GPIODevice(models.Model):
    gpio_device = models.OneToOneField(Device, null=True, blank=True)
    board_choices = (('rpi', 'Raspberry Pi'),)
    board = models.CharField(max_length=254, choices=board_choices, default='rpi')

    def __str__(self):
        return self.gpio_device.short_name


@python_2_unicode_compatible
class GPIOVariable(models.Model):
    gpio_variable = models.OneToOneField(Variable, null=True, blank=True)
    gpio_mode_choices = (
        ('Polling', (('input', 'Input'),
                     ('input_pull_up', 'Input Pull Up'),
                     ('input_pull_down', 'Input Pull Down'),
                     ('output', 'Output'),),),
        ('Interupt Rising Edge (not implemented)',
         (('input_pull_up_rising', 'Input Pull Up'), ('input_pull_down_rising', 'Input Pull Down'),),),
        ('Interupt Falling Edge (not implemented)',
         (('input_pull_up_falling', 'Input Pull Up'), ('input_pull_down_falling', 'Input Pull Down'),),),
        ('Interupt Both Edges (not implemented)',
         (('input_pull_up_both', 'Input Pull Up'), ('input_pull_down_both', 'Input Pull Down'),),),
    )
    gpio_mode = models.CharField(max_length=254, choices=gpio_mode_choices)
    gpio_pin = models.CharField(max_length=254, help_text="pin number in Board notation (pin number of the pin header)")

    def __str__(self):
        return self.gpio_device.short_name


@receiver(post_save, sender=GPIODevice)
@receiver(post_save, sender=GPIOVariable)
def _reinit_daq_daemons(sender, instance, **kwargs):
    """
    update the daq daemon configuration when changes be applied in the models
    """
    if type(instance) is GPIODevice:
        post_save.send_robust(sender=Device, instance=instance.gpio_device)
    elif type(instance) is GPIOVariable:
        post_save.send_robust(sender=Variable, instance=instance.gpio_variable)
