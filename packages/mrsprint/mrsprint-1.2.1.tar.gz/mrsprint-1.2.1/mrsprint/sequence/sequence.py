#! python
# -*- coding: utf-8 -*-


"""Module for pulse sequence related classes and functions.

Authors:
    * Victor Hugo de Mello Pessoa <victor.pessoa@usp.br>
    * Daniel Cosmo Pizetta <daniel.pizetta@usp.br>

Since:
    2017/07/01

"""

import logging

import numpy as np
import pyqtgraph.parametertree as pt

from mrsprint.system import gradient, rf

_logger = logging.getLogger(__name__)


class Sequence(pt.parameterTypes.GroupParameter):
    """Class that represents a sequence for magnetic resonance systems."""

    def __init__(self, settings, nucleus, **opts):
        opts['name'] = 'Sequence'
        opts['type'] = 'bool'
        opts['value'] = True
        pt.parameterTypes.GroupParameter.__init__(self, **opts)

        # Main constant values
        self.dt = settings.simulator_group.timeResolution.value()
        self.b1_max = settings.rf_group.amMaxValue.value()
        self.gamma = nucleus.gamma.value()

        self.__rf = rf.rf_delay(self.dt, self.dt)
        self.__gradient = gradient.gradient_delay(self.dt, self.dt)

    def setRF(self, rf_value):
        """Properly sets the rf stream signal."""
        for rep_num, events in rf_value:
            for _ in np.arange(0, rep_num):
                for event in events:
                    self.__rf = np.append(self.__rf, event)

    def getRF(self):
        """Return the entire rf."""
        return self.__rf

    def setGradient(self, grad_value):
        """Properly sets the gradient."""
        for rep_num, events in gradient_value:
            for _ in np.arange(0, rep_num):
                for event in events:
                    self.__gradient = np.append(self.__gradient, event)

    def getGradient(self):
        """Return the entire gradient."""
        rf_shape = self.__rf.shape
        gradient_size = self.__gradient.size

        grad_zero = np.zeros(3 * (rf_shape[0])).reshape(3, rf_shape[0])

        if 3 * rf_shape[0] != gradient_size:
            if gradient_size <= 3:
                self.__gradient = grad_zero
            else:
                raise ValueError("RF and Gradient must have the same temporal size!")
        return self.__gradient


class CPMGSequence(Sequence):
    """Generates a CPMG sequence."""

    def __init__(self):
        Sequence.__init__(self)
        # sequence specific parameters

        self.numberOfCycles = self.addChild({'name': 'Number of Cycles', 'type': 'int', 'value': 3})
        self.te = self.addChild({'name': 'Time to Echo', 'type': 'float', 'value': 0.02, 'suffix': 's', 'siPrefix': True})
        self.dtr = self.addChild({'name': 'Delay TR', 'type': 'float', 'value': 0.02, 'suffix': 's', 'siPrefix': True})

        # pulse of 90 degrees in x
        rf_90_x = rf.square_rf_pulse(flip_angle=90, phase=0)
        t_half_rf_90 = rf.rf_duration(rf_90_x) / 2.
        # pulse of 180 degrees in y
        rf_180_y = rf.square_rf_pulse(flip_angle=180, phase=90)
        t_half_rf_180 = rf.rf_duration(rf_180_y) / 2.

        # delay between pulse 90x and 180y  = te/2 between pulse centers
        d_90_180 = rf.rf_delay(-t_half_rf_90 + self.te.value() / 2. - t_half_rf_180)
        # delay between pulse 180y and 180y  = te between pulse centers
        d_180_180 = rf.rf_delay(-t_half_rf_180 + self.te.value() - t_half_rf_180)
        # delay repetition time before restart
        d_tr = rf.rf_delay(self.dtr.value())

        # rf for CPMG
        self.setRF([(1, [rf_90_x, d_90_180]),
                    (self.numberOfCycles.value(), [-rf_180_y, d_180_180, rf_180_y, d_180_180]),
                    (1, [d_tr])])


class GradientEchoSequence(Sequence):
    """Generate a Gradient Echo sequence."""

    def __init__(self):
        Sequence.__init__(self)
        # sequence specific parameters
        self.a90 = self.addChild({'name': 'Delay After RF', 'type': 'float', 'value': 0.01, 'suffix': 's', 'siPrefix': True})
        self.te = self.addChild({'name': 'Time to Echo', 'type': 'float', 'value': 0.02, 'suffix': 's', 'siPrefix': True})
        self.dtr = self.addChild({'name': 'Delay TR', 'type': 'float', 'value': 0.01, 'suffix': 's', 'siPrefix': True})

        # first event, excitation
        rf_90_x = rf.square_rf_pulse(flip_angle=90, phase=0)
        t_rf_90 = rf.rf_duration(rf_90_x)
        d_gr_90 = gradient.gradient_delay(t_rf_90)

        # second event, a delay
        d_rf_a90 = rf.rf_delay(self.dbgr.value())
        d_gr_a90 = gradient.gradient_delay(self.dbgr.value())

        # third event, dephasing
        d_rf_deph = rf.rf_delay()
        gr_deph = gradient.SquareGradient()

        # fourth event, read
        d_rf_read = rf.rf_delay()
        gr_read = gradient.SquareGradient()

        # fifty event, a delay
        d_rf_tr = rf.rf_delay(self.dtr.value())
        d_gr_tr = gradient.gradient_delay(self.dtr.value())

        self.setRF([(1, [rf_90_x, d_rf_a90, d_rf_deph, d_rf_read, d_rf_tr])])
        self.setGradient([(1, [d_gr_90, d_gr_a90, gr_deph, gr_read, d_gr_tr])])
