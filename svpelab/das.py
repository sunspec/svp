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

import dataset

'''
The DAS module supports collecting time series data records in a dataset. Each time series data record is comprised
of a reading for each data point in the dataset. The Dataset object organizes the data point values as a list of values
for each data point. The data point lists are contained in a list. The DAS module supports both RMS and waveform
datasets and DAS device devices may support either RMS data, waveform data, or both.

The DAS module supports the reading of a single data record as a point in time. The data record read can either be
the last data record placed in the current active dataset or a new data record read directly from the DAS device.
Data records read directly can be returned as a list of data point values or in the expanded form of a dictionary where
the keys are the data point names and values are the data point values.

    das_init() - Create das instance.

    data_capture() - Enable/disable RMS data capture
    data_capture_read() - Return the last data sample from the data capture in expanded format.
    data_capture_dataset() - Return dataset (Dataset) created from last data capture.
    device_data_read() - Read the current data values directly from the DAS. It does not create a new data sample in
                         the data capture, if active.
    data_read() - Read the current data values directly from the DAS and return as expanded data record. It does
                      not create a new data sample in the data capture, if active.
    data_sample() - Read the current data values directly from the DAS and place in the current dataset.

    waveform_capture() - Enable/disable waveform capture.
    waveform_status() - Get waveform capture status.
    waveform_force_trigger() - Create trigger event
    waveform_capture_dataset() - Return dataset (Dataset) created from last waveform capture.

The DAS module supports adding additional data points to those provided by the data acquisition device. The additional
data points are termed 'soft channel' and the values are maintained by updated the points in the dictionary.
Soft channel data points are indicated using the 'sc_points' argument in data_init(). The 'sc_points' argument is a
list of soft channel point names that are active. The value of a soft channel point name is update with the 'sc'
dictionary of the DAS object. The soft channel points are added to each dataset record during data collection.

    sc_points = ['SC_1', 'SC_2']

    daq = das.das_init(ts, sc_points = sc_points)

    daq.sc['SC_1'] = ''
    daq.sc['SC_2'] = 2
'''

WFM_STATUS_INACTIVE = 'active'
WFM_STATUS_ACTIVE = 'inactive'
WFM_STATUS_COMPLETE = 'complete'

points_default = {
    'AC': ('VRMS', 'IRMS', 'P', 'S', 'Q', 'PF', 'FREQ'),
    'DC': ('V', 'I', 'P')
}

sc_points_default = ('SC_TRIG',)

MINIMUM_SAMPLE_PERIOD = 50

das_modules = {}

def params(info, id=None, label='Data Acquisition System', group_name=None, active=None, active_value=None):
    if group_name is None:
        group_name = DAS_DEFAULT_ID
    else:
        group_name += '.' + DAS_DEFAULT_ID
    if id is not None:
        group_name = group_name + '_' + str(id)
    name = lambda name: group_name + '.' + name
    info.param_group(group_name, label='%s Parameters' % label, active=active, active_value=active_value, glob=True)
    info.param(name('mode'), label='Mode', default='Disabled', values=['Disabled'])
    for mode, m in das_modules.iteritems():
        m.params(info, group_name=group_name)

DAS_DEFAULT_ID = 'das'

def das_init(ts, id=None, points=None, sc_points=None, group_name=None):
    """
    Function to create specific das implementation instances.
    """
    if group_name is None:
        group_name = DAS_DEFAULT_ID
    else:
        group_name += '.' + DAS_DEFAULT_ID
    if id is not None:
        group_name = group_name + '_' + str(id)
    mode = ts.param_value(group_name + '.' + 'mode')
    sim = None
    if mode != 'Disabled':
        sim_module = das_modules.get(mode)
        if sim_module is not None:
            sim = sim_module.DAS(ts, group_name, points=points, sc_points=sc_points)
        else:
            raise DASError('Unknown data acquisition system mode: %s' % mode)

    return sim


class DASError(Exception):
    """
    Exception to wrap all das generated exceptions.
    """
    pass


