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

batt_modules = {}

def params(info):
    info.param_group('batt', label='Battery Simulator Parameters', glob=True)
    info.param('batt.mode', label='Mode', default='Manual', values=[])
    info.param('batt.auto_config', label='Configure battery simulator at beginning of test', default='Disabled',
               values=['Enabled', 'Disabled'])
    for mode, m in batt_modules.iteritems():
        m.params(info)

def batt_init(ts):
    """
    Function to create specific battery simulator implementation instances.

    Each supported battery simulator type should have an entry in the 'mode' parameter conditional.
    Module import for the simulator is done within the conditional so modules only need to be
    present if used.
    """
    mode = ts.param_value('batt.mode')
    sim_module = batt_modules.get(mode)
    if sim_module is not None:
        sim = sim_module.Batt(ts)
    else:
        raise BattError('Unknown battery simulation mode: %s' % mode)

    return sim


class BattError(Exception):
    """
    Exception to wrap all battery generated exceptions.
    """
    pass


class Batt(object):
    """
    Template for battery simulator implementations. This class can be used as a base class or
    independent battery simulator classes can be created containing the methods contained in this class.
    """

    def __init__(self, ts):
        self.ts = ts

    def config(self):
        """ Perform any configuration for the simulation based on the previously provided parameters. """
        pass

    def open(self):
        """ Open the communications resources associated with the battery simulator. """
        pass

    def close(self):
        """ Close any open communications resources associated with the battery simulator. """
        pass

    def conn_status(self, params=None):
        """ Get status of controls (binary True if active).
        :return: Dictionary of active controls.
        """
        pass

def batt_scan():
    global batt_modules
    # scan all files in current directory that match batt_*.py
    package_name = '.'.join(__name__.split('.')[:-1])
    files = glob.glob(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'batt_*.py'))
    for f in files:
        module_name = None
        try:
            module_name = os.path.splitext(os.path.basename(f))[0]
            if package_name:
                module_name = package_name + '.' + module_name
            m = importlib.import_module(module_name)
            if hasattr(m, 'batt_info'):
                info = m.batt_info()
                mode = info.get('mode')
                # place module in module dict
                if mode is not None:
                    batt_modules[mode] = m
            else:
                if module_name is not None and module_name in sys.modules:
                    del sys.modules[module_name]
        except Exception, e:
            if module_name is not None and module_name in sys.modules:
                del sys.modules[module_name]
            raise BattError('Error scanning module %s: %s' % (module_name, str(e)))

# scan for batt modules on import
batt_scan()

if __name__ == "__main__":
    pass
