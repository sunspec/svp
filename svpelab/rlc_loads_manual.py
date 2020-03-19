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

from . import rlc_loads

manual_info = {
    'name': os.path.splitext(os.path.basename(__file__))[0],
    'mode': 'Manual'
}

def rlc_loads_info():
    return manual_info

def params(info, group_name):
    gname = lambda name: group_name + '.' + name
    pname = lambda name: group_name + '.' + GROUP_NAME + '.' + name
    mode = manual_info['mode']
    info.param_add_value(gname('mode'), mode)

GROUP_NAME = 'manual'


class RLC(rlc_loads.RLC):
    """
    Template for RLC load implementations. This class can be used as a base class or
    independent RLC load classes can be created containing the methods contained in this class.
    """

    def __init__(self, ts, group_name):
        rlc_loads.RLC.__init__(self, ts, group_name=None)


    def resistance(self, r=None):
        if r is not None:
            self.ts.confirm('Adjust the resistive load to R = %0.3f Ohms.' % r)
        else:
            self.ts.log('Enter the resistive load in Ohms.')

    def inductance(self, i=None):
        if i is not None:
            self.ts.confirm('Adjust the inductive load to L = %0.6f H.' % i)
        else:
            self.ts.log('Enter the inductive load in H.')

    def capacitance(self, c=None):
        if c is not None:
            self.ts.confirm('Adjust the capacitive load to C = %0.6f F.' % c)
        else:
            self.ts.log('Enter the capacitive load in F.')

    def capacitor_q(self, q=None):
        if q is not None:
            self.ts.confirm('Adjust the capacitive load of the fundamental freq to %0.3f VAr.' % q)
        else:
            self.ts.log('Enter the capacitor reactive power in VAr.')

    def inductor_q(self, q=None):
        if q is not None:
            self.ts.confirm('Adjust the inductive load of the fundamental freq to %0.3f VAr.' % q)
        else:
            self.ts.log('Enter the inductor reactive power in VAr.')

    def resistance_p(self, p=None):
        if p is not None:
            self.ts.confirm('Adjust the resistive load of the fundamental freq to %0.3f W.' % p)
        else:
            self.ts.log('Enter the resistor power in W.')

    def tune_current(self, i=None):
        if c is not None:
            self.ts.confirm('Adjust R, L, and C until the fundamental frequency current through switch S3 is '
                            'less than %0.2f' % i)
        else:
            pass

    def switch_s3(self, switch_state=None):
        if switch_state is not None:
            if switch_state == rlc_loads.S3_CLOSED:
                self.ts.confirm('Close S3 switch (switch to the utility). '
                                'Verify that the EUT output current is zero before closing.')
            elif switch_state == rlc_loads.S3_OPEN:
                self.ts.confirm('Open S3 switch (switch to the utility).')
            else:
                self.ts.log_warning('Unknown S3 switch state.')
        else:
            self.ts.log_warning('No switch state given for the RLC Load S3 switch.')

