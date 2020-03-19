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

from . import wavegen
from . import gridsim

manual_info = {
    'name': os.path.splitext(os.path.basename(__file__))[0],
    'mode': 'Manual'
}

def gridsim_info():
    return manual_info


def params(info, group_name):
    gname = lambda name: group_name + '.' + name
    pname = lambda name: group_name + '.' + GROUP_NAME + '.' + name
    mode = manual_info['mode']
    info.param_add_value(gname('mode'), mode)
    info.param_group(gname(GROUP_NAME), label='%s Parameters' % mode, active=gname('mode'), active_value=mode,
                     glob=True)
    info.param(pname('phases'), label='Phases', default=1, values=[1, 2, 3])
    info.param(pname('v_nom'), label='Nominal voltage for all phases', default=120.0)
    info.param(pname('v_max'), label='Max Voltage', default=200.0)
    info.param(pname('i_max'), label='Max Current', default=10.0)
    info.param(pname('freq'), label='Frequency', default=60.0)
    info.param(pname('comm'), label='Communications Interface', default='VISA', values=['GPIB', 'VISA', 'WAVEGEN'])
    info.param(pname('gpib_device'), label='GPIB address', active=pname('comm'), active_value=['GPIB'],
               default='GPIB0::17::INSTR')
    info.param(pname('visa_device'), label='VISA address', active=pname('comm'), active_value=['VISA'],
               default='GPIB0::17::INSTR')


GROUP_NAME = 'manual'


class GridSim(gridsim.GridSim):

    def __init__(self, ts, group_name, params=None):
        gridsim.GridSim.__init__(self, ts, group_name, params)

        if ts.confirm('Please run the grid simulator profile.') is False:
            raise gridsim.GridSimError('Aborted grid simulation')

        ts.log('Grid sim init')
        self.v_nom_param = self._param_value('v_nom')
        self.v_max_param = self._param_value('v_max')
        self.i_max_param = self._param_value('i_max')
        self.freq_param = self._param_value('freq')
        self.phases = self._param_value('phases')
        self.profile_name = ts.param_value('profile.profile_name')
        self.comm = self._param_value('comm')
        self.gpib_bus_address = self._param_value('gpib_bus_address')
        self.gpib_board = self._param_value('gpib_board')
        self.visa_device = self._param_value('visa_device')
        self.cmd_str = ''
        self.cmd_str = ''

        self._cmd = None
        self._query = None

    def _param_value(self, name):
        return self.ts.param_value(self.group_name + '.' + GROUP_NAME + '.' + name)