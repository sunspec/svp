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






class HILGenericException(Exception):
    pass

class HILCompileException(Exception):
    pass

class HILModelException(Exception):
    pass

class HILRuntimeException(Exception):
    pass

class HILSimulationException(Exception):
    pass

# Import all hardware-in-the-loop extensions in current directory.
# A hil extension has a file name of hil_*.py and contains a function hil_params(info) that contains
# a dict with the following entries: name, init_func.

# dict of modules found, entries are: name : module_name

hil_modules = {}

def params(info, id=None, label='HIL', group_name=None, active=None, active_value=None):
    if group_name is None:
        group_name = HIL_DEFAULT_ID
    else:
        group_name += '.' + HIL_DEFAULT_ID
    if id is not None:
        group_name = group_name + '_' + str(id)
    name = lambda name: group_name + '.' + name
    info.param_group(group_name, label='%s Parameters' % label, active=active, active_value=active_value, glob=True)
    info.param(name('mode'), label='Mode', default='Disabled', values=['Disabled'])
    for mode, m in hil_modules.items():

        m.params(info, group_name=group_name)

HIL_DEFAULT_ID = 'hil'

def hil_init(ts, id=None, group_name=None):
    """
    Function to create specific HIL implementation instances.

    Each supported HIL type should have an entry in the 'mode' parameter conditional.
    Module import for the simulator is done within the conditional so modules only need to be
    present if used.
    """
    if group_name is None:
        group_name = HIL_DEFAULT_ID
    else:
        group_name += '.' + HIL_DEFAULT_ID
    if id is not None:
        group_name = group_name + '_' + str(id)
    mode = ts.param_value(group_name + '.' + 'mode')
    # ts.log_debug('group_name, %s, mode: %s' % (group_name, mode))
    sim = None
    if mode != 'Disabled':
        sim_module = hil_modules.get(mode)
        if sim_module is not None:

            sim = sim_module.HIL(ts, group_name)
        else:
            raise HILError('Unknown HIL mode: %s' % mode)

    return sim


class HILError(Exception):
    """
    Exception to wrap all HIL generated exceptions.
    """
    pass


class HIL(object):
    """
    Template for HIL implementations. This class can be used as a base class or
    independent HIL classes can be created containing the methods contained in this class.
    """

    def __init__(self, ts, group_name):
        self.ts = ts
        self.group_name = group_name
        self.params = params

        if self.params is None:
            self.params = {}

    def config(self):
        """
        Perform any configuration for the simulation based on the previously
        provided parameters.
        """
        pass

    def open(self):
        """
        Open the communications resources associated with the HIL.
        """
        pass

    def close(self):
        """
        Close any open communications resources associated with the HIL.
        """
        self.stop_simulation()

    def info(self):
        pass

    def control_panel_info(self):
        pass

    def load_schematic(self):
        pass

    def compile_model(self):
        pass

    def load_model_on_hil(self):
        pass

    def init_sim_settings(self):
        pass

    def init_control_panel(self):
        pass

    def voltage(self, voltage=None):
        pass

    def stop_simulation(self):
        pass

    def start_simulation(self):
        pass


def hil_scan():
    global hil_modules
    # scan all files in current directory that match hil_*.py
    package_name = '.'.join(__name__.split('.')[:-1])
    files = glob.glob(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'hil_*.py'))
    for f in files:
        module_name = None
        try:
            module_name = os.path.splitext(os.path.basename(f))[0]
            if package_name:
                module_name = package_name + '.' + module_name
            m = importlib.import_module(module_name)
            if hasattr(m, 'hil_info'):
                info = m.hil_info()
                mode = info.get('mode')
                # place module in module dict
                if mode is not None:
                    hil_modules[mode] = m
            else:
                if module_name is not None and module_name in sys.modules:
                    del sys.modules[module_name]
        except Exception as e:
            if module_name is not None and module_name in sys.modules:
                del sys.modules[module_name]
            raise HILError('Error scanning module %s: %s' % (module_name, str(e)))

# scan for hil modules on import
hil_scan()

if __name__ == "__main__":
    pass
