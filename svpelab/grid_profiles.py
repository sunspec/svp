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

# (time offset in seconds, % nominal voltage 1, % nominal voltage 2, % nominal voltage 3, % nominal frequency)
vv_voltage_profile = [
    (0, 100, 100, 100, 100),
    (30, 100, 100, 100, 100),
    (30, 106, 106, 106, 100),
    (60, 106, 106, 106, 100),
    (60, 94, 94, 94, 100),
    (90, 94, 94, 94, 100),
    (90, 100, 100, 100, 100),
    (120, 100, 100, 100, 100),
    (135, 106, 106, 106, 100),
    (150, 106, 106, 106, 100),
    (180, 94, 94, 94, 100),
    (195, 94, 94, 94, 100),
    (210, 100, 100, 100, 100),
    (240, 100, 100, 100, 100),
    (245, 106, 106, 106, 100),
    (250, 106, 106, 106, 100),
    (260, 94, 94, 94, 100),
    (265, 94, 94, 94, 100),
    (270, 100, 100, 100, 100),
    (300, 100, 100, 100, 100)
]

vrt_50v_2s = [
    (0, 50, 50, 50, 100),
    (2, 50, 50, 50, 100),
    (2, 100, 100, 100, 100)
]

# (time offset in seconds, % nominal voltage, % nominal frequency)
fw_freq_profile = [
    (0, 100.0, 100.0, 100.0, 100.0),
    (30, 100.0, 100.0, 100.0, 100.0),
    (30, 100.0, 100.0, 100.0, 103.0),
    (60, 100.0, 100.0, 100.0, 103.0),
    (60, 100.0, 100.0, 100.0, 97.0),
    (90, 100.0, 100.0, 100.0, 97.0),
    (90, 100.0, 100.0, 100.0, 103.0),
    (95, 100.0, 100.0, 100.0, 103.0),
    (95, 100.0, 100.0, 100.0, 100.0),
    (125, 100.0, 100.0, 100.0, 100.0),
    (155, 100.0, 100.0, 100.0, 102.0),
    (185, 100.0, 100.0, 100.0, 102.0),
    (215, 100.0, 100.0, 100.0, 98.0),
    (245, 100.0, 100.0, 100.0, 98.0),
    (260, 100.0, 100.0, 100.0, 102.0),
    (275, 100.0, 100.0, 100.0, 102.0),
    (280, 100.0, 100.0, 100.0, 100.0),
    (295, 100.0, 100.0, 100.0, 100.0),
    (310, 100.0, 100.0, 100.0, 100.3),
    (325, 100.0, 100.0, 100.0, 100.3),
    (340, 100.0, 100.0, 100.0, 100.0),
    (360, 100.0, 100.0, 100.0, 100.0)
]

profiles = {
    'FW Profile': fw_freq_profile,
    'VV Profile': vv_voltage_profile,
    'VRT Test Profile': vrt_50v_2s
}

if __name__ == "__main__":

    pass
