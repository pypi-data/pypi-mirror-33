"""
RocketLogger Data Import Support.

File reading support for RocketLogger data (rld) files.

Copyright (c) 2016-2018, Swiss Federal Institute of Technology (ETH Zurich)
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""

import os

import numpy as np
import matplotlib.pyplot as plt

from .data import RocketLoggerData

from datetime import datetime, timezone
from math import ceil, floor
import warnings


_ROCKETLOGGER_FILE_MAGIC = 0x444C5225

_CHANNEL_UNIT_NAMES = {
    0: 'unitless',
    1: 'voltage',
    2: 'current',
    3: 'binary',
    4: 'range valid (binary)',
    5: 'illuminance',
    6: 'temerature',
    7: 'integer',
    8: 'percent',
    9: 'preasure',
    0xffffffff: 'undefined',
}


def _decimate_mean(values, decimation_factor):
    """
    Decimate analog values, using averaging of values.

    :param values: Numpy vector of the values to decimate

    :param decimation_factor: The decimation factor

    :returns: Numpy vector of the decimated values
    """
    count_new = floor(values.shape[0] / decimation_factor)
    count_old = count_new * decimation_factor
    aggregated_values = np.reshape(values[0:count_old],
                                   (count_new, decimation_factor))
    return np.mean(aggregated_values, axis=1)


class RocketLoggerCalibrationError(IOError):
    """RocketLogger calibration related errors."""

    pass


class RocketLoggerCalibration:
    """
    RocketLogger calibration support class.

    File reading and basic data processing support for binary RocketLogger data
    files.
    """

    _data_v = None
    _data_i1l = None
    _data_i1h = None
    _data_i2l = None
    _data_i2h = None

    _calibration_scale = []
    _calibration_offset = []

    _error_offset = []
    _error_scale = []

    def __init__(self, *kwargs):
        """

        """

        # if five arguments given, treat them as measurement data
        if True:
            self.load_measurement_data(kwargs)

        pass

    def load_measurement_data(self, data_v, data_i1l, data_i1h,
                              data_i2l, data_i2h):
        """
        Load calibration measurement data from RocketLoggerData structures or
        RocketLogger data files. Loading new measurement data invalidates
        previously made calibration.

        :param data_v: Voltage V1-V4 calibration measurement data or filename.

        :param data_i1l: Current I1L calibration measurement data or filename.

        :param data_i1h: Current I1H calibration measurement data or filename.

        :param data_i2l: Current I2L calibration measurement data or filename.

        :param data_i2h: Current I2H calibration measurement data or filename.
        """
        for data in [data_v, data_i1l, data_i1h, data_i2l, data_i2h]:
            if type(data) is RocketLoggerData:
                continue
            elif os.path.isfile(data):
                data = RocketLoggerData(data)
            else:
                raise ValueError('"{}" is not valid measurement data nor an '
                                 'existing data file.'.format(data))

        # store the loaded data in class
        self._data_v = data_v
        self._data_i1l = data_i1l
        self._data_i1h = data_i1h
        self._data_i2l = data_i2l
        self._data_i2h = data_i2h

        # reset existing calibrations
        self._calibration_scale = []
        self._calibration_offset = []
        self._error_offset = []
        self._error_scale = []

    def calibrate(self):
        """
        Perform channel calibration with loaded measeurement data.
        """

        pass

    def print_statistics(self):
        """
        Print statistics of the calibration.
        """

        pass

    def plot_pareto_curves(self):
        """
        """

        pass

    def write_calibration_file(self):
        """

        """

        pass

    def write_log_file(self):
        """

        """

        pass
