#! python
# -*- coding: utf-8 -*-

"""Example of sequence: Gradient echo phase 1D

:author: Victor Hugo de Mello Pessoa, Daniel Cosmo Pizetta
:email: victor.pessoa@usp.br, daniel.pizetta@usp.br
:since: 08/03/2017

"""

import numpy as np
import pyqtgraph.parametertree as pt

from bloch.simulator import evolve
from mrsprint.sequence import sequence
from mrsprint.simulator import (calculate_t2_star, create_positions,
                                  frequency_shift,
                                  reduce_magnetization_in_position)
from mrsprint.system.rf import rf_delay, rf_duration, square_rf_pulse


class SequenceExample(pt.parameterTypes.GroupParameter):
    """
    Class that configurates the a specific sequence.

    :todo: this class needs to be reviewed for its parameters.
    """

    def __init__(self, settings, **opts):
        """
        Constructor.
        """
        opts['name'] = 'Gradient echo phase 1D'
        opts['type'] = 'bool'
        opts['value'] = True
        pt.parameterTypes.GroupParameter.__init__(self, **opts)

        # Sequence parameters
        self.te = self.addChild({'name': 'Time to echo', 'type': 'float', 'value': 0.1, 'suffix': 's', 'limits': (0, 100), 'siPrefix': True})
        self.te.sigValueChanged.connect(self.setSequence)

        self.xMaxGradient = settings.gradient_group.xMaxValue.value()

        self.rf = None
        self.gr = None
        self.dt = settings.simulator_group.timeResolution.value()
        self.tp = None
        self.setSequence()

    def sequenceAction(self):
        """
        Gradient echo sequence.
        """

        mode = 2
        freq_shift_max = 125
        freq_step = 1
        freq_offset = 0
        t1 = 1.
        t2 = .100

        _logger.debug("in %s", locals())

        position = create_positions(size=(4.8, 1, 1), step=(0.2, 1, 1), offset=(0.2, 0, 0))

        freq_shift = frequency_shift(freq_shift_max, freq_step, freq_offset)
        t2star = calculate_t2_star(t2, freq_shift)
        parameters = Parameter.create(name='params', type='group', children=[seq])

        freq_shift_max = 250
        """
        nvoxels = position.shape[1]
        readout_array = np.zeros((points_to_read.size), dtype=complex)

        print("nvoxels: ", nvoxels)
        print("points_to_read.shape: ", points_to_read.shape, " From ", points_to_read[0], " to ", points_to_read[-1])
        print("readout_array.shape: ", readout_array.shape)

        mx0 = np.zeros(nvoxels * (freq_shift_max - 1)).reshape(freq_shift_max - 1, nvoxels)
        my0 = mx0
        mzi = np.zeros(nvoxels)
        mzi[30:31] = 2.
        mzi[21:23] = 3.
        mzi[nvoxels - 1:nvoxels] = 1.
        mzi[0:3] = 1.
        mz0 = np.zeros(nvoxels * (freq_shift_max - 1)).reshape(freq_shift_max - 1, nvoxels)

        for i in np.arange(0, freq_shift_max - 1):
            mz0[int(i)] = mzi

        mx, my, mz = evolve(rf, gr, DT, t1, t2, freq_shift, position, mode, mx0, my0, mz0)
        mxf, myf, mzf = reduceMagnetizationInPosition(mx, my, mz, position, freq_shift)
        mxy = mxf + 1.0j * myf
        cra = mxy[points_to_read[0]:points_to_read[-1] + 1]

        print("readout,shape", readout_array.shape)
        plotEverything(mx, my, mz, gr, rf, freq_shift, position, cra)
        """

    def setSequence(self):
        """Creates two np.array to contain both RF data and Gradient data."""
        seq = sequence.CPMGSequence()
        self.rf = seq.getRF()
        self.gr = seq.getGradient()

        # pulse 90 degrees in y
        p90y = square_rf_pulse(90, 0)
        d90 = rf_delay(rf_duration(p90y))
        # delay time to echo
        dte2 = rf_delay(self.te.value() / 2.)
        # rf pulse sequence
        self.rf = np.concatenate((np.zeros(100), p90y, dte2, dte2, dte2, dte2, dte2, dte2))
        grx = np.concatenate((np.zeros(100), d90.real, dte2.real, dte2.real - 1, dte2.real + 1, dte2.real + 1, dte2.real, dte2.real))
        grx_read = np.concatenate((np.zeros(100), d90.real, dte2.real, dte2.real, dte2.real + 1, dte2.real + 1, dte2.real, dte2.real))
        # index from start read gradient to the end of it
        points_to_read = np.nonzero(grx_read)[0]
        # 3d gradient
        self.gr = np.concatenate((grx, np.zeros(grx.size) * self.xMaxGradient, np.zeros(grx.size))).reshape(3, grx.size)
        self.tp = np.arange(0, self.rf.size) * self.dt
