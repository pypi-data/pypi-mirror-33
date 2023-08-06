#! python
# -*- coding: utf-8 -*-

"""Gradient echo with phase enconding 2D.

Authors:
    * Daniel Cosmo Pizetta <daniel.pizetta@usp.br>
    * Victor Hugo de Mello Pessoa <victor.pessoa@usp.br>

Since:
    2017/03/08

"""

import numpy as np
import pyqtgraph.parametertree as pt

from mrsprint.sequence import sequence
from mrsprint.simulator import (calculate_t2_star, create_positions,
                                frequency_shift,
                                reduce_magnetization_in_position)
from mrsprint.system.rf import rf_delay, rf_duration, square_rf_pulse


class SequenceExample(pt.parameterTypes.GroupParameter):
    """Class that configure the a specific sequence.

    Todo:
        This class needs to be reviewed for its parameters.
    """

    def __init__(self, settings, nucleus, **opts):
        opts['name'] = 'Gradient echo phase 2D'
        opts['type'] = 'bool'
        opts['value'] = True
        pt.parameterTypes.GroupParameter.__init__(self, **opts)

        # Sequence parameters
        self.te = self.addChild({'name': 'Time to echo', 'type': 'float', 'value': 0.1, 'suffix': 's', 'limits': (0, 100), 'siPrefix': True})
        self.te.sigValueChanged.connect(self.setSequence)

        self.xMaxGradient = settings.gradient_group.xMaxValue.value()
        self.yMaxGradient = settings.gradient_group.yMaxValue.value()

        self.dt = settings.simulator_group.timeResolution.value()
        self.b1_max = settings.rf_group.amMaxValue.value()
        self.gamma = nucleus.gamma.value()

        self.rf = None
        self.gr = None
        self.tp = None

        self.setSequence()

    def sequenceAction(self):
        """Gradient echo sequence."""

        mode = 2
        freq_shift_max = 36
        freq_step = 1
        t1 = 1.
        t2 = .100

        _logger.debug("in %s", locals())

        position = create_positions(size=(4.8, 4.8, 1), step=(0.8, 0.8, 1), offset=(0.2, 0.2, 0))

        freq_shift = frequency_shift(freq_shift_max, freq_step)
        t2star = calculate_t2_star(t2, freq_shift)

        freq_shift_max = 250

        """
        phase_encs = 12
        phase_enc = 0
        nvoxels = position.shape[1]
        readout_array = np.zeros((phase_encs, phase_encs), dtype=complex)

        print("nvoxels: ", nvoxels)
        print("phase_enc: ", phase_encs)
        print("points_to_read.shape: ", points_to_read.shape, " From ", points_to_read[0], " to ", points_to_read[-1])
        print("readout_array.shape: ", readout_array.shape)

        mx0 = np.zeros(nvoxels * (freq_shift_max - 1)).reshape(freq_shift_max - 1, nvoxels)
        my0 = mx0
        mzi = np.ones(nvoxels)
        mzi[3] = 2
        mzi[6] = 2
        mzi[11] = 0
        mzi[15] = 0
        mzi[9] = 1
        mzi[12] = 1
        mzi[0] = 0

        mz0 = np.zeros(nvoxels * (freq_shift_max - 1)).reshape(freq_shift_max - 1, nvoxels)

        for i in np.arange(0, freq_shift_max - 1):
            mz0[int(i)] = mzi

        print("mag_zero.shape: ", mx0.shape)
        print("mag_z.shape: ", mz0.shape)

        for grady in np.linspace(0, 1., phase_encs):
            # create a new phase gradient
            gr[1][:] = gry * grady * GR_MAX * 0.1
            print("Current phase encoding: ", phase_enc + 1, " of ", phase_encs, "with grady = ", grady)
            # colocar um erro na função bloch caso mx0, my0 ou mz0 não tenham as dimensoes corretas,
            # ele ignora e nao avisa, duas hrs pra encontrar isso
            print("bef mag_zero.shape: ", mx0.shape)
            print("bef mag_z.shape: ", mz0.shape)
            mx, my, mz = evolve(rf, gr, DT, t1, t2, freq_shift, position, 2, mx0, my0, mz0)
            print("aft mag_zero.shape: ", mx.shape)
            print("aft mag_z.shape: ", mz.shape)
            mxf, myf, mzf = reduceMagnetizationInPosition(mx, my, mz, position, freq_shift)
            print("mxf.shape: ", mxf.shape)
            mxy = mxf + 1.0j * myf
            cra = mxy[points_to_read[0]:points_to_read[-1] + 1]
            print("cra", cra.shape)
            readout_array[phase_enc] = cra[int(cra.size / 2) - int(phase_encs / 2): int(cra.size / 2) + int(phase_encs / 2)]
            #plotEverything(tp, mx, my, mz, gr, rf, freq_shift, position, cra[int(cra.size / 2) - 1024 / 2:int(cra.size / 2) + 1024 / 2])
            phase_enc += 1
        print("readout,shape", readout_array.shape)
        plotEverything(mx, my, mz, gr, rf, freq_shift, position, readout_array)
        """

    def setSequence(self):
        """Creates two np.array to contain both RF data and Gradient data."""
        # pulse 90 degrees in y
        p90y = square_rf_pulse(self.dt, self.gamma, self.b1_max, 90, 0)
        d90 = rf_delay(rf_duration(p90y, self.dt), self.dt)

        # delay time to echo
        dte = rf_delay(self.te.value(), self.dt)
        dte2 = rf_delay(self.te.value() / 2., self.dt)

        # rf pulse sequence
        self.rf = np.concatenate((np.zeros(100), p90y, dte2, dte2, dte2, dte2, dte2, dte2))
        grx = np.concatenate((np.zeros(100), d90.real, dte2.real, dte2.real - 1, dte2.real + 1, dte2.real + 1, dte2.real, dte2.real))
        gry = np.concatenate((np.zeros(100), d90.real, dte2.real, dte2.real + 1, dte2.real, dte2.real, dte2.real, dte2.real))
        grx_read = np.concatenate((np.zeros(100), d90.real, dte2.real, dte2.real, dte2.real + 1, dte2.real + 1, dte2.real, dte2.real))

        # index from start read gradient to the end of it
        self.read = np.nonzero(grx_read)[0]

        # 3d gradient
        #self.gr = np.concatenate((grx * self.xMaxGradient, gry * self.yMaxGradient, np.zeros(grx.size))).reshape(3, grx.size)
        self.gr = np.concatenate((grx * self.xMaxGradient, np.zeros(grx.size), np.zeros(grx.size))).reshape(3, grx.size)
        self.tp = np.arange(0, self.rf.size) * self.dt
