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

import sys
import os
import glob
import importlib

# Import all dcsim extensions in current directory.
# A dcsim extension has a file name of dcsim_*.py and contains a function dcsim_params(info) that contains
# a dict with the following entries: name, init_func.

# dict of modules found, entries are: name : module_name

dcsim_modules = {}

def params(info, id=None, label='DC Simulator', group_name=None, active=None, active_value=None):
    if group_name is None:
        group_name = DCSIM_DEFAULT_ID
    else:
        group_name += '.' + DCSIM_DEFAULT_ID
    if id is not None:
        group_name = group_name + '_' + str(id)
    name = lambda name: group_name + '.' + name
    info.param_group(group_name, label='%s Parameters' % label, active=active, active_value=active_value, glob=True)
    info.param(name('mode'), label='Mode', default='Disabled', values=['Disabled'])
    info.param(name('auto_config'), label='Configure dc simulator at beginning of test', default='Disabled',
               values=['Enabled', 'Disabled'])
    for mode, m in dcsim_modules.items():
        m.params(info, group_name=group_name)

DCSIM_DEFAULT_ID = 'dcsim'

def dcsim_init(ts, id=None, group_name=None):
    """
    Function to create specific dc simulator implementation instances.

    Each supported dc simulator type should have an entry in the 'mode' parameter conditional.
    Module import for the simulator is done within the conditional so modules only need to be
    present if used.
    """
    if group_name is None:
        group_name = DCSIM_DEFAULT_ID
    else:
        group_name += '.' + DCSIM_DEFAULT_ID
    if id is not None:
        group_name = group_name + '_' + str(id)
    mode = ts.param_value(group_name + '.' + 'mode')
    sim = None
    if mode != 'Disabled':
        sim_module = dcsim_modules.get(mode)
        if sim_module is not None:
            sim = sim_module.DCSim(ts, group_name)
        else:
            raise DCSimError('Unknown dc simulation mode: %s' % mode)

    return sim

RELAY_OPEN = 'open'
RELAY_CLOSED = 'closed'
RELAY_UNKNOWN = 'unknown'

class DCSimError(Exception):
    """
    Exception to wrap all dc simulator generated exceptions.
    """
    pass


class DCSim(object):
    """
    Template for dc simulator implementations. This class can be used as a base class or
    independent dc simulator classes can be created containing the methods contained in this class.
    """

    def __init__(self, ts, group_name, params=None):
        self.ts = ts
        self.group_name = group_name
        self.params = params
        if self.params is None:
            self.params = {}
        self.auto_config = self._group_param_value('auto_config')

    def _group_param_value(self, name):
        return self.ts.param_value(self.group_name + '.' + name)

    def info(self):
        """
        Return information string for the device.
        """
        pass

    def config(self):
        """
        Perform any configuration for the simulation based on the previously
        provided parameters.
        """
        pass

    def open(self):
        """
        Open the communications resources associated with the dc simulator.
        """
        pass

    def close(self):
        """
        Close any open communications resources associated with the dc simulator.
        """
        pass

    def output(self, start=None):
        """
        Start/stop power supply output

        start: if False stop output, if True start output
        """
        if start is not None:
            if start is True:
                pass  # start output
            else:
                pass  # stop output
        else:  # get output state
            pass

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
            pass
        else:
            current = 0.0
        return current

    def current_max(self, current=None):
        """
        Set the value for max current if provided. If none provided, obtains
        the value for max current.
        """
        if current is not None:
            pass
        else:
            current = 0.0
        return current

    def voltage(self, voltage=None):
        """
        Set the value for voltage if provided. If none provided, obtains
        the value for voltage.
        """
        if voltage is not None:
            pass
        else:
            voltage = 0.0
        return voltage

    def voltage_max(self, voltage=None):
        """
        Set the value for max voltage if provided. If none provided, obtains
        the value for max voltage.
        """
        if voltage is not None:
            pass
        else:
            voltage = 0.0
        return voltage

    def voltage_min(self, voltage=None):
        """
        Set the value for min voltage if provided. If none provided, obtains
        the value for min voltage.
        """
        if voltage is not None:
            pass
        else:
            voltage = 0.0
        return voltage

    def relay(self, state=None):
        """
        Set the state of the relay if provided. Valid states are: RELAY_OPEN,
        RELAY_CLOSED. If none is provided, obtains the state of the relay.
        """
        if state is not None:
            pass
        else:
            state = RELAY_OPEN
        return state

def dcsim_scan():
    global dcsim_modules
    # scan all files in current directory that match dcsim_*.py
    package_name = '.'.join(__name__.split('.')[:-1])
    files = glob.glob(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'dcsim_*.py'))
    for f in files:
        module_name = None
        try:
            module_name = os.path.splitext(os.path.basename(f))[0]
            if package_name:
                module_name = package_name + '.' + module_name
            m = importlib.import_module(module_name)
            if hasattr(m, 'dcsim_info'):
                info = m.dcsim_info()
                mode = info.get('mode')
                # place module in module dict
                if mode is not None:
                    dcsim_modules[mode] = m
            else:
                if module_name is not None and module_name in sys.modules:
                    del sys.modules[module_name]
        except Exception as e:
            if module_name is not None and module_name in sys.modules:
                del sys.modules[module_name]
            raise DCSimError('Error scanning module %s: %s' % (module_name, str(e)))

# scan for dcsim modules on import
dcsim_scan()

if __name__ == "__main__":
    pass
