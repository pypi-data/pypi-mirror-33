#! python
# -*- coding: utf-8 -*-

"""Module for simulate the response of the sample to the magnetic signal related classes and functions.

Authors:
    * Victor Hugo de Mello Pessoa <victor.pessoa@usp.br>
    * Daniel Cosmo Pizetta <daniel.pizetta@usp.br>

Since:
    2017/07/01

"""


import logging

import pyqtgraph.parametertree as pt

_logger = logging.getLogger(__name__)


class Simulator(pt.parameterTypes.GroupParameter):
    """Class that represents the simulator."""

    def __init__(self, **opts):
        opts['name'] = 'Simulator'
        opts['type'] = 'bool'
        opts['value'] = True
        pt.parameterTypes.GroupParameter.__init__(self, **opts)

        # modes
        self.magnetizationMode = self.addChild({'name': 'Magnetization Mode', 'type': 'list',
                                                'values': ['From Start', 'Steady State'], 'value': 'From Start'})
        self.timeMode = self.addChild({'name': 'Time Mode', 'type': 'list', 'values': ['All Points', 'End Points'],
                                       'value': 'All Points'})

        # resolution
        self.pointsResolution = self.addChild({'name': 'Points of Resolution (p90x)', 'type': 'int', 'value': 128})
        self.timeResolution = self.addChild({'name': 'Time Resolution (p90x)', 'type': 'float', 'value': 1e-6,
                                             'suffix': 's', 'siPrefix': True})

        # display
        self.show3DAxes = self.addChild({'name': 'Show Axes', 'type': 'bool', 'value': True})
        self.show3DGrid = self.addChild({'name': 'Show Grid', 'type': 'bool', 'value': True})
        self.showSample = self.addChild({'name': 'Show Sample', 'type': 'bool', 'value': False})
        self.showMagnet = self.addChild({'name': 'Show Magnet', 'type': 'bool', 'value': False})

        # display
        self.plot3DGrad = self.addChild({'name': 'Show Gradient Lines', 'type': 'bool', 'value': True})
        self.plot3DOffResMag = self.addChild({'name': 'Off Resonance Magnetization', 'type': 'bool', 'value': True})
        self.plot3DOffResPercentage = self.addChild({'name': 'Off Resonance Magnetization Percentage', 'type': 'float',
                                                     'value': 10.0, 'suffix': '%', 'limits': (0, 100)})
        self.plot3DTotalMag = self.addChild({'name': 'Show Total Magnetization', 'type': 'bool', 'value': True})
        self.plot3DTotalMagZero = self.addChild({'name': 'Show Initial Magnetization', 'type': 'bool', 'value': True})
