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
import datetime

class DatasetError(Exception):
    """
    Exception to wrap all das generated exceptions.
    """
    pass

"""
    Data AC/DC point names have three parts:

    - category (AC/DC)
    - type (V, I, VRMS, IRMS, P, Q, S, PF, FREQ)
    - id (optional)

    Example names:
    AC_V
    AC_I

    AC_V_1
    AC_I_1
    AC_VRMS_1

    DC_V
    DC_I

    A dataset consists of a set of time series points organized as parallel arrays and some
    additional optional properties.

    Optional roperties:
    Start time of dataset
    Sample rate of dataset (samples/sec)
    Trigger sample (record index into dataset)

"""
class Dataset(object):
    def __init__(self, points=None, data=None, start_time=None, sample_rate=None, trigger_sample=None, params=None,
                 ts=None):
        self.start_time = start_time              # start time
        self.sample_rate = sample_rate            # samples/second
        self.trigger_sample = trigger_sample      # trigger sample
        self.points = points                      # point names
        self.data = data                          # data
        self.ts = ts

        if points is None:
            self.points = []
        if data is None:
            self.clear()

    def point_data(self, point):
        try:
            idx = self.points.index(point)
        except ValueError:
            raise DatasetError('Data point not in dataset: %s' % point)
        return self.data[idx]

    def append(self, data):
        dlen = len(data)
        if len(data) != len(self.data):
            raise DatasetError('Append record point mismatch, dataset contains %s points,'
                               ' appended data contains %s points' % (len(self.data), dlen))
        for i in range(dlen):
            try:
                if data[i] is not None:
                    if data[i] is tuple:
                        self.ts.log_debug('tuple data point recorded: %s' % data)
                        v = float(data[i][0])
                    elif isinstance(data[i], datetime.datetime):
                        epoch = datetime.datetime.utcfromtimestamp(0)
                        total_seconds = (data[i] - epoch).total_seconds()
                        # total_seconds will be in decimals (millisecond precision)
                        v = total_seconds
                    else:
                        v = float(data[i])
                else:
                    v = 'None'
            except ValueError:
                v = data[i]
            self.data[i].append(v)

    def extend(self, data):
        dlen = len(data)
        if len(data) != len(self.data):
            raise DatasetError('Extend record point mismatch, dataset contains %s points,'
                               ' appended data contains %s points' % (len(self.data), dlen))
        for i in range(dlen):
            self.data[i].extend(data[i])

    def clear(self):
        self.data = []
        for i in range(len(self.points)):
            self.data.append([])

    def to_csv(self, filename):
        cols = list(range(len(self.data)))
        if len(cols) > 0:
            f = open(filename, 'w')
            f.write('%s\n' % ', '.join(map(str, self.points)))
            for i in range(len(self.data[0])):
                d = []
                for j in cols:
                    # self.ts.log_debug('data = %s' % self.data)
                    # self.ts.log_debug('point names = %s' % self.points)
                    # self.ts.log_debug('len(points) = %s, len(data) = %s' % (len(self.points), len(self.data)))
                    # self.ts.log_debug('j = %s, i = %i, self.data[j][i] = %s' % (j, i, self.data[j][i]))
                    d.append(self.data[j][i])
                f.write('%s\n' % ', '.join(map(str, d)))
            f.close()

    def from_csv(self, filename, sep=','):
        self.clear()
        f = open(filename, 'r')
        ids = None
        while ids is None:
            line = f.readline().strip()
            if len(line) > 0 and line[0] != '#':
                ids = [e.strip() for e in line.split(sep)]
        self.points = ids
        for i in range(len(self.points)):
            self.data.append([])
        for line in f:
            data = [float(e.strip()) for e in line.split(sep)]
            if len(data) > 0:
                self.append(data)
        f.close()


if __name__ == "__main__":

    rms_points = ['TIME',
                  'AC_VRMS_1', 'AC_IRMS_1', 'AC_P_1', 'AC_S_1', 'AC_Q_1', 'AC_PF_1', 'AC_FREQ_1',
                  'AC_VRMS_2', 'AC_IRMS_2', 'AC_P_2', 'AC_S_2', 'AC_Q_2', 'AC_PF_2', 'AC_FREQ_2',
                  'AC_VRMS_3', 'AC_IRMS_3', 'AC_P_3', 'AC_S_3', 'AC_Q_3', 'AC_PF_3', 'AC_FREQ_3',
                  'DC_V', 'DC_I', 'DC_P']

    rms_data = [[0.0,
                 220.1, 10.1, 2100.1, 2200, 0.011, 0.991, 60.1,
                 220.2, 10.2, 2100.2, 2200, 0.012, 0.992, 60.2,
                 220.3, 10.3, 2100.3, 2200, 0.013, 0.993, 60.3,
                 440, 5, 2200],
                [1.0,
                 220.1, 10.1, 2100.1, 2200, 0.011, 0.991, 60.1,
                 220.2, 10.2, 2100.2, 2200, 0.012, 0.992, 60.2,
                 220.3, 10.3, 2100.3, 2200, 0.013, 0.993, 60.3,
                 440, 5, 2200],
                [2.0,
                 220.1, 10.1, 2100.1, 2200, 0.011, 0.991, 60.1,
                 220.2, 10.2, 2100.2, 2200, 0.012, 0.992, 60.2,
                 220.3, 10.3, 2100.3, 2200, 0.013, 0.993, 60.3,
                440, 5, 2200]]

    ds = Dataset(points=rms_points)
    for i in range(len(rms_data)):
        ds.append(rms_data[i])
    ds.to_csv('xyz')
