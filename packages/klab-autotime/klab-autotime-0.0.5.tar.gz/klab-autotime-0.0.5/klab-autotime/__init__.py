from __future__ import print_function

import time
import sys

from IPython.core.magics.execution import _format_time as format_delta


class LineWatcher(object):
    """Class that implements a basic timer.

    Notes
    -----
    * Register the `start` and `stop` methods with the IPython events API.
    """

    def __init__(self):
        self.start_time = 0.0

    def start_timer(self):
        if sys.version_info.major == 2:
            self.start_time = time.time()
        else:
            self.start_time = time.monotonic()

    def stop_timer(self):
        if sys.version_info.major == 2:
            stop_time = time.time()
        else:
            stop_time = time.monotonic()

        if self.start_time:
            diff = stop_time - self.start_time
            assert diff > 0
            print('time: {}'.format(format_delta(diff)))

lineTimer = LineWatcher()

def load_ipython_extension(ip):
    ip.events.register('pre_execute', lineTimer.start_timer)
    ip.events.register('post_execute', lineTimer.stop_timer)


def unload_ipython_extension(ip):
    ip.events.unregister('pre_execute', lineTimer.start_timer)
    ip.events.unregister('post_execute', lineTimer.stop_timer)
