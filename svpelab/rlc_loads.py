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

rlc_loads_modules = {}

def params(info, id=None, label='RLC Loads'):
    group_name = RLC_DEFAULT_ID
    if id is not None:
        group_name = group_name + '_' + str(id)
    print 'group_name = %s' % group_name
    name = lambda name: group_name + '.' + name
    info.param_group(group_name, label='%s Parameters' % label, glob=True)
    print 'name = %s' % name('mode')
    info.param(name('mode'), label='Mode', default='Manual', values=[])
    for mode, m in rlc_loads_modules.iteritems():
        m.params(info, group_name=group_name)

RLC_DEFAULT_ID = 'rlc_loads'
S3_OPEN = 'open'
S3_CLOSED = 'closed'

def rlc_loads_init(ts, id=None):
    """
    Function to create specific rlc_loads implementation instances.
    """
    group_name = RLC_DEFAULT_ID
    if id is not None:
        group_name = group_name + '_' + str(id)
    print 'run group_name = %s' % group_name
    mode = ts.param_value(group_name + '.' + 'mode')
    sim_module = rlc_loads_modules.get(mode)
    if sim_module is not None:
        sim = sim_module.RLC(ts, group_name)
    else:
        raise RLCError('Unknown data acquisition system mode: %s' % mode)

    return sim


class RLCError(Exception):
    """
    Exception to wrap all rlc_loads generated exceptions.
    """
    pass


class RLC(object):
    """
    Template for RLC load implementations. This class can be used as a base class or
    independent RLC load classes can be created containing the methods contained in this class.
    """

    def __init__(self, ts, group_name):
        self.ts = ts
        self.group_name = group_name

    def resistance(self, r=None):
        pass

    def inductance(self, i=None):
        pass

    def capacitance(self, c=None):
        pass

    def capacitor_q(self, q=None):
        pass

    def inductor_q(self, q=None):
        pass

    def resistance_p(self, p=None):
        pass

    def tune_current(self, i=None):
        pass

    def switch_s3(self, p=None):
        """
        Opening and closing the S3 switch in the unintentional islanding tests
        """
        pass

def rlc_loads_scan():
    global rlc_loads_modules
    # scan all files in current directory that match rlc_loads_*.py
    package_name = '.'.join(__name__.split('.')[:-1])
    files = glob.glob(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'rlc_loads_*.py'))
    for f in files:
        module_name = None
        try:
            module_name = os.path.splitext(os.path.basename(f))[0]
            if package_name:
                module_name = package_name + '.' + module_name
            m = importlib.import_module(module_name)
            if hasattr(m, 'rlc_loads_info'):
                info = m.rlc_loads_info()
                mode = info.get('mode')
                # place module in module dict
                if mode is not None:
                    rlc_loads_modules[mode] = m
            else:
                if module_name is not None and module_name in sys.modules:
                    del sys.modules[module_name]
        except Exception, e:
            if module_name is not None and module_name in sys.modules:
                del sys.modules[module_name]
            raise RLCError('Error scanning module %s: %s' % (module_name, str(e)))

# scan for rlc_loads modules on import
rlc_loads_scan()

if __name__ == "__main__":
    pass
