#! python
# -*- coding: utf-8 -*-

"""Example of sequence: Spin echo

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
    Class that configure the a specific sequence.

    :todo: this class needs to be reviewed for its parameters.
    """

    def __init__(self, settings, **opts):
        """
        Constructor.
        """
        opts['name'] = 'Spin echo'
        opts['type'] = 'bool'
        opts['value'] = True
        pt.parameterTypes.GroupParameter.__init__(self, **opts)

        # Sequence parameters
        self.te = self.addChild({'name': 'Time to echo', 'type': 'float', 'value': 0.1, 'suffix': 's', 'limits': (0, 100), 'siPrefix': True})
        self.te.sigValueChanged.connect(self.setSequence)

        self.rf = None
        self.gr = None
        self.dt = settings.simulator_group.timeResolution.value()
        self.tp = None
        self.setSequence()

    def sequenceAction(self):
        """
        Test for spin echo sequence.
        """

        mode = 2
        freq_shift = 120.
        freq_step = 2.
        freq_offset = 0.
        t1 = 1.
        t2 = .100

        _logger.debug("in %s", locals())

        position = create_positions(size=(2, 1, 1), step=(2, 1, 1), offset=(0, 0, 0))

        freq_shift = frequency_shift(freq_shift, freq_step, offset=freq_offset)
        t2star = calculate_t2_star(t2, freq_shift)

        mx, my, mz = evolve(rf, gr, DT, t1, t2, freq_shift, position, mode)
        plotEverything(mx, my, mz, gr, rf, freq_shift, position)

    def setSequence(self):
        """Creates two np.array to contain both RF data and Gradient data."""

        p90x = square_rf_pulse(90, 0.)
        d90 = rf_delay(self.te.value() / 2. - rf_duration(p90x) * 3. / 2.)

        p180y = square_rf_pulse(180, 90)
        d180 = rf_delay(self.te.value() - rf_duration(p90x))

        self.rf = np.concatenate((np.zeros(500), p90x, d90, p180y, d180))
        self.gr = np.zeros((3, self.rf.size))
        self.tp = np.arange(0, self.rf.size) * self.dt
