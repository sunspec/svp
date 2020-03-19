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

from . import der

manual_info = {
    'name': os.path.splitext(os.path.basename(__file__))[0],
    'mode': 'Manual'
}

def der_info():
    return manual_info

def params(info, group_name):
    gname = lambda name: group_name + '.' + name
    pname = lambda name: group_name + '.' + GROUP_NAME + '.' + name
    mode = manual_info['mode']
    info.param_add_value(gname('mode'), mode)
    info.param_group(gname(GROUP_NAME), label='%s Parameters' % mode, active=gname('mode'), active_value=mode,
                     glob=True)
    info.param(pname('ipaddr'), label='IP Address', default='1.2.3.4')
    info.param(pname('ipport'), label='IP Port', default=999)
    info.param(pname('slave_id'), label='Slave Id', default=1)

    '''
    info.param_group(gname(GROUP_NAME), label='%s Parameters' % mode,
                     active=gname('mode'),  active_value=mode, glob=True)
    '''

GROUP_NAME = 'manual'

class DER(der.DER):

    def __init__(self, ts, group_name):
        der.DER.__init__(self, ts, group_name)
        
    def param_value(self, name):
        return self.ts.param_value(self.group_name + '.' + GROUP_NAME + '.' + name)

    def info(self):
        """ Get DER device information.

        Params:
            Manufacturer
            Model
            Version
            Options
            SerialNumber

        :return: Dictionary of information elements.
        """
        try:
            params = {}
            params['Manufacturer'] = 'MANUAL'
            params['Model'] = 'MANUAL'
            params['Options'] = 'MANUAL'
            params['Version'] = 'MANUAL'
            params['SerialNumber'] = 'MANUAL'
        except Exception as e:
            raise der.DERError(str(e))

        return params

    def nameplate(self):
        """ Get nameplate ratings.

        Params:
            WRtg - Active power maximum rating
            VARtg - Apparent power maximum rating
            VArRtgQ1, VArRtgQ2, VArRtgQ3, VArRtgQ4 - VAr maximum rating for each quadrant
            ARtg - Current maximum rating
            PFRtgQ1, PFRtgQ2, PFRtgQ3, PFRtgQ4 - Power factor rating for each quadrant
            WHRtg - Energy maximum rating
            AhrRtg - Amp-hour maximum rating
            MaxChaRte - Charge rate maximum rating
            MaxDisChaRte - Discharge rate maximum rating

        :return: Dictionary of nameplate ratings.
        """

        try:
            params = {}
            params['WRtg'] = self.ts.prompt('Enter WRtg: ')
            params['VARtg'] = self.ts.prompt('Enter VARtg: ')
            params['VArRtgQ1'] = self.ts.prompt('Enter VArRtgQ1: ')
            params['VArRtgQ2'] = self.ts.prompt('Enter VArRtgQ2: ')
            params['VArRtgQ3'] = self.ts.prompt('Enter VArRtgQ3: ')
            params['VArRtgQ4'] = self.ts.prompt('Enter VArRtgQ4: ')
            params['ARtg'] = self.ts.prompt('Enter ARtg: ')
            params['PFRtgQ1'] = self.ts.prompt('Enter PFRtgQ1: ')
            params['PFRtgQ2'] = self.ts.prompt('Enter PFRtgQ2: ')
            params['PFRtgQ3'] = self.ts.prompt('Enter PFRtgQ3: ')
            params['PFRtgQ4'] = self.ts.prompt('Enter PFRtgQ4: ')
            params['WHRtg'] = self.ts.prompt('Enter WHRtg: ')
            params['AhrRtg'] = self.ts.prompt('Enter AhrRtg: ')
            params['MaxChaRte'] = self.ts.prompt('Enter MaxChaRte: ')
            params['MaxDisChaRte'] = self.ts.prompt('Enter MaxDisChaRte: ')
        except Exception as e:
            raise der.DERError(str(e))

        return params

    def measurements(self):
        """ Get measurement data.

        Params:

        :return: Dictionary of measurement data.
        """

        try:
            a = 123
            params = {}

            params['A'] = a
            params['AphA'] = a
            params['AphB'] = a
            params['AphC'] = a
            params['PPVphAB'] = a
            params['PPVphBC'] = a
            params['PPVphCA'] = a
            params['PhVphA'] = a
            params['PhVphB'] = a
            params['PhVphC'] = a
            params['W'] = a
            params['Hz'] = a
            params['VA'] = a
            params['VAr'] = a
            params['PF'] = a
            params['WH'] = a
            params['DCA'] = a
            params['DCV'] = a
            params['DCW'] = a
            params['TmpCab'] = a
            params['TmpSnk'] = a
            params['TmpTrns'] = a
            params['TmpOt'] = a
            params['St'] = a
            params['StVnd'] = a
            params['Evt1'] = a
            params['Evt2'] = a
            params['EvtVnd1'] = a
            params['EvtVnd2'] = a
            params['EvtVnd3'] = a
            params['EvtVnd4'] = a

        except Exception as e:
            raise der.DERError(str(e))

        return params

    def settings(self, params=None):
        """
        Get/set capability settings.

        Params:
            WMax - Active power maximum
            VRef - Reference voltage
            VRefOfs - Reference voltage offset
            VMax - Voltage maximum
            VMin - Voltage minimum
            VAMax - Apparent power maximum
            VArMaxQ1, VArMaxQ2, VArMaxQ3, VArMaxQ4 - VAr maximum for each quadrant
            WGra - Default active power ramp rate
            PFMinQ1, PFMinQ2, PFMinQ3, PFMinQ4
            VArAct

        :param params: Dictionary of parameters to be updated.
        :return: Dictionary of active settings for connect.
        """
        try:
            params = {}
            params['WMax'] = self.inv.settings['WMax']
            params['VRef'] = self.inv.settings.VRef
            params['VRefOfs'] = self.inv.settings.VRefOfs
            params['VMax'] = self.inv.settings.VMax
            params['VMin'] = self.inv.settings.VMin
            params['VAMax'] = self.inv.settings.VAMax
            params['VArMaxQ1'] = self.inv.settings.VArMaxQ1
            params['VArMaxQ2'] = self.inv.settings.VArMaxQ2
            params['VArMaxQ3'] = self.inv.settings.VArMaxQ3
            params['VArMaxQ4'] = self.inv.settings.VArMaxQ4
            params['WGra'] = self.inv.settings.WGra
            params['PFMinQ1'] = self.inv.settings.PFMinQ1
            params['PFMinQ2'] = self.inv.settings.PFMinQ2
            params['PFMinQ3'] = self.inv.settings.PFMinQ3
            params['PFMinQ4'] = self.inv.settings.PFMinQ4
            params['VArAct'] = self.inv.settings.VArAct
        except Exception as e:
            raise der.DERError(str(e))

        return params


    def conn_status(self, params=None):
        """ Get status of controls (binary True if active).
        :return: Dictionary of active controls.
        """
        if self.inv is None:
            raise der.DERError('DER not initialized')

        try:
            self.inv.status.read()
            pv_conn_bitfield = self.inv.status.PVConn
            stor_conn_bitfield = self.inv.status.StorConn
            ecp_conn_bitfield = self.inv.status.ECPConn

            params = {}
            if pv_conn_bitfield is not None:
                params['PV_Connected'] = (pv_conn_bitfield & PVCONN_CONNECTED) == PVCONN_CONNECTED
                params['PV_Available'] = (pv_conn_bitfield & PVCONN_AVAILABLE) == PVCONN_AVAILABLE
                params['PV_Operating'] = (pv_conn_bitfield & PVCONN_OPERATING) == PVCONN_OPERATING
                params['PV_Test'] = (pv_conn_bitfield & PVCONN_TEST) == PVCONN_TEST
            elif stor_conn_bitfield is not None:
                params['Storage_Connected'] = (stor_conn_bitfield & STORCONN_CONNECTED) == STORCONN_CONNECTED
                params['Storage_Available'] = (stor_conn_bitfield & STORCONN_AVAILABLE) == STORCONN_AVAILABLE
                params['Storage_Operating'] = (stor_conn_bitfield & STORCONN_OPERATING) == STORCONN_OPERATING
                params['Storage_Test'] = (stor_conn_bitfield & STORCONN_TEST) == STORCONN_TEST
            elif ecp_conn_bitfield is not None:
                params['EPC_Connected'] = (ecp_conn_bitfield & ECPCONN_CONNECTED) == ECPCONN_CONNECTED
            else:
                params = {}
        except Exception as e:
            raise der.DERError(str(e))

        return params


    def controls_status(self, params=None):
        """ Get status of controls (binary True if active).
        :return: Dictionary of active controls.
        """
        if self.inv is None:
            raise der.DERError('DER not initialized')

        try:
            self.inv.status.read()
            status_bitfield = self.inv.status.StActCtl
            params = {}
            if status_bitfield is not None:
                params['Fixed_W'] = (status_bitfield & STACTCTL_FIXED_W) == STACTCTL_FIXED_W
                params['Fixed_Var'] = (status_bitfield & STACTCTL_FIXED_VAR) == STACTCTL_FIXED_VAR
                params['Fixed_PF'] = (status_bitfield & STACTCTL_FIXED_PF) == STACTCTL_FIXED_PF
                params['Volt_Var'] = (status_bitfield & STACTCTL_VOLT_VAR) == STACTCTL_VOLT_VAR
                params['Freq_Watt_Param'] = (status_bitfield & STACTCTL_FREQ_WATT_PARAM) == STACTCTL_FREQ_WATT_PARAM
                params['Freq_Watt_Curve'] = (status_bitfield & STACTCTL_FREQ_WATT_CURVE) == STACTCTL_FREQ_WATT_CURVE
                params['Dyn_Reactive_Power'] = (status_bitfield & STACTCTL_DYN_REACTIVE_POWER) == STACTCTL_DYN_REACTIVE_POWER
                params['LVRT'] = (status_bitfield & STACTCTL_LVRT) == STACTCTL_LVRT
                params['HVRT'] = (status_bitfield & STACTCTL_HVRT) == STACTCTL_HVRT
                params['Watt_PF'] = (status_bitfield & STACTCTL_WATT_PF) == STACTCTL_WATT_PF
                params['Volt_Watt'] = (status_bitfield & STACTCTL_VOLT_WATT) == STACTCTL_VOLT_WATT
                params['Scheduled'] = (status_bitfield & STACTCTL_SCHEDULED) == STACTCTL_SCHEDULED
                params['LFRT'] = (status_bitfield & STACTCTL_LFRT) == STACTCTL_LFRT
                params['HFRT'] = (status_bitfield & STACTCTL_HFRT) == STACTCTL_HFRT
            else:
                params = {}
        except Exception as e:
            raise der.DERError(str(e))

        return params

    def connect(self, params=None):
        """ Get/set connect/disconnect function settings.

        Params:
            Conn - Connected (True/False)
            WinTms - Randomized start time delay in seconds
            RvrtTms - Reversion time in seconds

        :param params: Dictionary of parameters to be updated.
        :return: Dictionary of active settings for connect.
        """
        try:
            if params is not None:
                self.ts.confirm('Set the following parameters %s' % params)
            else:
                params = {}
                params['Conn'] = self.ts.prompt('What is the connect status: True/False')
                params['WinTms'] = self.ts.prompt('What is the Time Window?')
                params['RvrtTms'] = self.ts.prompt('What is the Revert Time?')
        except Exception as e:
            raise der.DERError(str(e))

        return params

    def fixed_pf(self, params=None):
        """ Get/set fixed power factor control settings.

        Params:
            Ena - Enabled (True/False)
            PF - Power Factor set point
            WinTms - Randomized start time delay in seconds
            RmpTms - Ramp time in seconds to updated output level
            RvrtTms - Reversion time in seconds

        :param params: Dictionary of parameters to be updated.
        :return: Dictionary of active settings for fixed factor.
        """
        try:
            if params is not None:
                enable = params.get('Ena')
                pf = params.get('PF')
                if pf is not None:
                    cmd = 'Set DER power factor to %s' % (str(pf))
                    if enable is not None and enable is True:
                        cmd += ' and enable fixed power factor mode'
                elif enable is not None:
                    if enable is True:
                        cmd = 'Enable DER fixed power factor mode'
                    else:
                        cmd = 'Disable DER fixed power factor mode'
                self.ts.confirm(cmd)
            else:
                params = {}

        except Exception as e:
            raise der.DERError(str(e))

        return params

    def limit_max_power(self, params=None):
        """ Get/set max active power control settings.

        Params:
            Ena - Enabled (True/False)
            WMaxPct - Active power maximum as percentage of WMax
            WinTms - Randomized start time delay in seconds
            RmpTms - Ramp time in seconds to updated output level
            RvrtTms - Reversion time in seconds

        :param params: Dictionary of parameters to be updated.
        :return: Dictionary of active settings for limit max power.
        """
        try:
            if params is not None:
                self.ts.confirm('Set the following parameters %s' % params)
            else:
                params = {}
                self.inv.controls.read()
                if self.inv.controls.WMaxLim_Ena == 0:
                    params['Ena'] = False
                else:
                    params['Ena'] = True
                params['WMaxPct'] = self.inv.controls.WMaxLimPct
                params['WinTms'] = self.inv.controls.WMaxLimPct_WinTms
                params['RmpTms'] = self.inv.controls.WMaxLimPct_RmpTms
                params['RvrtTms'] = self.inv.controls.WMaxLimPct_RvrtTms
        except Exception as e:
            raise der.DERError(str(e))

        return params

    def volt_var(self, params=None):
        """ Get/set volt/var control

        Params:
            Ena - Enabled (True/False)
            ActCrv - Active curve number (0 - no active curve)
            NCrv - Number of curves supported
            NPt - Number of points supported per curve
            WinTms - Randomized start time delay in seconds
            RmpTms - Ramp time in seconds to updated output level
            RvrtTms - Reversion time in seconds

        :param params: Dictionary of parameters to be updated.
        :return: Dictionary of active settings for volt/var control.
        """

        try:
            if params is not None:
                self.ts.confirm('Set the following parameters %s' % params)
            else:
                params = None

        except Exception as e:
            raise der.DERError(str(e))

        return params

    def volt_var_curve(self, id, params=None):
        """ Get/set volt/var curve
            v [] - List of voltage curve points
            var [] - List of var curve points based on DeptRef
            DeptRef - Dependent reference type: 'VAR_MAX_PCT', 'VAR_AVAL_PCT', 'VA_MAX_PCT', 'W_MAX_PCT'
            RmpTms - Ramp timer
            RmpDecTmm - Ramp decrement timer
            RmpIncTmm - Ramp increment timer

        :param params: Dictionary of parameters to be updated.
        :return: Dictionary of active settings for volt/var control.
        """
        try:
            if params is not None:
                self.ts.confirm('Set the following parameters %s' % params)
            else:
                params = None

        except Exception as e:
            raise der.DERError(str(e))

        return params


    def freq_watt(self, params=None):
        """ Get/set freq/watt control

        Params:
            Ena - Enabled (True/False)
            ActCrv - Active curve number (0 - no active curve)
            NCrv - Number of curves supported
            NPt - Number of points supported per curve
            WinTms - Randomized start time delay in seconds
            RmpTms - Ramp time in seconds to updated output level
            RvrtTms - Reversion time in seconds

        :param params: Dictionary of parameters to be updated.
        :return: Dictionary of active settings for freq/watt control.
        """

        try:
            if params is not None:
                self.ts.confirm('Set the following parameters %s' % params)
            else:
                params = {}
                self.inv.freq_watt.read()
                if self.inv.freq_watt.ModEna == 0:
                    params['Ena'] = False
                else:
                    params['Ena'] = True
                params['ActCrv'] = self.inv.freq_watt.ActCrv
                params['NCrv'] = self.inv.freq_watt.NCrv
                params['NPt'] = self.inv.freq_watt.NPt
                params['WinTms'] = self.inv.freq_watt.WinTms
                params['RmpTms'] = self.inv.freq_watt.RmpTms
                params['RvrtTms'] = self.inv.freq_watt.RvrtTms
                if self.inv.freq_watt.ActCrv != 0:
                    params['curve'] = self.freq_watt_curve(id=self.inv.freq_watt.ActCrv)
        except Exception as e:
            raise der.DERError(str(e))

        return params

    def freq_watt_curve(self, id, params=None):
        """ Get/set volt/var curve
            hz [] - List of frequency curve points
            w [] - List of power curve points
            CrvNam - Optional description for curve. (Max 16 chars)
            RmpPT1Tms - The time of the PT1 in seconds (time to accomplish a change of 95%).
            RmpDecTmm - Ramp decrement timer
            RmpIncTmm - Ramp increment timer
            RmpRsUp - The maximum rate at which the power may be increased after releasing the frozen value of
                      snap shot function.
            SnptW - 1=enable snapshot/capture mode
            WRef - Reference active power (default = WMax).
            WRefStrHz - Frequency deviation from nominal frequency at the time of the snapshot to start constraining
                        power output.
            WRefStopHz - Frequency deviation from nominal frequency at which to release the power output.
            ReadOnly - 0 = READWRITE, 1 = READONLY

        :param params: Dictionary of parameters to be updated.
        :return: Dictionary of active settings for freq/watt curve.
        """

        try:
            if params is not None:
                self.ts.confirm('Set the following parameters %s' % params)
            else:
                params = {}
                act_pt = curve.ActPt
                params['CrvNam'] = curve.CrvNam
                params['RmpPT1Tms'] = curve.RmpPT1Tms
                params['RmpDecTmm'] = curve.RmpDecTmm
                params['RmpIncTmm'] = curve.RmpIncTmm
                params['RmpRsUp'] = curve.RmpRsUp
                params['SnptW'] = curve.SnptW
                params['WRef'] = curve.WRef
                params['WRefStrHz'] = curve.WRefStrHz
                params['WRefStopHz'] = curve.WRefStopHz
                params['ReadOnly'] = curve.ReadOnly
                params['id'] = id  #also store the curve number
                hz = []
                w = []
                for i in range(1, act_pt + 1):  # SunSpec point index starts at 1
                    hz_point = 'Hz%d' % i
                    w_point = 'VAr%d' % i
                    hz.append(getattr(curve, hz_point))
                    w.append(getattr(curve, w_point))
                params['hz'] = hz
                params['w'] = w

        except Exception as e:
            raise der.DERError(str(e))

        return params

    def freq_watt_param(self, params=None):
        """ Get/set frequency-watt with parameters

        Params:
            Ena - Enabled (True/False)
            HysEna - Enable hysterisis (True/False)
            WGra - The slope of the reduction in the maximum allowed watts output as a function of frequency.
            HzStr - The frequency deviation from nominal frequency (ECPNomHz) at which a snapshot of the instantaneous
                    power output is taken to act as the CAPPED power level (PM) and above which reduction in power
                    output occurs.
            HzStop - The frequency deviation from nominal frequency (ECPNomHz) at which curtailed power output may
                    return to normal and the cap on the power level value is removed.
            HzStopWGra - The maximum time-based rate of change at which power output returns to normal after having
                         been capped by an over frequency event.

        :param params: Dictionary of parameters to be updated.
        :return: Dictionary of active settings for frequency-watt with parameters control.
        """

        try:
            if params is not None:
                self.ts.confirm('Set the following parameters %s' % params)
        except Exception as e:
            raise der.DERError(str(e))

        return params

    def frt_stay_connected_high(self, params=None):
        """ Get/set high frequency ride through (must stay connected curve)

        Params:
            Ena - Enabled (True/False)
            ActCrv - Active curve number (0 - no active curve)
            NCrv - Number of curves supported
            NPt - Number of points supported per curve
            WinTms - Randomized start time delay in seconds
            RmpTms - Ramp time in seconds to updated output level
            RvrtTms - Reversion time in seconds
            Tms# - Time point in the curve
            Hz# - Frequency point in the curve

        :param params: Dictionary of parameters to be updated.
        :return: Dictionary of active settings for HFRT control.
        """

        try:
            if params is not None:
                self.ts.confirm('Set the following parameters %s' % params)
            else:
                params = {}
                self.inv.hfrtc.read()
                if self.inv.hfrtc.ModEna == 0:
                    params['Ena'] = False
                else:
                    params['Ena'] = True
                params['ActCrv'] = self.inv.hfrtc.ActCrv
                params['NCrv'] = self.inv.hfrtc.NCrv
                params['NPt'] = self.inv.hfrtc.NPt
                params['WinTms'] = self.inv.hfrtc.WinTms
                params['RmpTms'] = self.inv.hfrtc.RmpTms
                params['RvrtTms'] = self.inv.hfrtc.RvrtTms

        except Exception as e:
            raise der.DERError(str(e))

        return params


    def frt_stay_connected_low(self, params=None):
        """ Get/set high frequency ride through (must stay connected curve)

        Params:
            Ena - Enabled (True/False)
            ActCrv - Active curve number (0 - no active curve)
            NCrv - Number of curves supported
            NPt - Number of points supported per curve
            WinTms - Randomized start time delay in seconds
            RmpTms - Ramp time in seconds to updated output level
            RvrtTms - Reversion time in seconds
            Tms# - Time point in the curve
            Hz# - Frequency point in the curve

        :param params: Dictionary of parameters to be updated.
        :return: Dictionary of active settings for HFRT control.
        """
        try:
            if params is not None:
                self.ts.confirm('Set the following parameters %s' % params)
            else:
                params = {}
                self.inv.lfrtc.read()
                if self.inv.lfrtc.ModEna == 0:
                    params['Ena'] = False
                else:
                    params['Ena'] = True
                params['ActCrv'] = self.inv.lfrtc.ActCrv
                params['NCrv'] = self.inv.lfrtc.NCrv
                params['NPt'] = self.inv.lfrtc.NPt
                params['WinTms'] = self.inv.lfrtc.WinTms
                params['RmpTms'] = self.inv.lfrtc.RmpTms
                params['RvrtTms'] = self.inv.lfrtc.RvrtTms

        except Exception as e:
            raise der.DERError(str(e))

        return params

    def reactive_power(self, params=None):
        """ Set the reactive power

        Params:
            Ena - Enabled (True/False)
            Q - Reactive power as %Qmax (positive is overexcited, negative is underexcited)
            WinTms - Randomized start time delay in seconds
            RmpTms - Ramp time in seconds to updated output level
            RvrtTms - Reversion time in seconds

        :param params: Dictionary of parameters to be updated.
        :return: Dictionary of active settings for Q control.
        """
        try:
            if params is not None:
                self.ts.confirm('Set the following parameters %s' % params)
            else:
                params = {}
                params['Q'] = 200
                '''
                params['Ena'] = self.ts.prompt('Reactive power is enabled (True/False)? ')
                params['Q'] = self.ts.prompt('Reactive power is: ')
                params['WinTms'] = self.ts.prompt('Time Window is: ')
                params['RmpTms'] = self.ts.prompt('Ramp Time is: ')
                params['RvrtTms'] = self.ts.prompt('Revert Time is: ')
                params['curve'] = self.ts.prompt('Curve parameters are: ')
                '''

        except Exception as e:
            raise der.DERError(str(e))

        return params

    def active_power(self, params=None):
        """ Get/set active power of EUT

        Params:
            Ena - Enabled (True/False)
            P - Active power in %Wmax (positive is exporting (discharging), negative is importing (charging) power)
            WinTms - Randomized start time delay in seconds
            RmpTms - Ramp time in seconds to updated output level
            RvrtTms - Reversion time in seconds

        :param params: Dictionary of parameters to be updated.
        :return: Dictionary of active settings for HFRT control.
        """
        try:
            if params is not None:
                self.ts.confirm('Set the following parameters %s' % params)
            else:
                params = {}
                params['P'] = 2000
                '''
                params['Ena'] = self.ts.prompt('Active power is enabled (True/False)? ')
                params['P'] = self.ts.prompt('Active power is: ')
                params['WinTms'] = self.ts.prompt('Time Window is: ')
                params['RmpTms'] = self.ts.prompt('Ramp Time is: ')
                params['RvrtTms'] = self.ts.prompt('Revert Time is: ')
                params['curve'] = self.ts.prompt('Curve parameters are: ')
                '''

        except Exception as e:
            raise der.DERError(str(e))

        return params


    def storage(self, params=None):
        """ Get/set storage parameters

        Params:
            WChaMax - Setpoint for maximum charge.
            WChaGra - Setpoint for maximum charging rate. Default is MaxChaRte.
            WDisChaGra - Setpoint for maximum discharge rate. Default is MaxDisChaRte.
            StorCtl_Mod - Activate hold/discharge/charge storage control mode. Bitfield value.
            VAChaMax - Setpoint for maximum charging VA.
            MinRsvPct - Setpoint for minimum reserve for storage as a percentage of the nominal maximum storage.
            ChaState (R) - Currently available energy as a percent of the capacity rating.
            StorAval (R) - State of charge (ChaState) minus storage reserve (MinRsvPct) times capacity rating (AhrRtg).
            InBatV (R) - Internal battery voltage.
            ChaSt (R) - Charge status of storage device. Enumerated value.
            OutWRte - Percent of max discharge rate.
            InWRte - Percent of max charging rate.
            InOutWRte_WinTms - Time window for charge/discharge rate change.
            InOutWRte_RvrtTms - Timeout period for charge/discharge rate.
            InOutWRte_RmpTms - Ramp time for moving from current setpoint to new setpoint.

        :param params: Dictionary of parameters to be updated.
        :return: Dictionary of active settings for HFRT control.
        """
        try:
            if params is not None:
                self.ts.confirm('Set the following parameters %s' % params)

            else:
                params = {}
                params['ChaState'] = 50
                '''
                params['WChaMax'] = self.ts.prompt('WChaMax? ')
                params['WChaGra'] = self.ts.prompt('WChaGra? ')
                params['WDisChaGra'] = self.ts.prompt('WDisChaGra? ')
                params['StorCtl_Mod'] = self.ts.prompt('StorCtl_Mod? ')
                params['VAChaMax'] = self.ts.prompt('VAChaMax? ')
                params['MinRsvPct'] = self.ts.prompt('MinRsvPct? ')
                params['ChaState'] = self.ts.prompt('ChaState? ')
                params['StorAval'] = self.ts.prompt('StorAval? ')
                params['InBatV'] = self.ts.prompt('InBatV? ')
                params['ChaSt'] = self.ts.prompt('ChaSt? ')
                params['OutWRte'] = self.ts.prompt('OutWRte? ')
                params['InWRte'] = self.ts.prompt('InWRte? ')
                params['InOutWRte_WinTms'] = sself.ts.prompt('InOutWRte_WinTms? ')
                params['InOutWRte_RvrtTms'] = self.ts.prompt('InOutWRte_RvrtTms? ')
                params['InOutWRte_RmpTms'] = self.ts.prompt('InOutWRte_RmpTms? ')
                '''
        except Exception as e:
            raise der.DERError(str(e))

        return params

