#! python
# -*- coding: utf-8 -*-

"""Module for sample related classes and functions.

Authors:
    * Victor Hugo de Mello Pessoa <victor.pessoa@usp.br>
    * Daniel Cosmo Pizetta <daniel.pizetta@usp.br>

Since:
    2017/07/01

"""


import logging

import pyqtgraph.parametertree as pt

_logger = logging.getLogger(__name__)


class SampleConfig(pt.parameterTypes.GroupParameter):
    """Class that configure the limit parameters of each sample.

    Todo:
        This class needs to be reviewed for its parameters.

    """

    def __init__(self, **opts):
        opts['name'] = 'Sample Config'
        opts['type'] = 'bool'
        opts['value'] = True
        pt.parameterTypes.GroupParameter.__init__(self, **opts)

        # Sample size
        self.maxSizeX = self.addChild({'name': 'Size X Max', 'type': 'float', 'value': 50.0, 'suffix': ' cm', 'limits': (1, 100)})
        self.SizeX = self.addChild({'name': 'Size X Default', 'type': 'float', 'value': 10.0, 'suffix': ' cm', 'limits': (1, 100)})
        self.maxSizeY = self.addChild({'name': 'Size Y Max', 'type': 'float', 'value': 50.0, 'suffix': ' cm', 'limits': (1, 100)})
        self.SizeY = self.addChild({'name': 'Size Y Default', 'type': 'float', 'value': 10.0, 'suffix': ' cm', 'limits': (1, 100)})
        self.maxSizeZ = self.addChild({'name': 'Size Z Max', 'type': 'float', 'value': 50.0, 'suffix': ' cm', 'limits': (1, 100)})
        self.SizeZ = self.addChild({'name': 'Size Z Default', 'type': 'float', 'value': 10.0, 'suffix': ' cm', 'limits': (1, 100)})

        # Number of points
        self.Nx = self.addChild({'name': 'Nx Default', 'type': 'int', 'value': 2, 'step': 1, 'limits': (1, 2048)})
        self.Ny = self.addChild({'name': 'Ny Default', 'type': 'int', 'value': 2, 'step': 1, 'limits': (1, 2048)})
        self.Nz = self.addChild({'name': 'Nz Default', 'type': 'int', 'value': 2, 'step': 1, 'limits': (1, 2048)})
        self.maxN = self.addChild({'name': 'Max Number of points', 'type': 'int', 'value': 1024, 'step': 1, 'limits': (1, 2048)})


class Sample(pt.parameterTypes.GroupParameter):
    """Class that represents the parameters of each sample.

    Args:
        sample_config (SampleConfig): An object that represents the limits to this sample.

    Todo:
        This class needs to be reviewed for its parameters.

    """

    def __init__(self, sample_config, **opts):
        opts['name'] = 'Sample'
        opts['type'] = 'bool'
        opts['value'] = True
        pt.parameterTypes.GroupParameter.__init__(self, **opts)

        # Sample size
        self.SizeX = self.addChild({'name': 'Size X', 'type': 'float', 'value': 10.0, 'suffix': ' cm'})
        self.SizeX.setValue(sample_config.SizeX.value())
        self.SizeX.setLimits((1, sample_config.maxSizeX.value()))

        self.SizeY = self.addChild({'name': 'Size Y', 'type': 'float', 'value': 10.0, 'suffix': ' cm'})
        self.SizeY.setValue(sample_config.SizeY.value())
        self.SizeY.setLimits((1, sample_config.maxSizeY.value()))

        self.SizeZ = self.addChild({'name': 'Size Z', 'type': 'float', 'value': 10.0, 'suffix': ' cm'})
        self.SizeZ.setValue(sample_config.SizeZ.value())
        self.SizeZ.setLimits((1, sample_config.maxSizeZ.value()))

        # Number of points in each direction
        self.Nx = self.addChild({'name': 'Nx', 'value': 5, 'type': 'int'})
        self.Nx.setValue(sample_config.Nx.value())
        self.Nx.setLimits((1, sample_config.maxN.value()))

        self.Ny = self.addChild({'name': 'Ny', 'value': 5, 'type': 'int'})
        self.Ny.setValue(sample_config.Ny.value())
        self.Ny.setLimits((1, sample_config.maxN.value()))

        self.Nz = self.addChild({'name': 'Nz', 'value': 5, 'type': 'int'})
        self.Nz.setValue(sample_config.Nz.value())
        self.Nz.setLimits((1, sample_config.maxN.value()))

        # Sample element size
        self.dX = self.addChild({'name': 'dX', 'type': 'float', 'value': 10.0, 'suffix': ' cm', 'readonly': True})
        self.dY = self.addChild({'name': 'dY', 'type': 'float', 'value': 10.0, 'suffix': ' cm', 'readonly': True})
        self.dZ = self.addChild({'name': 'dZ', 'type': 'float', 'value': 10.0, 'suffix': ' cm', 'readonly': True})

        # Connecting signals
        self.Nx.sigValueChanged.connect(self.dXUpdate)
        self.Ny.sigValueChanged.connect(self.dYUpdate)
        self.Nz.sigValueChanged.connect(self.dZUpdate)

        self.SizeX.sigValueChanged.connect(self.dXUpdate)
        self.SizeY.sigValueChanged.connect(self.dYUpdate)
        self.SizeZ.sigValueChanged.connect(self.dZUpdate)

    def dXUpdate(self):
        """Update the value for dX."""
        self.dX.setValue(self.SizeX.value() / self.Nx.value())

    def dYUpdate(self):
        """Update the value for dY."""
        self.dY.setValue(self.SizeY.value() / self.Ny.value())

    def dZUpdate(self):
        """Update the value for dZ."""
        self.dZ.setValue(self.SizeZ.value() / self.Nz.value())


