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

from . import device_wavegen_manual
from . import wavegen

manual_info = {
    'name': os.path.splitext(os.path.basename(__file__))[0],
    'mode': 'Manual'
}

def wavegen_info():
    return manual_info

def params(info, group_name):
    gname = lambda name: group_name + '.' + name
    pname = lambda name: group_name + '.' + GROUP_NAME + '.' + name
    mode = manual_info['mode']
    info.param_add_value(gname('mode'), mode)
    info.param_group(gname(GROUP_NAME), label='%s Parameters' % mode, active=gname('mode'), active_value=mode,
                     glob=True)
    info.param(pname('comm'), label='Communications Interface', default='VISA', values=['Network', 'VISA', 'GPIB'])
    info.param(pname('gen_mode'), label='Function Generator mode', default='ON', values=['ON', 'OFF'])
    info.param(pname('visa_address'), label='VISA address', active=pname('comm'), active_value=['VISA'],
               default='GPIB0::10::INSTR')
    info.param(pname('ip_addr'), label='IP Address', active=pname('comm'), active_value=['Network'],
               default='10.0.0.115')

GROUP_NAME = 'manual'

class Wavegen(wavegen.Wavegen):

    def __init__(self, ts, group_name, points=None):
        wavegen.Wavegen.__init__(self, ts, group_name)
        self.params['comm'] = self._param_value('comm')
        self.params['gen_mode'] = self._param_value('gen_mode')
        self.params['ip_addr'] = self._param_value('ip_addr')
        self.params['visa_address'] = self._param_value('visa_address')

        self.device = device_wavegen_manual.Device(self.params)

    def _param_value(self, name):
        return self.ts.param_value(self.group_name + '.' + GROUP_NAME + '.' + name)
        
