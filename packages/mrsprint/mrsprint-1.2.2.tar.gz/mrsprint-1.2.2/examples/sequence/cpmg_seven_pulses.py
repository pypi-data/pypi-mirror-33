#! python
# -*- coding: utf-8 -*-

"""CPMG with seven pulses.

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
        opts['name'] = 'CPMG seven pulses'
        opts['type'] = 'bool'
        opts['value'] = True
        pt.parameterTypes.GroupParameter.__init__(self, **opts)

        # Sequence parameters
        self.te = self.addChild({'name': 'Time to echo', 'type': 'float', 'value': 0.1, 'suffix': 's', 'limits': (0, 100), 'siPrefix': True})
        self.te.sigValueChanged.connect(self.setSequence)

        self.dt = settings.simulator_group.timeResolution.value()
        self.b1_max = settings.rf_group.amMaxValue.value()
        self.gamma = nucleus.gamma.value()

        self.rf = None
        self.gr = None
        self.tp = None

        self.setSequence()

    def sequenceAction(self):
        """
        Generates a CPMG sequence.
        """

        mode = 2
        freq_shift = 256.
        freq_step = 64.
        freq_offset = 0.
        t1 = 1.
        t2 = .100

        _logger.debug("in %s", locals())

        # position setup
        position = create_positions(size=(20, 1, 1), step=(2, 1, 1), offset=(0, 0, 0))
        # frequency and t2 star setup
        freq_shift = frequency_shift(freq_shift, freq_step, offset=freq_offset)
        t2star = calculate_t2_star(t2, freq_shift)

        # calculate magnetization, m0 is mz = 1, mx = my = 0
        mx, my, mz = evolve(self.rf, self.gr, DT, t1, t2, freq_shift, position, mode)
        plotEverything(mx, my, mz, self.gr, self.rf, freq_shift, position)

    def setSequence(self):
        """Creates two np.array to contain both RF data and Gradient data."""
        # pulse of 90 degrees in x
        p90x = square_rf_pulse(self.dt, self.gamma, self.b1_max, 90, 0)
        tp90 = rf_duration(p90x, self.dt)

        # pulse of 180 degrees in y
        p180y = square_rf_pulse(self.dt, self.gamma, self.b1_max, 180, 90)
        tp180 = rf_duration(p180y, self.dt)

        # delay bewteen pulse 90x and 180y  = te/2 between pulse centers
        d90_180 = rf_delay(-tp90 / 2. + self.te.value() / 2. - tp180 / 2., self.dt)
        
        # delay bewteen pulse 180y and 180y  = te between pulse centers
        d180_180 = rf_delay(-tp180 / 2. + self.te.value() - tp180 / 2., self.dt)

        # rf for CPMG sequence composed
        self.rf = np.concatenate((np.zeros(500),
                                  p90x, d90_180,
                                  -p180y, d180_180,
                                  p180y, d180_180,
                                  -p180y, d180_180,
                                  p180y, d180_180,
                                  -p180y, d180_180,
                                  p180y, d180_180))

        # gradients for CMPG = 0
        self.gr = np.zeros((3, self.rf.size))
        self.read = np.zeros((3, self.rf.size))[0]
        self.tp = np.arange(0, self.rf.size) * self.dt
