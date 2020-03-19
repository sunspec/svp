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

# Import all battsim extensions in current directory.
# A battsim extension has a file name of battsim_*.py and contains a function battsim_params(info) that contains
# a dict with the following entries: name, init_func.

# dict of modules found, entries are: name : module_name

battsim_modules = {}


def params(info, id=None, label='Battery Simulator', group_name=None, active=None, active_value=None):
    if group_name is None:
        group_name = BATTSIM_DEFAULT_ID
    else:
        group_name += '.' + BATTSIM_DEFAULT_ID
    if id is not None:
        group_name = group_name + '_' + str(id)
    name = lambda name: group_name + '.' + name

    info.param_group(group_name, label='%s Parameters' % label,  active=active, active_value=active_value, glob=True)
    info.param(name('mode'), label='Mode', default='Disabled', values=['Disabled'])
    info.param(name('auto_config'), label='Configure battery simulator at beginning of test', default='Disabled',
               values=['Enabled', 'Disabled'])
    for mode, m in battsim_modules.items():
        m.params(info, group_name=group_name)

BATTSIM_DEFAULT_ID = 'battsim'


def battsim_init(ts, id=None, group_name=None):
    """
    Function to create specific batt simulator implementation instances.

    Each supported batt simulator type should have an entry in the 'mode' parameter conditional.
    Module import for the simulator is done within the conditional so modules only need to be
    present if used.
    """
    if group_name is None:
        group_name = BATTSIM_DEFAULT_ID
    else:
        group_name += '.' + BATTSIM_DEFAULT_ID
    if id is not None:
        group_name = group_name + '_' + str(id)
    mode = ts.param_value(group_name + '.' + 'mode')
    sim = None
    if mode != 'Disabled':
        sim_module = battsim_modules.get(mode)
        if sim_module is not None:
            sim = sim_module.BattSim(ts, group_name)
        else:
            raise BattSimError('Unknown battery simulation mode: %s' % mode)

    return sim

RELAY_OPEN = 'open'
RELAY_CLOSED = 'closed'
RELAY_UNKNOWN = 'unknown'


class BattSimError(Exception):
    """
    Exception to wrap all battery simulator generated exceptions.
    """
    pass


class BattSim(object):
    """
    Template for battery simulator implementations. This class can be used as a base class or
    independent battery simulator classes can be created containing the methods contained in this class.
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
        Open the communications resources associated with the battery simulator.
        """
        pass

    def close(self):
        """
        Close any open communications resources associated with the battery simulator.
        """
        pass


def battsim_scan():
    global battsim_modules
    # scan all files in current directory that match battsim_*.py
    package_name = '.'.join(__name__.split('.')[:-1])
    files = glob.glob(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'battsim_*.py'))
    for f in files:
        module_name = None
        try:
            module_name = os.path.splitext(os.path.basename(f))[0]
            if package_name:
                module_name = package_name + '.' + module_name
            m = importlib.import_module(module_name)
            if hasattr(m, 'battsim_info'):
                info = m.battsim_info()
                mode = info.get('mode')
                # place module in module dict
                if mode is not None:
                    battsim_modules[mode] = m
            else:
                if module_name is not None and module_name in sys.modules:
                    del sys.modules[module_name]
        except Exception as e:
            if module_name is not None and module_name in sys.modules:
                del sys.modules[module_name]
            raise BattSimError('Error scanning module %s: %s' % (module_name, str(e)))

# scan for battsim modules on import
battsim_scan()

if __name__ == "__main__":
    pass