class DAS(object):
    """
    Template for grid simulator implementations. This class can be used as a base class or
    independent grid simulator classes can be created containing the methods contained in this class.
    """

    def __init__(self, ts, group_name, points=None, sc_points=None):
        self.ts = ts
        self.group_name = group_name
        self.points = points
        self.data_points = None
        self.sc_data_points = sc_points
        self.params = {}
        self.device = None
        self.sample_interval = 1000
        self.sc = {}
        self._capture = False
        self._timer = None
        self._ds = None
        self._last_datarec = []

        if self.points is None:
            self.points = dict(points_default)

        # determine SVP Files directory path
        script_path = os.path.realpath(__file__)
        result_dir = self.ts._results_dir
        for i in range(len(script_path)):
            if script_path[i] != result_dir[i]:
                break
        self.files_dir = os.path.join(script_path[:i], 'Files')

    def _init_sc_points(self):
        if self.sc_data_points is None:
            self.sc_data_points = sc_points_default

        if len(self.sc_data_points) > 0:
            for p in self.sc_data_points:
                self.data_points.append(p)
                self.sc[p] = 0

        self._ds = dataset.Dataset(self.data_points, ts=self.ts)

    def _data_expand(self, data):
        if len(self.data_points) != len(data):
            raise DASError('Data/data point mismatch: %s %s' % (self.data_points, data))
        return dict(zip(self.data_points, data))

    def _timer_timeout(self, arg=None):
        self.data_sample()

    def info(self):
        """
        Return information string for the DAS device.
        """
        if self.device is None:
            raise DASError('DAS device not initialized')
        return self.device.info()

    def open(self):
        """
        Open communications resources associated with the DAS device.
        """
        if self.device is None:
            raise DASError('DAS device not initialized')
        self.device.open()

    def close(self):
        """
        Close any open communications resources associated with the DAS device.
        """
        if self.device is None:
            raise DASError('DAS device not initialized')
        self.device.close()

    def data_capture(self, enable=True, channels=None):
        """
        Enable/disable data capture.

        If sample_interval == 0, there will be no autonomous data captures and self.data_sample should be used to add
        data points to the capture
        """
        if self.device is not None:
            self.sample_interval = self.device.sample_interval
        if enable is True:
            if self._capture is False:
                self._ds = dataset.Dataset(self.data_points, ts=self.ts)
                self._last_datarec = []
                if self.sample_interval > 0:
                    if self.sample_interval < MINIMUM_SAMPLE_PERIOD:
                        raise DASError('Sample period too small: %s' % (self.sample_interval))
                    self._timer = self.ts.timer_start(float(self.sample_interval)/1000, self._timer_timeout,
                                                      repeating=True)
                self._capture = True
        elif enable is False:
            if self._capture is True:
                if self._timer is not None:
                    self.ts.timer_cancel(self._timer)
                self._timer = None
                self._capture = False
        self.device.data_capture(enable)

    def data_capture_read(self):
        """
        Return the last data sample from the data capture in expanded format.
        """
        rec = []
        if len(self._last_datarec) > 0:
            rec = self._data_expand(self._last_datarec)
        else:
            rec = self.data_read()
        return rec

    def data_capture_dataset(self):
        """
        Return dataset (Dataset) created from last data capture.
        """
        return self._ds

    def device_data_read(self):
        """
        Read the current data values directly from the DAS. It does not create a new data sample in the
        data capture, if active.
        """
        data = self.device.data_read()
        # add soft channel points
        for p in self.sc_data_points:
            data.append(self.sc[p])

        return data

    def data_read(self):
        """
        Read the current data values directly from the DAS. It does not create a new data sample in the
        data capture, if active.
        """
        return self._data_expand(self.device_data_read())

    def data_sample(self):
        """
        Read the current data values directly from the DAS and place in the current dataset.
        """
        if self._capture is True:
            self._last_datarec = self.device_data_read()
            self._ds.append(self._last_datarec)
        return self._last_datarec

    def waveform_config(self, params):
        """
        Configure waveform capture.

        params: Dictionary with following entries:
            'sample_rate' - Sample rate (samples/sec)
            'pre_trigger' - Pre-trigger time (sec)
            'post_trigger' - Post-trigger time (sec)
            'trigger_level' - Trigger level
            'trigger_cond' - Trigger condition - ['Rising_Edge', 'Falling_Edge']
            'trigger_channel' - Trigger channel - ['AC_V_1', 'AC_V_2', 'AC_V_3', 'AC_I_1', 'AC_I_2', 'AC_I_3', 'EXT']
            'timeout' - Timeout (sec)
            'channels' - Channels to capture - ['AC_V_1', 'AC_V_2', 'AC_V_3', 'AC_I_1', 'AC_I_2', 'AC_I_3', 'EXT']
        """
        return self.device.waveform_config(params=params)

    def waveform_capture(self, enable=True, sleep=None):
        """
        Enable/disable data capture.
        """
        if sleep is None:
            sleep = self.ts.sleep
        return self.device.waveform_capture(enable=enable, sleep=sleep)

    def waveform_status(self):
        """
        Get waveform capture status.
        """
        return self.device.waveform_status()

    def waveform_force_trigger(self):
        """
        Create trigger event
        """
        return self.device.waveform_force_trigger()

    def waveform_capture_dataset(self):
        """
        Return dataset (Dataset) created from last waveform capture.
        """
        return self.device.waveform_capture_dataset()

def das_scan():
    global das_modules
    # scan all files in current directory that match das_*.py
    package_name = '.'.join(__name__.split('.')[:-1])
    files = glob.glob(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'das_*.py'))
    for f in files:
        module_name = None
        try:
            module_name = os.path.splitext(os.path.basename(f))[0]
            if package_name:
                module_name = package_name + '.' + module_name
            m = importlib.import_module(module_name)
            if hasattr(m, 'das_info'):
                info = m.das_info()
                mode = info.get('mode')
                # place module in module dict
                if mode is not None:
                    das_modules[mode] = m
            else:
                if module_name is not None and module_name in sys.modules:
                    del sys.modules[module_name]
        except Exception, e:
            if module_name is not None and module_name in sys.modules:
                del sys.modules[module_name]
            raise DASError('Error scanning module %s: %s' % (module_name, str(e)))

# scan for das modules on import
das_scan()

if __name__ == "__main__":
    pass
