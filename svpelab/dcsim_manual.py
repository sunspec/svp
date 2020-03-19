"""
Copyright (c) 2017, Sandia National Labs and SunSpec Alliance
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice, this
list of conditions and the following disclaimer in the documentation and/or
other materials provided with the distribution.

Neither the names of the Sandia National Labs and SunSpec Alliance nor the names of its
contributors may be used to endorse or promote products derived from
this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Questions can be directed to support@sunspec.org
"""

import os
import time
from . import dcsim

chroma_info = {
    'name': os.path.splitext(os.path.basename(__file__))[0],
    'mode': 'Manual'
}

def dc_info():
    return chroma_info

def params(info, group_name=None):
    gname = lambda name: group_name + '.' + name
    pname = lambda name: group_name + '.' + GROUP_NAME + '.' + name
    mode = chroma_info['mode']
    info.param_add_value(gname('mode'), mode)
    info.param_group(gname(GROUP_NAME), label='%s Parameters' % mode,
                     active=gname('mode'),  active_value=mode, glob=True)

GROUP_NAME = 'manual'

class DCSim(dcsim.DCSim):

    """
    Implementation for manual
    """
    def __init__(self, ts, group_name):
        dcsim.DCSim.__init__(self, ts, group_name)

    def _param_value(self, name):
        return self.ts.param_value(self.group_name + '.' + GROUP_NAME + '.' + name)

    def info(self):
        """
        Return information string for the device.
        """
        return 'Manual DC Power Supply'

    def config(self):
        """
        Perform any configuration for the simulation based on the previously
        provided parameters.
        """
        self.ts.confirm('Configure DC Power Supply.')

    def output(self, start=None):
        """
        Start/stop power supply output

        start: if False stop output, if True start output
        """
        if start is not None:
            if start is True:
                self.ts.confirm('Start DC Power Supply.')
            else:
                self.ts.confirm('Stop DC Power Supply.')
        else:  # get output state
            return self.ts.prompt('What is the DC Power Supply status ("on"/"off")?')

    def output_mode(self, mode=None):
        """
        Start/stop power supply output
        """
        pass

    def current(self, current=None):
        """
        Set the value for current if provided. If none provided, obtains the value for current.
        """
        if current is not None:
            self.ts.confirm('Set DC Power Supply current to %s.' % current)
        else:
            current = self.ts.prompt('What is the DC Power Supply current (A)?')
        return current

    def current_max(self, current=None):
        """
        Set the value for max current if provided. If none provided, obtains
        the value for max current.
        """
        if current is not None:
            self.ts.confirm('Set DC Power Supply max current to %s.' % current)
        else:
            current = self.ts.prompt('What is the DC Power Supply max current (A)?')
        return current

    def voltage(self, voltage=None):
        """
        Set the value for voltage if provided. If none provided, obtains
        the value for voltage.
        """
        if voltage is not None:
            self.ts.confirm('Set DC Power Supply voltage to %s.' % voltage)
        else:
            voltage = self.ts.prompt('What is the DC Power Supply voltage (V)?')
        return voltage

    def voltage_max(self, voltage=None):
        """
        Set the value for max voltage if provided. If none provided, obtains
        the value for max voltage.
        """
        if voltage is not None:
            self.ts.confirm('Set DC Power Supply max voltage to %s.' % voltage)
        else:
            voltage = self.ts.prompt('What is the DC Power Supply max voltage (V)?')
        return voltage

    def voltage_min(self, voltage=None):
        """
        Set the value for min voltage if provided. If none provided, obtains
        the value for min voltage.
        """
        if voltage is not None:
            self.ts.confirm('Set DC Power Supply min voltage to %s.' % voltage)
        else:
            voltage = self.ts.prompt('What is the DC Power Supply min voltage (V)?')
        return voltage

    def relay(self, state=None):
        """
        Set the state of the relay if provided. Valid states are: RELAY_OPEN,
        RELAY_CLOSED. If none is provided, obtains the state of the relay.
        """
        if state is not None:
            self.ts.confirm('Set DC Power Supply relay to %s.' % state)
        else:
            state = self.ts.prompt('What is the DC Power Supply relay state ("open"/"closed"/"unknown")?')
        return state
