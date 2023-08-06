#! python
# -*- coding: utf-8 -*-

"""Example of sequence: Simple CPMG

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
    """Class that configures the a specific sequence.

    Todo:
        This class needs to be reviewed for its parameters.
    """

    def __init__(self, settings, **opts):
        opts['name'] = 'Simple CPMG'
        opts['type'] = 'bool'
        opts['value'] = True
        pt.parameterTypes.GroupParameter.__init__(self, **opts)

        seq = sequence.CPMGSequence()
        self.rf = seq.getRF()
        self.gr = seq.getGradient()
        self.dt = settings.simulator_group.timeResolution.value()
        self.tp = np.arange(0, self.rf.size) * self.dt

        def sequenceAction(self):
            """Simple Carr-Purcell-Meiboom-Gill (CPMG).
            It allows to measure transverse or spin-spin T2 relaxation times.
            """
            freq_shift = 120.
            freq_step = 2.
            freq_offset = 0.

            freq_shift = frequency_shift(freq_shift, freq_step, offset=freq_offset)
            t2star = calculate_t2_star(t2, freq_shift)
            p = Parameter.create(name='params', type='group', children=[seq])

            print("T1:", t1)
            print("T2: ", t2)
            print("T2*: ", t2star)
            print("freq_shift.shape: ", freq_shift.shape)
            print("gr.shape: ", self.gr.shape)
            print("rf.shape: ", self.rf.shape)

            # position 3D array
            position = create_positions(size=(20, 1, 1), step=(2, 1, 1), offset=(0, 0, 0))
            # calculate magnetization, m0 is mz = 1, mx = my = 0
            mx, my, mz = evolve(self.rf, self.gr, dt, t1, t2, freq_shift, position, mode)
            plotEverything(mx, my, mz, self.gr, self.rf, freq_shift, position, p)
