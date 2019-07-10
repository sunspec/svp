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
import time

query_points = {
    'AC_VRMS': 'UTRMS',
    'AC_IRMS': 'ITRMS',
    'AC_P': 'P',
    'AC_S': 'S',
    'AC_Q': 'Q',
    'AC_PF': 'PF',
    'AC_FREQ': 'FCYC',
    'DC_V': 'UDC',
    'DC_I': 'IDC',
    'DC_P': 'P'
}


class DeviceError(Exception):
    """
    Exception to wrap all das generated exceptions.
    """
    pass
class Device(object):

    def __init__(self, params=None):

        self.params = params
        self.sample_interval = params.get('sample_interval')
        self.channels = params.get('channels')
        self.data_points = ['TIME']
        self.rm = None
        # Connection object
        self.conn = None

        self.query_chan_str = ""
        item = 0

        for i in range(1, 4):
            chan = self.channels[i]
            if chan is not None:
                chan_type = chan.get('type')
                points = chan.get('points')
                if points is not None:
                    chan_label = chan.get('label')
                    if chan_type is None:
                        raise DeviceError('No channel type specified')
                    if points is None:
                        raise DeviceError('No points specified')
                    for p in points:
                        item += 1
                        point_str = '%s_%s' % (chan_type, p)
                        chan_str = query_points.get(point_str)
                        self.query_chan_str += '%s%d?; ' % (chan_str, i)
                        if chan_label:
                            point_str = '%s_%s' % (point_str, chan_label)
                        self.data_points.append(point_str)


                        # Config the rms values

    def info(self):
        return 'DAS Manual - 1.0'

    def open(self):
        pass

    def close(self):
        pass

    def data_capture(self, enable=True):
        pass

    def data_read(self):

        data = []
        points = self.query_chan_str.split(";")[:-1]
        for point in points:
            if 'U' in point:
                data.append(123)
            elif 'I' in point:
                data.append(12)
            elif 'PF' in point:
                data.append(0.12)
            elif 'FCYC' in point:
                data.append(67)
            elif 'P' in point and 'PF' not in point:
                data.append(12345)
            elif 'Q' in point:
                data.append(11111)
            elif 'S' in point and 'RMS' not in point:
                data.append(16609)
            else:
                data.append(9991)
        data.insert(0, time.clock())
        return data
