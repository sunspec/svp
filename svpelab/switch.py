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

# switch controller
SWITCH_CLOSED = True
SWITCH_OPEN = False

switch_modules = {}


def params(info, id=None, label='Switch Controller', group_name=None, active=None, active_value=None):
    if group_name is None:
        group_name = SWITCH_DEFAULT_ID
    else:
        group_name += '.' + SWITCH_DEFAULT_ID
    if id is not None:
        group_name += '_' + str(id)
    print('group_name = %s' % group_name)
    name = lambda name: group_name + '.' + name
    info.param_group(group_name, label='%s Parameters' % label, active=active, active_value=active_value, glob=True)
    print('name = %s' % name('mode'))
    info.param(name('mode'), label='Mode', default='Disabled', values=['Disabled'])
    for mode, m in switch_modules.items():
        m.params(info, group_name=group_name)

SWITCH_DEFAULT_ID = 'switch'


def switch_init(ts, id=None, group_name=None):
    """
    Function to create specific switch implementation instances.
    """
    if group_name is None:
        group_name = SWITCH_DEFAULT_ID
    else:
        group_name += '.' + SWITCH_DEFAULT_ID
    if id is not None:
        group_name = group_name + '_' + str(id)
    mode = ts.param_value(group_name + '.' + 'mode')
    # ts.log_debug('group_name, %s, mode: %s' % (group_name, mode))
    sim = None
    if mode != 'Disabled':
        # ts.log_debug('mode, %s' % (mode))
        switch_module = switch_modules.get(mode)
        # ts.log_debug('switch_module, %s, switch_modules: %s' % (switch_module, switch_modules))
        if switch_module is not None:
            sim = switch_module.Switch(ts, group_name)
        else:
            raise SwitchError('Unknown switch controller mode: %s' % mode)

    return sim


class SwitchError(Exception):
    """
    Exception to wrap all switch generated exceptions.
    """
    pass


class Switch(object):
    """
    Template for sunspec device implementations. This class can be used as a base class or
    independent sunspec device classes can be created containing the methods contained in this class.
    """

    def __init__(self, ts, group_name):
        self.ts = ts
        self.group_name = group_name
        self.device = None
        self.params = {}
        self.switch_state = False

    def info(self):
        """
        Return information string for the switch controller device.
        """
        if self.device is None:
            raise SwitchError('Switch device not initialized')
        return self.device.info()

    def open(self):
        """
        Open communications resources associated with the switch controller device.
        """
        if self.device is None:
            raise SwitchError('Switch device not initialized')
        self.device.open()

    def close(self):
        """
        Close any open communications resources associated with the switch controller device.
        """
        if self.device is None:
            raise SwitchError('Switch device not initialized')
        self.device.close()
        
    def switch_open(self):
        """
        Open the switch associated with this device
        """
        if self.device is None:
            raise SwitchError('Switch device not initialized')
        self.device.switch_open()
        self.switch_state = SWITCH_OPEN
        return self.switch_state
        
    def switch_close(self):
        """
        Close the switch associated with this device
        """
        if self.device is None:
            raise SwitchError('Switch device not initialized')
        self.device.switch_close()
        self.switch_state = SWITCH_CLOSED

    def switch_state(self):
        """
        Get the state of the switch associated with this device
        """
        if self.device is None:
            raise SwitchError('Switch device not initialized')
        return self.switch_state

def switch_scan():
    global switch_modules
    # scan all files in current directory that match switch_*.py
    package_name = '.'.join(__name__.split('.')[:-1])
    files = glob.glob(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'switch_*.py'))
    for f in files:
        module_name = None
        try:
            module_name = os.path.splitext(os.path.basename(f))[0]
            if package_name:
                module_name = package_name + '.' + module_name
            m = importlib.import_module(module_name)
            if hasattr(m, 'switch_info'):
                info = m.switch_info()
                mode = info.get('mode')
                # place module in module dict
                if mode is not None:
                    switch_modules[mode] = m
            else:
                if module_name is not None and module_name in sys.modules:
                    del sys.modules[module_name]
        except Exception as e:
            if module_name is not None and module_name in sys.modules:
                del sys.modules[module_name]
            raise SwitchError('Error scanning module %s: %s' % (module_name, str(e)))

# scan for switch modules on import
switch_scan()

if __name__ == "__main__":
    pass
