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

der_modules = {}

def params(info, id=None, label='DER', group_name=None, active=None, active_value=None):
    if group_name is None:
        group_name = DER_DEFAULT_ID
    else:
        group_name += '.' + DER_DEFAULT_ID
    if id is not None:
        group_name = group_name + '_' + str(id)
    name = lambda name: group_name + '.' + name
    info.param_group(group_name, label='%s Parameters' % label,  active=active, active_value=active_value, glob=True)
    info.param(name('mode'), label='%s Mode' % label, default='Disabled', values=['Disabled'])
    for mode, m in der_modules.items():
        m.params(info, group_name=group_name)

DER_DEFAULT_ID = 'der'


def der_init(ts, id=None, group_name=None):
    """
    Function to create specific der implementation instances.
    """
    if group_name is None:
        group_name = DER_DEFAULT_ID
    else:
        group_name += '.' + DER_DEFAULT_ID
    if id is not None:
        group_name = group_name + '_' + str(id)
    print('run group_name = %s' % group_name)
    mode = ts.param_value(group_name + '.' + 'mode')
    sim = None
    if mode != 'Disabled':
        sim_module = der_modules.get(mode)
        if sim_module is not None:
            sim = sim_module.DER(ts, group_name)
        else:
            raise DERError('Unknown DER system mode: %s' % mode)

    return sim


class DERError(Exception):
    """
    Exception to wrap all der generated exceptions.
    """
    pass


