#! python
# -*- coding: utf-8 -*-

"""Simple 90x pulse, FID.

Authors:
    * Daniel Cosmo Pizetta <daniel.pizetta@usp.br>
    * Victor Hugo de Mello Pessoa <victor.pessoa@usp.br>

Since:
    2017/03/08


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
    """Class that configures the a specific sequence."""

    def __init__(self, settings, nucleus, **opts):
        """
        Constructor.
        """
        opts['name'] = 'Simple FID'
        opts['type'] = 'bool'
        opts['value'] = True
        pt.parameterTypes.GroupParameter.__init__(self, **opts)

        # Sequence parameters
        self.flipAngle = self.addChild({'name': 'Flip Angle', 'type': 'float', 'value':90, 'suffix': 'deg', 'limits': (0, 360), 'siPrefix': True})
        self.flipAngle.sigValueChanged.connect(self.setSequence)

        self.delay = self.addChild({'name': 'Delay', 'type': 'float', 'value':0.5, 'suffix': 's', 'limits': (0.01, 2), 'siPrefix': True})
        self.delay.sigValueChanged.connect(self.setSequence)

        self.dt = settings.simulator_group.timeResolution.value()
        self.b1_max = settings.rf_group.amMaxValue.value()
        self.gamma = nucleus.gamma.value()

        self.rf = None
        self.gr = None
        self.tp = None

        self.setSequence()

    def sequenceAction(self):
        """
        Simple free induction decay (FID).

        Just rf and gradient are essential for the fid code.

        Todo:
            - May accept the constants as parameters.
            - May return parameters for bloch.evolve().
        """

        mode = 2           # [#]
        freq_shift = 250.  # [Hz]
        freq_step = 2.     # [Hz]
        freq_offset = 0.   # [Hz]
        t1 = 0.5           # [s]
        t2 = .01           # [s]

        _logger.debug("in %s", locals())

        # position setup
        position = create_positions(size=(2, 1, 1), step=(2, 1, 1), offset=(0, 0, 0))
        # frequency and t2 star setup
        freq_shift = frequency_shift(freq_shift, freq_step, offset=freq_offset)
        t2star = calculate_t2_star(t2, freq_shift)

        mx, my, mz = evolve(rf, gr, DT, t1, t2, freq_shift, position, mode)
        plotEverything(mx, my, mz, gr, rf, freq_shift, position)

    def setSequence(self):
        """Creates two np.array to contain both RF data and Gradient data."""
        # rf setup
        p90x = square_rf_pulse(self.dt, self.gamma, self.b1_max, self.flipAngle.value(), 0)
        dte = rf_delay(self.delay.value(), self.dt)
        self.rf = np.concatenate((p90x, dte))
        # gradient setup
        self.gr = np.zeros((3, self.rf.size))
        self.tp = np.arange(0, self.rf.size) * self.dt
