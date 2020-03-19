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

from . import pvsim

manual_info = {
    'name': os.path.splitext(os.path.basename(__file__))[0],
    'mode': 'Manual'
}

def pvsim_info():
    return manual_info

def params(info, group_name):
    gname = lambda name: group_name + '.' + name
    pname = lambda name: group_name + '.' + GROUP_NAME + '.' + name
    mode = manual_info['mode']
    info.param_add_value(gname('mode'), mode)
    info.param_group(gname(GROUP_NAME), label='%s Parameters' % mode,
                     active=gname('mode'),  active_value=mode, glob=True)

    info.param(pname('ipaddr'), label='IP Address', default='192.168.0.167')
    info.param(pname('curve_type'), label='IV Curve Type', default='EN50530',
               values=['EN50530', 'Name', 'Fill Factor', 'Vmp/Imp'])

    info.param(pname('overvoltage'), label='Overvoltage Protection Level (V)', default=660.0)

    info.param(pname('pmp'), label='EN50530 MPP Power (W)', default=3000.0,
               active=pname('curve_type'),  active_value='EN50530')
    info.param(pname('vmp'), label='EN50530 MPP Voltage (V)', default=460.0,
               active=pname('curve_type'),  active_value='EN50530')

    info.param(pname('filename'), label='IV Curve Name', default='BP Solar - BP 3230T (60 cells)',
               active=pname('curve_type'),  active_value='Name')

    info.param(pname('voc'), label='Voc (V)', default=65.0,
               active=pname('curve_type'),  active_value=['Vmp/Imp', 'Fill Factor'])
    info.param(pname('isc'), label='Isc (A)', default=2.5,
               active=pname('curve_type'),  active_value=['Vmp/Imp', 'Fill Factor'])

    # can choose between Vmp/Imp or Fill Factor
    info.param(pname('vmp2'), label='MPP Voltage (V)', default=50.0,
               active=pname('curve_type'),  active_value='Vmp/Imp')
    info.param(pname('imp'), label='MPP Current (A)', default=2.3,
               active=pname('curve_type'),  active_value='Vmp/Imp')

    info.param(pname('form_factor'), label='Form Factor (Fill Factor)', default=0.71,
               active=pname('curve_type'),  active_value=['Fill Factor'])

    info.param(pname('beta_v'), label='Beta V (%/K)', default=-0.36,
               active=pname('curve_type'),  active_value=['Vmp/Imp', 'Fill Factor'])
    info.param(pname('beta_p'), label='Beta P (%/K)', default=-0.5,
               active=pname('curve_type'),  active_value=['Vmp/Imp', 'Fill Factor'])
    info.param(pname('kfactor_voltage'), label='K Factor V1 (V)', default=60.457,
               active=pname('curve_type'),  active_value=['Vmp/Imp', 'Fill Factor'])
    info.param(pname('kfactor_irradiance'), label='K Factor E1 (W/m^2)', default=200,
               active=pname('curve_type'),  active_value=['Vmp/Imp', 'Fill Factor'])

    info.param(pname('channel'), label='TerraSAS channel(s)', default='1',
               desc='Channels are a string: 1 or  1,2,4,5')

GROUP_NAME = 'manual'


class PVSim(pvsim.PVSim):

    def __init__(self, ts, group_name):
        pvsim.PVSim.__init__(self, ts, group_name)

        self.ts = ts

        self.ipaddr = self._param_value('ipaddr')
        self.curve_type = self._param_value('curve_type')
        self.v_overvoltage = self._param_value('overvoltage')
        self.pmp = self._param_value('pmp')
        self.vmp = self._param_value('vmp')
        if self.vmp is None:
            self.vmp = self._param_value('vmp2')  # it can only be one of the vmp's
        self.imp = self._param_value('imp')
        self.filename = self._param_value('filename')
        self.voc = self._param_value('voc')
        self.isc = self._param_value('isc')
        self.form_factor = self._param_value('form_factor')
        self.beta_v = self._param_value('beta_v')
        self.beta_p = self._param_value('beta_p')
        self.kfactor_voltage = self._param_value('kfactor_voltage')
        self.kfactor_irradiance = self._param_value('kfactor_irradiance')

        self.channel = []
        self.irr_start = self._param_value('irr_start')
        chans = str(self._param_value('channel')).split(',')
        for c in chans:
            try:
                self.channel.append(int(c))
            except ValueError:
                raise pvsim.PVSimError('Invalid channel number: %s' % c)

        self.profile_name = None
 

    def _param_value(self, name):
        return self.ts.param_value(self.group_name + '.' + GROUP_NAME + '.' + name)
    
    def irradiance_set(self, irradiance=1000):
        if self.ts.confirm('Please change the irradiance to %0.1f W/m^2.' % irradiance) is False:
            raise pvsim.PVSimError('Aborted PV simulation')

    def power_set(self, power):
        if self.ts.confirm('Please change the power to %0.1f%% power.' % power) is False:
            raise pvsim.PVSimError('Aborted PV simulation')

    def power_on(self):
        if self.ts.confirm('Please turn on PV simulator to give EUT DC power.') is False:
            raise pvsim.PVSimError('Aborted PV simulation')

    def profile_start(self):
        if self.ts.confirm('Please run the PV simulator profile.') is False:
            raise pvsim.PVSimError('Aborted PV simulation')

if __name__ == "__main__":
    pass