class DER(object):
    """
    Template for grid simulator implementations. This class can be used as a base class or
    independent grid simulator classes can be created containing the methods contained in this class.
    """

    def __init__(self, ts, group_name):
        self.ts = ts
        self.group_name = group_name

        '''
        self.connect_settings = {'enable': False,
                                 'conn': True,
                                 'win_tms': 0,
                                 'rvrt_tms': 0}

        self.fixed_pf_params = {'enable': False,
                                'pf': 1.0,
                                'win_tms': 0,
                                'rmp_tms': 0,
                                'rvrt_tms': 0}

        self.max_power_params = {'enable': False,
                                 'wmax_pct': 100,
                                 'win_tms': 0,
                                 'rmp_tms': 0,
                                 'rvrt_tms': 0}

        self.volt_var_params = {'enable': False,
                                'active_curve': 0,
                                'max_curves': 1,
                                'max_points'}
        '''

    def config(self):
        """ Perform any configuration for the simulation based on the previously provided parameters. """
        pass

    def open(self):
        """ Open the communications resources associated with the grid simulator. """
        pass

    def close(self):
        """ Close any open communications resources associated with the grid simulator. """
        pass

    """
        WRtg
        VARtg
        VArRtgQ1
        VArRtgQ2
        VArRtgQ3
        VArRtgQ4
        ARtg
        PFRtgQ1
        PFRtgQ2
        PFRtgQ3
        PFRtgQ4
        WHRtg
        AhrRtg
        MaxChaRte
        MaxDisChaRte
    """
    def nameplate(self):
        pass

    """
        A - Current
        AphA
        AphB
        AphC
        PPVphAB
        PPVphBC
        PPVphCA
        PhVphA
        PhVphB
        PhVphC
        W
        Hz
        VA
        VAr
        PF
        WH
        DCA
        DCV
        DCW
        TmpCab
        TmpSnk
        TmpTrns
        TmpOt
        St
        StVnd
        Evt1
        Evt2
        EvtVnd1
        EvtVnd2
        EvtVnd3
        EvtVnd4
    """
    def measurements(self):
        """ Get measurement data.

        Params:

        :return: Dictionary of measurement data.
        """
        pass

    """
        WMax
        VRef
        VRefOfs
        VMax
        VMin
        VAMax
        VArMaxQ1
        VArMaxQ2
        VArMaxQ3
        VArMaxQ4
        WGra
        PFMinQ1
        PFMinQ2
        PFMinQ3
        PFMinQ4
        VArAct
    """
    def settings(self, params=None):
        pass

    def conn_status(self, params=None):
        """ Get status of controls (binary True if active).
        :return: Dictionary of active controls.
        """
        pass

    def controls_status(self, params=None):
        """ Get status of controls (binary True if active).
            :return: Dictionary of active controls.

        """
        pass

    """
        'Conn': True/False
        'WinTms': 0
        'RvrtTms': 0
    """
    def connect(self, params=None):
        """ Get/set connect/disconnect function settings.

        :param params: Dictionary of parameters. Following keys are supported: enable, conn, win_tms, rvrt_tms.
        :return: Dictionary of active settings for fixed factor.
        """

        if params is None:
            # get current settings
            params = {}
        else:
            # apply params
            pass

        return params

    """
        'ModEna': True/False
        'PF': 1.0
        'WinTms': 0
        'RmpTms': 0
        'RvrtTms': 0
    """
    def fixed_pf(self, params=None):
        """ Get/set fixed power factor control settings.

        :param params: Dictionary of parameters. Following keys are supported: enable, pf, win_tms, rmp_tms, rvrt_tms.
        :return: Dictionary of active settings for fixed factor.
        """
        if params is None:
            params = self.fixed_pf_params
        else:
            self.fixed_pf_params = params
        return params

    """
        'ModEna': True/False
        'WMaxPct': 100
        'WinTms': 0
        'RmpTms': 0
        'RvrtTms': 0
    """
    def limit_max_power(self, params=None):

        if params is None:
            params = self.max_power_params
        else:
            self.max_power_params = params
        return params

    """
        'ModEna': True/False
        'ActCrv': 0
        'NCrv': 1
        'NPt': 4
        'ActPt': 4
        'RmpTmsCv': 0
        'RmpDecTmm': 0
        'RmpIncrTmm': 0
    """
    def volt_var(self, params=None):
        pass

    """
        'x': []       # %VRef
        'y': []       # units based on dep_ref
        'DepRef': 'var_max_pct', 'var_aval_pct', 'va_max_pct', 'w_max_pct'
        'WinTms': 0
        'RmpTms': 0
        'RvrtTms': 0
        'RmpTmsCv': 0
        'RmpDecTmm': 0
        'RmpIncrTmm': 0
    """
    def volt_var_curve(self, id, params=None):
        pass

    """ Example param dict
        'Ena': True
        'ActCrv': 1
        'NCrv': 2
        'NPt': 3
        'WinTms': 0
        'RmpTms': 0
        'RvrtTms': 0
    """
    def freq_watt(self, params=None):
        pass

    """ Example param dict
        'hz': [] - List of frequency curve points
        'w': [] - List of power curve points
        'CrvNam': 'VDE 4105' - Optional description for curve. (Max 16 chars)
        'RmpPT1Tms': 1 - The time of the PT1 in seconds (time to accomplish a change of 95%).
        'RmpDecTmm': 0 - Ramp decrement timer
        'RmpIncTmm': 0 - Ramp increment timer
        'RmpRsUp': 0 - The maximum rate at which the power may be increased after releasing the frozen value of
                  snap shot function.
        'SnptW': 0 - 1=enable snapshot/capture mode
        'WRef': 0 - Reference active power (default = WMax).
        'WRefStrHz': 0 - Frequency deviation from nominal frequency at the time of the snapshot to start constraining
                    power output.
        'WRefStopHz': 0 - Frequency deviation from nominal frequency at which to release the power output.
        'ReadOnly': 0 - 0 = READWRITE, 1 = READONLY
    """
    def freq_watt_curve(self, id, params=None):
        pass

    """ Example param dict
        'Ena': True - Enabled (True/False)
        'HysEna': 1 - Enable hysterisis (True/False)
        'WGra': 0.4 - The slope of the reduction in the maximum allowed watts output as a function of frequency.
        'HzStr': 0.2 - The frequency deviation from nominal frequency (ECPNomHz) at which a snapshot of the instantaneous
                power output is taken to act as the CAPPED power level (PM) and above which reduction in power
                output occurs.
        'HzStop': 1.4 - The frequency deviation from nominal frequency (ECPNomHz) at which curtailed power output may
                return to normal and the cap on the power level value is removed.
        'HzStopWGra' : 1/300 - The maximum time-based rate of change at which power output returns to normal after having
                     been capped by an over frequency event.
    """
    def freq_watt_param(self, params=None):
        pass

    def soft_start_ramp_rate(self, params=None):
        pass

    def ramp_rate(self, params=None):
        pass

    """ volt/watt control
        'ModEna': True/False
        'ActCrv': 0
        'NCrv': 1
        'NPt': 4
        'WinTms': 0
        'RvrtTms': 0
        'RmpTms': 0
        'curve': {
                 'ActPt': 3
                 'v': [95, 101, 105]
                 'w': [100, 100, 0]
                 'DeptRef': 1
                 'RmpPt1Tms': 0
                 'RmpDecTmm': 0
                 'RmpIncTmm': 0
                 }
    """
    def volt_watt(self, params=None):
        pass


    """
        'Q': 0       # %Qmax (positive is overexcited, negative is underexcited)
        'WinTms': 0
        'RmpTms': 0
        'RvrtTms': 0
    """
    def reactive_power(self, params=None):
        pass

    """
        'P': 0       # %Wmax (positive is exporting (discharging), negative is importing (charging) power)
        'WinTms': 0
        'RmpTms': 0
        'RvrtTms': 0
    """
    def active_power(self, params=None):
        pass

    """ Get/set storage parameters
        'WChaMax': 0 - Setpoint for maximum charge.
        'WChaGra': 0 - Setpoint for maximum charging rate. Default is MaxChaRte.
        'WDisChaGra': 0 - Setpoint for maximum discharge rate. Default is MaxDisChaRte.
        'StorCtl_Mod': 0 - Activate hold/discharge/charge storage control mode. Bitfield value.
        'VAChaMax': 0 - Setpoint for maximum charging VA.
        'MinRsvPct': 0 - Setpoint for minimum reserve for storage as a percentage of the nominal maximum storage.
        'ChaState' (Read only) - Currently available energy as a percent of the capacity rating.
        'StorAval' (Read only) - State of charge (ChaState) minus storage reserve (MinRsvPct) times capacity rating (AhrRtg).
        'InBatV' (Read only) - Internal battery voltage.
        'ChaSt' (Read only) - Charge status of storage device. Enumerated value.
        'OutWRte': 0 - Percent of max discharge rate.
        'InWRte': 0 - Percent of max charging rate.
        'InOutWRte_WinTms': 0 - Time window for charge/discharge rate change.
        'InOutWRte_RvrtTms': 0 - Timeout period for charge/discharge rate.
        'InOutWRte_RmpTms': 0 - Ramp time for moving from current setpoint to new setpoint.
    """
    def storage(self, params=None):
        pass

    def frt_stay_connected_high(self, params=None):
        pass

    def frt_stay_connected_low(self, params=None):
        pass

    def frt_trip_high(self, params=None):
        pass

    def frt_trip_low(self, params=None):
        pass

    def vrt_stay_connected_high(self, params=None):
        pass

    def vrt_stay_connected_low(self, params=None):
        pass

    def vrt_trip_high(self, params=None):
        pass

    def vrt_trip_low(self, params=None):
        pass

def der_scan():
    global der_modules
    # scan all files in current directory that match der_*.py
    package_name = '.'.join(__name__.split('.')[:-1])
    files = glob.glob(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'der_*.py'))
    for f in files:
        module_name = None
        try:
            module_name = os.path.splitext(os.path.basename(f))[0]
            if package_name:
                module_name = package_name + '.' + module_name
            m = importlib.import_module(module_name)
            if hasattr(m, 'der_info'):
                info = m.der_info()
                mode = info.get('mode')
                # place module in module dict
                if mode is not None:
                    der_modules[mode] = m
            else:
                if module_name is not None and module_name in sys.modules:
                    del sys.modules[module_name]
        except Exception as e:
            if module_name is not None and module_name in sys.modules:
                del sys.modules[module_name]
            raise DERError('Error scanning module %s: %s' % (module_name, str(e)))

# scan for der modules on import
der_scan()

if __name__ == "__main__":
    pass
