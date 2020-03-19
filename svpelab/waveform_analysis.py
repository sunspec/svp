"""
Waveform Analysis

V 1.0 - Javier Hernandez-Alvidrez, Sandia National Labs - 1/12/17

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



try:
    from prettytable import PrettyTable
except Exception as e:
    print('Error: prettytable python package not found!')  # This will appear in the SVP log file.

try:
    from matplotlib.mlab import find
    import matplotlib.pyplot as plt
except Exception as e:
    print('Error: matplotlib python package not found!')  # This will appear in the SVP log file.

try:
    import numpy as np
except Exception as e:
    print('Error: numpy python package not found!')  # This will appear in the SVP log file.

try:
    import math
except Exception as e:
    print('Error: math python package not found!')  # This will appear in the SVP log file.

def calc_ride_through_duration(wfmtime, ac_current, ac_voltage=None, grid_trig=None, v_window=20., trip_thresh=3.):
    """ Returns the time between the voltage change and when the EUT tripped

    wfmtime is the time vector from the waveform
    ac_current is the raw current measurement from the DAQ corresponding to wfmtime times
    ac_voltage  is the raw voltage measurements from the DAQ corresponding to wfmtime times
    grid_trig is the trigger measurement corresponding to wfmtime times
    v_window is the window around the nominal RMS voltage where the VRT test is started
    trip_thresh is the RMS current level where the EUT is believe to be tripped or ceasing to energize

    There are two options for determining the start of the VRT test (the latter is used when ac_voltage != None)
    1. Using the trigger channel from the grid simulator
    2. Using the RMS calculation of the ac voltage to determine when the voltage exits v_nominal +/- v_window
    """

    f_grid = 60.
    cycles_in_window = 1.
    window_size = cycles_in_window*(1./f_grid)*1000.  # in ms

    if ac_voltage is not None:  # use the ac voltage RMS values to determine when the vrt test starts
        time_RMS, ac_voltage_RMS = calculateRmsOfSignal(ac_voltage, windowSize=window_size,
                                                        samplingFrequency=24e3,
                                                        overlap=int(window_size/3))
        v_nom = 240.
        volt_idx = [idx for idx, i in enumerate(ac_voltage_RMS) if (i <= (v_nom - v_window) or i >= (v_nom + v_window))]
        if len(volt_idx) != 0:
            try:
                vrt_start = time_RMS[min(volt_idx)]
            except:
                raise script.ScriptFail('Error in Waveform File. Unable to get voltage time from wfmtime: %s' % str(e))
        else:
            raise script.ScriptFail('No voltage deviation in the waveform file.')

        '''
        # for comparison
        trig_thresh = 3.
        trig_idx = [idx for idx, i in enumerate(grid_trig) if i >= trig_thresh]
        if len(trig_idx) != 0:
            try:
                vrt_start = wfmtime[min(trig_idx)]
            except:
                raise script.ScriptFail('Error in Waveform File. Unable to get trig time from wfmtime: %s' % str(e))
        else:
            raise script.ScriptFail('No daq trigger in the waveform file.')
        '''

    else:  # use the trigger to indicate when the grid simulator started the VRT test
        trig_thresh = 3.
        trig_idx = [idx for idx, i in enumerate(grid_trig) if i >= trig_thresh]
        if len(trig_idx) != 0:
            try:
                vrt_start = wfmtime[min(trig_idx)]
            except:
                raise script.ScriptFail('Error in Waveform File. Unable to get trig time from wfmtime: %s' % str(e))
        else:
            raise script.ScriptFail('No daq trigger in the waveform file.')

    ac_current_thresh = trip_thresh  # Amps
    time_RMS, ac_current_RMS = calculateRmsOfSignal(ac_current, windowSize=window_size,
                                                    samplingFrequency=24e3,
                                                    overlap=int(window_size/3))

    ac_current_idx = [idx for idx, i in enumerate(ac_current_RMS) if i <= ac_current_thresh]
    if len(ac_current_idx) != 0:
        try:
            trip_time = time_RMS[min(ac_current_idx)]
        except:
            raise script.ScriptFail('Error in Waveform File. Unable to get trip time from wfmtime: %s' % str(e))

        '''
        plt.plot(wfmtime, ac_current, color='blue', label='ac_current')
        plt.plot(time_RMS, ac_current_RMS, color='black', label='ac_current_RMS')
        plt.plot(wfmtime, grid_trig, color='g', label='grid_trig')
        plt.plot([vrt_start, vrt_start], [min(ac_current), max(ac_current)], color='red', label='VRT start-trig')
        # plt.plot([vrt_start_RMS, vrt_start_RMS], [min(ac_current), max(ac_current)], 'r-.', label='VRT start-RMS')
        plt.plot([trip_time, trip_time], [min(ac_current), max(ac_current)], 'r--', label='EUT trip')
        plt.legend()
        plt.grid(which='both', axis='both')
        plt.show()
        '''

        return trip_time - vrt_start

    else:
        trip_time = 0.  # no trip occurred
        return trip_time


def freq_from_crossings(wfmtime, sig, fs):
    """Estimate frequency by counting zero crossings

    Doesn't work if there are multiple zero crossings per cycle.

    """
    try:
        from scipy import signal
    except Exception as e:
        print('Error: scipy python package not found!')  # This will appear in the SVP log file.

    # FILTER THE WAVEFORM WITH LOWPASS BUTTERWORTH FILTER
    # todo: revisit the wn calculation to be sure it works for multiple sampling rates
    wn = (2*math.pi*60)/fs  #Wn is normalized from 0 to 1, where 1 is the Nyquist frequency, pi radians/sample
    b, a = signal.butter(4, wn, analog=False)
    sig_ff = signal.filtfilt(b, a, sig)

    #check the frequency response
    '''
    w, h = signal.freqs(b, a)
    plt.plot(w, 20 * np.log10(abs(h)))
    plt.xscale('log')
    plt.title('Butterworth filter frequency response')
    plt.xlabel('Frequency [radians / second]')
    plt.ylabel('Amplitude [dB]')
    plt.margins(0, 0.1)
    plt.grid(which='both', axis='both')
    plt.show()
    '''

    # Find the zero crossings of the filtered data
    # Linear interpolation to find truer zero crossings

    indices = find(np.logical_and(sig_ff[1:] >= 0., sig_ff[:-1] < 0.))
    crossings = [i - sig_ff[i] / (sig_ff[i+1] - sig_ff[i]) for i in indices]  #interpolate
    cross_times = wfmtime[0] + np.array(crossings)/fs

    '''
    plt.plot(wfmtime, sig, color='red', label='Original')
    plt.plot(wfmtime, sig_ff, color='blue', label='filtered data')
    plt.plot(cross_times, np.zeros(len(cross_times)), 'ro', label='Zero Crossings')
    plt.legend()
    plt.grid(which='both', axis='both')
    plt.axis([0, 5/60, min(sig)/2, max(sig)/2])
    plt.show()
    '''

    time_steps = np.diff(crossings)
    avg_freq = fs / np.average(time_steps)
    freqs = [fs/time_steps[i] for i in range(0, len(cross_times)-1)]  #interpolate
    freq_times = [(cross_times[i]+cross_times[i+1])/2 for i in range(0, len(freqs)-1)]  #interpolate

    # plt.plot(wfmtime, sig, color='red', label='Original')
    # plt.plot(wfmtime, sig_ff, color='blue', label='Filtered data')
    # plt.plot(freq_times, freqs[:-1], 'g', label='Frequency')
    # plt.legend(loc=4)
    # plt.grid(which='both', axis='both')
    # plt.axis([0, freq_times[-1], 50, 61])
    # plt.show()

    return avg_freq, freqs


def calculateRMS(data):
    ######################################################################
    #   calculates the RMS data of the given array
    #   @param a list or a numpy array
    #   @return a scalar containing either an RMS value
    #   http://homepage.univie.ac.at/christian.herbst//python/dsp_util_8py_source.html
    tmp = 0
    size = len(data)
    for i in range(size):
        tmp += data[i]
    mean = tmp / float(size)
    #print "mean: ", mean
    tmp = 0
    for i in range(size):
        tmp2 = data[i] - mean
        tmp += tmp2 * tmp2
    tmp /= float(size)
    return math.sqrt(tmp)


def calculateRmsOfSignal(data, windowSize, samplingFrequency, overlap=0):
    ######################################################################
    #   calculate and return the time-varying RMS of a signal
    #   @param data a list or a numpy array containing the signal that should be
    #       analyzed
    #   @param windowSize duration of the sliding analysis window in milli-seconds
    #   @param samplingFrequency sampling frequency [Hz]
    #   @param overlap overlap between individual windows, specified in milli-seconds
    #   @return a tuple containing two numpy arrays for the temporal offset and the
    #       RMS value at the respective temporal offset.
    #   http://homepage.univie.ac.at/christian.herbst//python/dsp_util_8py_source.html

    if windowSize < 1:
        raise Exception("window size must not below 1 ms")
    if overlap >= windowSize:
        raise Exception("overlap must not exceed window size")

    numFrames = len(data)
    duration = numFrames / float(samplingFrequency)

    readProgress = (windowSize - overlap) / 1000.0
    outputSize = int(duration / readProgress)
    dataX = np.zeros(outputSize)
    dataY = np.zeros(outputSize)
    t = 0
    halfWindowSize = windowSize / 2000.0
    for idx in range(outputSize):
        left = int((t - halfWindowSize) * float(samplingFrequency))
        right = left + int(windowSize * float(samplingFrequency) / 1000.0)
        if right >= numFrames:
            right = numFrames - 1
        numFramesLocal = right - left
        #print idx, t, left, right, readProgress
        if numFramesLocal <= 0:
            raise Exception("zero window size (t = " + str(t) + " sec.)")
        dataTmp = np.zeros(numFramesLocal)
        for i in range(numFramesLocal):
            dataTmp[i] = data[i + left]
        dataX[idx] = t
        t += readProgress
        rms = calculateRMS(dataTmp)
        dataY[idx] = rms

    return dataX[1:], dataY[1:]  # throw away awful first data point


def active_power_from_waveform(t, V, I, sampling_rate, ts):
    """
    :param t: time vector (numpy)
    :param V: voltage vector (numpy)
    :param I: current vector (numpy)
    :param sampling_rate - sampling rate (int)
    :param ts - test script with logging capabilities

    :return:
    : avg_P - Average active power
    """
    pass


def reactive_power_from_waveform(t, V, I, sampling_rate, ts):
    """
    :param t: time vector (numpy)
    :param V: voltage vector (numpy)
    :param I: current vector (numpy)
    :param sampling_rate - sampling rate (int)
    :param ts - test script with logging capabilities

    :return:
    : Q1 - Fundamental Reactive Power
    """
    pass


def pf_from_waveform(t, V, I, sampling_rate, ts):
    """
    :param t: time vector (numpy)
    :param V: voltage vector (numpy)
    :param I: current vector (numpy)
    :param sampling_rate - sampling rate (int)
    :param ts - test script with logging capabilities

    :return:
    : PF - Power factor
    """
    pass


def harmonic_analysis(t, V, I, sampling_rate, ts):
    """
    :param t: time vector (numpy)
    :param V: voltage vector (numpy)
    :param I: current vector (numpy)
    :param sampling_rate - sampling rate (int)
    :param ts - test script with logging capabilities

    :return:
    : avg_P - Average active power
    : P1 - Fundamental active power
    : PH - Nonfundamental active power

    : N - Nonactive Power
    : Q1 - Fundamental Reactive Power
    : DI - Current distortion power
    : DV - Voltage distortion power
    : DH - Harmonic distortion power

    : S - Combined Apparent Power
    : S1 - Fundamental Apparent Power
    : SN - Nonfundamental Apparent Power
    : SH - Harmonic Apparent power

    : PF1 - Fundamental power factor
    : PF - Power factor

    : har_poll - Harmonic pollution

    : THD_V - Voltage Total Harmonic Distortion
    : THD_I - Current Total Harmonic Distortion
    """
    # import time
    # harmonic_start = time.time()

    P = V*I
    # w = 2*np.pi

    Fs = sampling_rate
    n_samples = len(t)

    # full spectrum
    ffI = np.fft.fft(I, n_samples)
    ffV = np.fft.fft(V, n_samples)
    # xfft = np.arange(0, len(ffI))*(Fs/len(ffI))  # x-axis of frequency for plotting

    # only half of the fft coefficients
    ffI2 = ffI[0:int(n_samples/2.)]
    ffV2 = ffV[0:int(n_samples/2.)]
    # xfft2 = xfft[0:int(n_samples/2.)]

    harmonicsI = [[], [], [], []]  # [[harmonic index], [complex fft], [abs(complex fft)], [angle of complex fft]]
    harmonicsV = [[], [], [], []]  # [[harmonic index], [complex fft], [abs(complex fft)], [angle of complex fft]]
    powers = [[], [], []]  # [[harmonics], [P at that harmonic], [Q at that harmonic]]
    # recoverI = []
    # recoverV = []

    # for i in range(len(ffI2)):
    for i in range(41):  # IEEE Std 1547.1-2005
        # ts.log_debug('Harmonic %d has mag %s' % (i, abs(ffI2[i])))

        # if abs(ffI2[i]) >= 3.:  # threshold for removing nonsignificant harmonics
        harmonicsI[0] += [i]
        harmonicsI[1] += [ffI2[i]*2/len(ffI)]
        harmonicsI[2] += [abs(ffI2[i])*2/len(ffI)]
        harmonicsI[3] += [np.angle(ffI2[i])]

        harmonicsV[0] += [i]
        harmonicsV[1] += [ffV2[i]*2/len(ffV)]
        harmonicsV[2] += [abs(ffV2[i])*2/len(ffV)]
        harmonicsV[3] += [np.angle(ffV2[i])]

    harmonicsI[1][0] = harmonicsI[1][0]/2
    harmonicsI[2][0] = abs(np.real(harmonicsI[1][0]))
    harmonicsV[1][0] = harmonicsV[1][0]/2
    harmonicsV[2][0] = abs(np.real(harmonicsV[1][0]))

    # Use to compare to other calculations
    # for i in range(len(t)):
    #     acumI = 0.0
    #     acumV = 0.0
    #     for k in range(1, len(harmonicsI[0])):
    #         acumI += harmonicsI[2][k]*np.sin(w*harmonicsI[0][k]*(Fs/len(ffI))*t[i] + harmonicsI[3][k] + (np.pi)/2)
    #         acumV += harmonicsV[2][k]*np.sin(w*harmonicsV[0][k]*(Fs/len(ffV))*t[i] + harmonicsV[3][k] + (np.pi)/2)
    #     acumI += np.real(harmonicsI[1][0])
    #     acumV += np.real(harmonicsV[1][0])
    #     recoverI += [acumI]
    #     recoverV += [acumV]

    ###############################################################################
    ################ CALCULATIONS ACCORDING TO IEEE 1459 ##########################
    ###############################################################################

    # THD = VH/V1
    VHsq = 0.0
    IHsq = 0.0
    # V0sq = 0.0
    # I0sq = 0.0
    V1sq = 0.0
    I1sq = 0.0

    for i in range(len(harmonicsV[0])):
        if harmonicsV[0][i] == 0:  # for DC
            #THDs
            V0sq = np.square(harmonicsV[2][i])
            I0sq = np.square(harmonicsI[2][i])
            VHsq += V0sq
            IHsq += I0sq

            #harmonics power
            powers[0] += [harmonicsI[0][i]*(Fs/len(I))/60.0]  # Harmonics
            powers[1] += [np.real(harmonicsI[1][i])*np.real(harmonicsV[1][i])]  # power associated with the harmonic
            powers[2] += [0]  # Reactive powers associated with those harmonics

        elif harmonicsV[0][i]*Fs/len(t) == 60:  # for fundamental
            #THDs
            V1sq = np.square(harmonicsV[2][i])/2
            I1sq = np.square(harmonicsI[2][i])/2
            VHsq += 0.0
            IHsq += 0.0
            #harmonics power
            powers[0] += [harmonicsI[0][i]*(Fs/len(I))/60.0]
            powers[1] += [harmonicsI[2][i]*harmonicsV[2][i]*np.cos(harmonicsI[3][i]-harmonicsV[3][i])/2]
            powers[2] += [harmonicsI[2][i]*harmonicsV[2][i]*np.sin(harmonicsI[3][i]-harmonicsV[3][i])/2]

        else:  # for the rest of the harmonics
            #THDs
            VHsq += np.square(harmonicsV[2][i])/2
            IHsq += np.square(harmonicsI[2][i])/2
            # harmonic power
            powers[0] += [harmonicsI[0][i]*(Fs/len(I))/60.0]
            powers[1] += [harmonicsI[2][i]*harmonicsV[2][i]*np.cos(harmonicsI[3][i]-harmonicsV[3][i])/2]
            powers[2] += [0]

    # Vsq = V1sq+VHsq
    # Isq = I1sq+IHsq

    THD_I = np.sqrt(IHsq/I1sq)
    THD_V = np.sqrt(VHsq/V1sq)

    # THD_I2 = np.sqrt((Isq/I1sq)-1)
    # THD_V2 = np.sqrt((Vsq/V1sq)-1)

    # instantaneous power
    i_P = 0.0
    for i in range(len(P)):
        i_P += P[i]

    avg_P = i_P/len(P)  # includes all the harmonics (P1 is just the fundamental)
    # avg_P2 = np.mean(P)

    PH = 0.0
    P1 = 0.0

    for i in range(len(powers[0])):
        if powers[0][i] == 1:
            P1 = powers[1][i]  # active power (fundamental)
            Q1 = -powers[2][i]  # reactive power (fundamental) (negative value to be generator POV)
        else:
            PH += powers[1][i]  # real power from harmonics
    if Q1 is None:
        ts.log_warning('No fundamental frequency for given capture timing parameters. Will not calculate P1 or Q1.')

    # Fundamental Apparent Power
    S1 = np.sqrt(np.square(P1)+np.square(Q1))

    # Current distortion power
    DI = -S1*THD_I  # (negative value to be generator POV)
    # DI_2 = np.sqrt(V1sq)*(np.sqrt(Isq-I1sq))

    # Voltage distortion power
    DV = -S1*THD_V # (negative value to be generator POV)
    # DV_2 = np.sqrt(Vsq-V1sq)*np.sqrt(I1sq)

    # Harmonic Apparent power
    SH = S1*THD_I*THD_V
    # SH_2 = (np.sqrt(Isq-I1sq))*np.sqrt(Vsq-V1sq)

    # Harmonic distortion power
    # DH = np.sqrt(np.square(SH)-np.square(PH))

    # Nonfundamental Apparent Power (SN)
    SN = np.sqrt(np.square(DI) + np.square(DV) + np.square(SH))
    S = np.sqrt(np.square(S1)+np.square(SN))

    # Nonactive Power
    N = -np.sqrt(np.square(S)-np.square(avg_P))  # (negative value to be generator POV)

    # Fundamental power factor
    # ts.log_debug('PF1 = %0.3f, P1 = %0.3f, S1 = %0.3f' % (P1/S1, P1, S1))
    PF1 = P1/S1
    # Power factor
    PF = avg_P/S

    # PF Convention
    if (Q1 > 0 and avg_P > 0) or (Q1 < 0 and avg_P < 0):
        PF1 = -PF1
        PF = -PF

    # Harmonic pollution
    # har_poll = SN/S1

    # ts.log_debug('Time to complete harmonic analysis = %s' % (time.time() - harmonic_start))

    # return avg_P, P1, PH, N, Q1, DI, DV, DH, S, S1, SN, SH, PF1, PF, har_poll, THD_V, THD_I
    return avg_P, S, Q1, N, PF1


if __name__ == "__main__":

    t, V, I = np.loadtxt('c:\DATA_INVERTERS\WAVEFORMS\FRONIUS_Node_10_1.csv', delimiter=',', unpack=True)

    P = V*I
    w = 2*np.pi

    Fs = 10000
    ffI = np.fft.fft(I, len(t))
    ffV = np.fft.fft(V, len(t))
    xfft = np.arange(0, len(ffI))*(Fs/len(ffI))

    ffI2 = ffI[0:500]
    ffV2 = ffV[0:500]
    xfft2 = xfft[0:500]

    # Plot harmonics of current and voltage

    plt.subplot(4, 1, 2)
    plt.plot(xfft2,abs(ffI2)*2/len(ffI), label='current harmonics')
    plt.grid()
    plt.legend()
    plt.subplot(4, 1, 4)
    plt.plot(xfft2, abs(ffV2)*2/len(ffV), label='voltage harmonics')
    plt.grid()
    plt.legend()
    plt.show()

    # lists with harmonic content harmonicsVI = [[n],[complex/norm],[abs/norm],[phase]] = [[0],[1],[2],[3]]
    # [0] = n
    # [1] = complex/norm
    # [2] = abs/norm
    # [3] = phase

    harmonicsI = [[], [], [], []]
    harmonicsV = [[], [], [], []]
    powers = [[], [], []]
    recoverI = []
    recoverV = []

    for i in range(len(ffI2)):
        if abs(ffI2[i]) >= 0.15:
            harmonicsI[0] += [i]
            harmonicsI[1] += [ffI2[i]*2/len(ffI)]
            harmonicsI[2] += [abs(ffI2[i])*2/len(ffI)]
            harmonicsI[3] += [np.angle(ffI2[i])]

            harmonicsV[0] += [i]
            harmonicsV[1] += [ffV2[i]*2/len(ffV)]
            harmonicsV[2] += [abs(ffV2[i])*2/len(ffV)]
            harmonicsV[3] += [np.angle(ffV2[i])]

    harmonicsI[1][0] = harmonicsI[1][0]/2
    harmonicsI[2][0] = abs(np.real(harmonicsI[1][0]))
    harmonicsV[1][0] = harmonicsV[1][0]/2
    harmonicsV[2][0] = abs(np.real(harmonicsV[1][0]))

    # synthesis
    for i in range(len(t)):
        acumI = 0.0
        acumV = 0.0
        for k in range(1,len(harmonicsI[0])):
            acumI += harmonicsI[2][k]*np.sin(w*harmonicsI[0][k]*(Fs/len(ffI))*t[i] + harmonicsI[3][k] + (np.pi)/2)
            acumV += harmonicsV[2][k]*np.sin(w*harmonicsV[0][k]*(Fs/len(ffV))*t[i] + harmonicsV[3][k] + (np.pi)/2)
        acumI += np.real(harmonicsI[1][0])
        acumV += np.real(harmonicsV[1][0])
        recoverI += [acumI]
        recoverV += [acumV]

    plt.subplot(4, 1, 1)
    plt.plot(t, I, label='original')
    plt.plot(t, recoverI, label='recovered')
    plt.xlim(0, 0.1)
    plt.grid()
    plt.legend()

    plt.subplot(4, 1, 3)
    plt.plot(t, V, label='original')
    plt.plot(t, recoverV, label='recovered')
    plt.xlim(0,0.1)
    plt.grid()
    plt.legend()
    plt.show()

    ###############################################################################
    ################ CALCULATIONS ACCORDING TO IEEE 1459 ##########################
    ###############################################################################

    #THD = VH/V1
    VHsq = 0.0
    IHsq = 0.0
    V0sq = 0.0
    I0sq = 0.0
    V1sq = 0.0
    I1sq = 0.0

    for i in range(len(harmonicsV[0])):
        if harmonicsV[0][i]==0:
            #THDs
            V0sq = np.square(harmonicsV[2][i])
            I0sq = np.square(harmonicsI[2][i])
            VHsq += V0sq
            IHsq += I0sq
            #harmonics power
            powers[0] += [harmonicsI[0][i]*(Fs/len(I))/60.0]
            powers[1] += [np.real(harmonicsI[1][i])*np.real(harmonicsV[1][i])]
            powers[2] += [0]

        elif harmonicsV[0][i]*Fs/len(t)==60:
            #THDs
            V1sq = np.square(harmonicsV[2][i])/2
            I1sq = np.square(harmonicsI[2][i])/2
            VHsq += 0.0
            IHsq += 0.0
            #harmonics power
            powers[0] += [harmonicsI[0][i]*(Fs/len(I))/60.0]
            powers[1] += [harmonicsI[2][i]*harmonicsV[2][i]*np.cos(harmonicsI[3][i]-harmonicsV[3][i])/2]
            powers[2] += [harmonicsI[2][i]*harmonicsV[2][i]*np.sin(harmonicsI[3][i]-harmonicsV[3][i])/2]

        else:
            #THDs
            VHsq += np.square(harmonicsV[2][i])/2
            IHsq += np.square(harmonicsI[2][i])/2
            #harmonics power
            powers[0] += [harmonicsI[0][i]*(Fs/len(I))/60.0]
            powers[1] += [harmonicsI[2][i]*harmonicsV[2][i]*np.cos(harmonicsI[3][i]-harmonicsV[3][i])/2]
            powers[2] += [0]



    Vsq = V1sq+VHsq
    Isq = I1sq+IHsq

    THD_I = np.sqrt(IHsq/I1sq)
    THD_V = np.sqrt(VHsq/V1sq)

    THD_I2 = np.sqrt((Isq/I1sq)-1)
    THD_V2 = np.sqrt((Vsq/V1sq)-1)

    #instantaneous power
    i_P = 0.0
    for i in range(len(P)):
        i_P += P[i]

    avg_P = i_P/len(P)
    avg_P2 = np.mean(P)

    #plt.plot(t,P)
    PH = 0.0
    P1 = 0.0

    for i in range(len(powers[0])):
        if powers[0][i] == 1:
            P1 = powers[1][i]
            Q1 = powers[2][i]
        else:
            PH += powers[1][i]


    #Fundamental Apparent Power
    S1 = np.sqrt(np.square(P1)+np.square(Q1))

    #Current distortion power
    DI = S1*THD_I
    DI_2 = np.sqrt(V1sq)*(np.sqrt(Isq-I1sq))

    #Voltage distortion power
    DV = S1*THD_V
    DV_2 = np.sqrt(Vsq-V1sq)*np.sqrt(I1sq)

    #Harmonic Apparent power
    SH = S1*THD_I*THD_V
    SH_2 = (np.sqrt(Isq-I1sq))*np.sqrt(Vsq-V1sq)

    #Harmonic distortion power
    DH = np.sqrt(np.square(SH)-np.square(PH))

    #Nonfundamental Apparent Power
    SN = np.sqrt(np.square(DI) + np.square(DV) + np.square(SH))
    S = np.sqrt(np.square(S1)+np.square(SN))

    #Nonactive Power
    N = np.sqrt(np.square(S)-np.square(avg_P))

    #Fundamental power factor
    PF1 = P1/S1

    #Power factor
    PF = avg_P/S

    #Harmonic pollution
    har_poll = SN/S1

    #Show results

    x = PrettyTable()
    x.field_names = ["Quantity or indicator","Combined","Fundamental Powers","Nonfundamental Powers"]
    x.add_row(["Apparent","S = "+repr(S),"S1 = "+repr(S1),"SN = "+repr(SN)])
    x.add_row(["","","","SH = "+repr(SH)])
    x.add_row(["----------------------","------------------------","------------------------","----------------------------"])
    x.add_row(["Active","P = "+repr(avg_P),"P1 = "+repr(P1),"PH = "+repr(PH)])
    x.add_row(["----------------------","------------------------","------------------------","----------------------------"])
    x.add_row(["Nonactive","N = "+repr(N),"Q1 = "+repr(Q1),"DI = "+repr(DI)])
    x.add_row(["","","","DV = "+repr(DV)])
    x.add_row(["","","","DH = "+repr(DH)])
    x.add_row(["----------------------","------------------------","------------------------","----------------------------"])
    x.add_row(["Line Utilization","PF = "+repr(PF),"PF1 = "+repr(PF1),"--------"])
    x.add_row(["----------------------","------------------------","------------------------","----------------------------"])
    x.add_row(["Harmonic Pollution","--------","--------","SN/S1 = "+repr(har_poll)])

    print(x)