class SampleElementConfig(pt.parameterTypes.GroupParameter):
    """Class that configure the limit parameters of each sample element.

    Todo:
        This class needs to be reviewed for its parameters.

    """

    def __init__(self, **opts):
        opts['name'] = 'Sample Element Config'
        opts['type'] = 'bool'
        opts['value'] = True
        pt.parameterTypes.GroupParameter.__init__(self, **opts)

        # T1 Limits and Default
        self.maxT1 = self.addChild({'name': 'T1 Max Value', 'type': 'float', 'value': 5., 'step': 1, 'limits': (0, 100), 'suffix': ' s', 'siPrefix': True})
        self.minT1 = self.addChild({'name': 'T1 Min Value', 'type': 'float', 'value': 0., 'step': 1, 'limits': (0, 100), 'suffix': ' s'})
        self.t1 = self.addChild({'name': 'T1 Default', 'type': 'float', 'value': 0.2, 'step': 1, 'limits': (0, 100), 'suffix': 's', 'siPrefix': True})

        # T2 Limits and Default
        self.maxT2 = self.addChild({'name': 'T2 Max Value', 'type': 'float', 'value': 5., 'step': 1, 'limits': (0, 100), 'suffix': ' s', 'siPrefix': True})
        self.minT2 = self.addChild({'name': 'T2 Min Value', 'type': 'float', 'value': 0., 'step': 1, 'limits': (0, 100), 'suffix': ' s'})
        self.t2 = self.addChild({'name': 'T2 Default', 'type': 'float', 'value': 0.3, 'step': 1, 'limits': (0, 100), 'suffix': 's', 'siPrefix': True})

        # Density of spins Limts and Default
        self.maxRho = self.addChild({'name': 'ρ Max Value', 'type': 'float', 'value': 1, 'step': 0.1, 'limits': (1, 100)})
        self.minRho = self.addChild({'name': 'ρ Min Value', 'type': 'float', 'value': 0, 'step': 0.1, 'limits': (0, 100)})
        self.rho = self.addChild({'name': 'ρ Default', 'type': 'float', 'value': 1, 'step': 0.01, 'limits': (0, 100)})


class SampleElement(pt.parameterTypes.GroupParameter):
    """Class that represents the parameters of each sample element.

    Args:
        sample_element_config (SampleElementConfig): An object that represents the limits to the sample elements.

    Todo:
        This class needs to be reviewed for its parameters.

    """

    def __init__(self, sample_element_config, **opts):
        opts['name'] = 'Sample Element'
        opts['type'] = 'bool'
        opts['value'] = True
        pt.parameterTypes.GroupParameter.__init__(self, **opts)

        # T1 and T2
        self.t1 = self.addChild({'name': 'T1', 'type': 'float', 'value': 5., 'step': 1, 'limits': (0, 100), 'suffix': ' s', 'siPrefix': True})
        self.t1.setValue(sample_element_config.t1.value())
        self.t1.setLimits((sample_element_config.minT1.value(), sample_element_config.maxT1.value()))

        self.t2 = self.addChild({'name': 'T2', 'type': 'float', 'value': 5., 'step': 1, 'limits': (0, 100), 'suffix': ' s', 'siPrefix': True})
        self.t2.setValue(sample_element_config.t2.value())
        self.t2.setLimits((sample_element_config.minT2.value(), sample_element_config.maxT2.value()))

        # Density of spins
        self.rho = self.addChild({'name': 'ρ', 'type': 'float', 'value': 1, 'step': 0.01, 'limits': (0, 100)})
        self.rho.setValue(sample_element_config.rho.value())
        self.rho.setLimits((sample_element_config.minRho.value(), sample_element_config.maxRho.value()))


class Nucleus(pt.parameterTypes.GroupParameter):
    """Class that represents the parameters in the nucleus."""

    def __init__(self, **opts):
        opts['name'] = 'Nucleus'
        opts['type'] = 'bool'
        opts['value'] = True
        pt.parameterTypes.GroupParameter.__init__(self, **opts)
        self.nucleus = self.addChild({'name': 'Nucleus', 'type': 'list', 'values': ['H', 'C', 'N', 'O'], 'value': 'H'})
        self.gamma = self.addChild({'name': 'Gamma', 'type': 'float', 'value': 26752.219, 'suffix': 'rad/(G.s)', 'siPrefix': True, 'readonly': True})
        self.updateGamma()

    def updateGamma(self):
        """Update the value for gamma if the nucleus is changed"""
        if self.nucleus.value() == 'H':
            self.gamma.setValue(26752.219)
        elif self.nucleus.value() == 'C':
            self.gamma.setValue(6726.150)
        elif self.nucleus.value() == 'N':
            self.gamma.setValue(1933.336)
        elif self.nucleus.value() == 'O':
            self.gamma.setValue(-3626.655)
