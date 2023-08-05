#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`accelerometer`
==================

Updated by lkasso <hello@mbientlab.com>
Created by hbldh <henrik.blidh@nedomkull.com>
Created on 2016-04-10

"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import time
import math

from pymetawear.discover import select_device
from pymetawear.client import MetaWearClient

address = select_device()
c = MetaWearClient(str(address), debug=False)
print("New client created: {0}".format(c))

c.accelerometer.set_settings(data_rate=3.125, data_range=4.0)

time.sleep(1.0)


class UpsideDownDetector(object):

    def __init__(self, t_limit=5.0):
        self.t_limit = t_limit * 1000
        self._upside_down_started = None
        self._have_sent_warning = False

    def __call__(self, data):
        x = data['value'].x
        y = data['value'].y
        z = data['value'].z
        epoch = data['epoch']
        norm = math.sqrt(x**2 + y**2 + z**2)
        if z/norm < -0.75:
            if not self._upside_down_started:
                self._upside_down_started = epoch
            if (epoch - self._upside_down_started) > self.t_limit and \
                    not self._have_sent_warning:
                print("WARNING: Upside down for {0:.2f} "
                      "seconds! Sending SMS...".format(self.t_limit / 1000))
                self._have_sent_warning = True
        else:
            self._upside_down_started = None
            self._have_sent_warning = False


print("Subscribing to accelerometer signal notifications...")
c.accelerometer.high_frequency_stream = False

detector = UpsideDownDetector()
c.accelerometer.notifications(detector)

try:
    time.sleep(600.0)
except KeyboardInterrupt:
    print("Aborting.")

print("Unsubscribe to notification...")
c.accelerometer.notifications(None)

time.sleep(5.0)

c.disconnect()
