# -*- coding: utf-8 -*-
"""
doc_test.py

Created on 2018-06-18 by hbldh <henrik.blidh@nedomkull.com>

"""

import os
import json
import time
from mbientlab.metawear import CartesianFloat

from pymetawear.client import MetaWearClient
from pymetawear.exceptions import PyMetaWearException, PyMetaWearDownloadTimeout

c = MetaWearClient('D7:A6:86:19:B5:0D')

# Set data rate to 200 Hz and measuring range to +/- 8g
c.accelerometer.set_settings(data_rate=200.0, data_range=8)

# Log data for 10 seconds.
c.accelerometer.start_logging()
print("Logging accelerometer data...")

time.sleep(10.0)

c.accelerometer.stop_logging()
print("Finished logging.")

# Download the stored data from the MetaWear board.
print("Downloading data...")
download_done = False
n = 0
data = None
while (not download_done) and n < 3:
    try:
        data = c.accelerometer.download_log()
        download_done = True
    except PyMetaWearDownloadTimeout:
        print("Download of log interrupted. Trying to reconnect...")
        c.disconnect()
        c.connect()
        n += 1
if data is None:
    raise PyMetaWearException("Download of logging data failed.")

print("Disconnecting...")
c.disconnect()


# Save the logged data.
class MetaWearDataEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, CartesianFloat):
            return o.x, o.y, o.z
        else:
            return super(MetaWearDataEncoder, self).default(o)


data_file = os.path.join(os.getcwd(), "logged_data.json")
print("Saving the data to file: {0}".format(data_file))
with open("logged_data.json", "wt") as f:
    json.dump(data, f, indent=2, cls=MetaWearDataEncoder)
