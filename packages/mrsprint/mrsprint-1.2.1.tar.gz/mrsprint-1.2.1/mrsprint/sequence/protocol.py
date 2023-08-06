#! python
# -*- coding: utf-8 -*-

"""Module for organize and group the information required by an MR experiment.

Authors:
    * Victor Hugo de Mello Pessoa <victor.pessoa@usp.br>
    * Daniel Cosmo Pizetta <daniel.pizetta@usp.br>

Since:
    2017/07/01

"""

import logging

import pyqtgraph.parametertree as pt

from mrsprint.simulator import plot, simulator
from mrsprint.sequence import processing, sequence
from mrsprint.system import gradient, magnet, nucleus, rf

_logger = logging.getLogger(__name__)


class Protocol(object):
    """Class that sets up everything to run an experiment."""

    def __init__(self):
        self.name = 'Protocol Name'
        self.description = 'A long description of this protocol'
        # sets up the system, where there is no plot
        self.system.magnet = magnet.Magnet(self)
        self.system.nucleus = nucleus.Nucleus(self)
        self.system.gradient = gradient.Gradient(self)
        self.system.rf = rf.RF(self)
        # sets up the sequence and its plot
        self.sequence = sequence.Sequence(self)
        self.sequencePlot = plot.SequencePlot(self)
        # sets up the simulator and its plot
        self.simulator = simulator.Simulator(self)
        self.simulatorPlot = plot.SimulatorPlot(self)
        # sets up the processing and its plot
        self.processing = processing.Processing(self)
        self.processingPlot = plot.ProcessingPlot(self)

    def readProtocol(self):
        """Reads the parameters to run an experiment.

        It must have at least sequence parameters the other ones can
        be default.

        """
        # load parameters and call calculate.
        self.valid = True

    def writeProtocol(self):
        """Writes the parameters into the procotol file."""

    def runExperiment(self):
        """Executes a list of procedures to run an experiment."""
        if self.valid:
            time, memory = self.simulator.calculateEffort()
            # if less then 100 seconds
            if time_to_run <= 100:
                _logger.info("Effort is OK, not wasting your time.")
                _logger.info("Effort is minimal, take a break now.")
                _logger.info("Effort is appreciable, did you take your coffee?")
                _logger.warning("Effort is not so big, have a sit and eat some cookies.")
                _logger.warning("Effort is big, I'll see you tomorrow.")
                _logger.error("Effort is tremenduous, let's by a new computer, no chance in this one, sorry.")
