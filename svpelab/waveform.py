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

import math

class WaveformError(Exception):
    """
    Exception to wrap all waveform generated exceptions.
    """
    pass


class Waveform(object):

    def __init__(self, ts=None):
        self.start_time = 0          # waveform start time
        self.sample_count = 0        # size of waveform/per channel
        self.sample_rate = 0         # samples/second
        self.trigger_sample = 0      # trigger sample
        self.channels = []           # channel names
        self.channel_data = []       # waveform curves
        self.rms_data = {}           # rms data calculated from waveform data
        self.ts = ts

    def from_csv(self, filename, sep=','):
        f = open(filename, 'r')
        ids = f.readline().split(sep)
        chans = []
        chan_count = len(ids)
        for i in range(chan_count):
            self.channels.append(ids[i].strip())
            chans.append([])
        # print self.channels
        line = 1
        for data in f:
            line += 1
            values = data.split(sep)
            if len(values) != chan_count:
                raise WaveformError('Channel data error: line %s' % (line))
            for i in range(chan_count):
                chans[i].append(float(values[i]))

        for i in range(chan_count):
            self.channel_data.append(chans[i])

    def from_dataset(self, ds=None):
        if ds is not None:
            self.start_time = ds.start_time          # waveform start time
            self.sample_rate = ds.sample_rate         # samples/second
            self.channels = ds.points
            self.channel_data = ds.data

    def to_csv(self, filename):
        f = open(filename, 'w')
        chan_count = len(self.channels)
        f.write('%s\n' % ','.join(self.channels))
        for i in range(len(self.channel_data[0])):
            data = []
            for c in range(chan_count):
                data.append(self.channel_data[c][i])
            f.write('%s\n' % ','.join(str(v) for v in data))

    def compute_rms(self, data):
        tmp = 0
        size = len(data)
        for i in range(size):
            v = data[i]
            tmp += v * v
        tmp /= float(size)
        return math.sqrt(tmp)

    def compute_cycle_rms(self, chan_id):
        c = None
        try:
            c = 'Time'
            time_index = self.channels.index(c)
            c = chan_id
            chan_index = self.channels.index(c)
        except Exception:
            try:
                c = 'TIME'
                time_index = self.channels.index(c)
                c = chan_id
                chan_index = self.channels.index(c)
            except Exception:
                raise WaveformError('Channel not found: %s' % (c))

        time_chan = self.channel_data[time_index]
        data_chan = self.channel_data[chan_index]
        scanning = False
        calculating = False
        neg = False
        start_index = 0
        rms_time = []
        rms_data = []

        for i in range(len(data_chan)):
            pos = data_chan[i] >= 0
            if calculating:
                if not pos:
                    neg = True
                elif neg:
                    # calculate rms [start_index:i]
                    rms_time.append(time_chan[i])
                    rms = self.compute_rms(data_chan[start_index:i])
                    rms_data.append(rms)
                    start_index = i
                    neg = False
            elif scanning:
                if pos:
                    start_index = i
                    calculating = True
            else:
                if not pos:
                    scanning = True

        return rms_time, rms_data

    def compute_rms_data(self, phase):
        phase = str(phase)
        chan_v = 'AC_V_%s' % phase
        chan_i = 'AC_I_%s' % phase
        rms_time_v, rms_data_v = self.compute_cycle_rms(chan_v)
        rms_time_i, rms_data_i = self.compute_cycle_rms(chan_i)
        count = min(len(rms_time_v), len(rms_time_i))
        self.rms_data[phase] = [rms_time_v[:count], rms_data_v[:count], rms_data_i[:count]]

if __name__ == "__main__":

    wf = Waveform()
    wf.from_csv('c:\\users\\bob\\waveforms\\sandia\\capture_1.csv')
    '''
    rms_time, rms_data = wf.compute_cycle_rms('AC_V_1')
    print rms_time
    print rms_data
    '''
    wf.compute_rms_data(1)
    print(wf.rms_data)



