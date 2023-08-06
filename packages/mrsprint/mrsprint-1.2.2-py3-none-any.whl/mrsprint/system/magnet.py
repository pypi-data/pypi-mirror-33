#! python
# -*- coding: utf-8 -*-

"""Module for magnet related classes and functions.

Authors:
    * Victor Hugo de Mello Pessoa <victor.pessoa@usp.br>
    * Daniel Cosmo Pizetta <daniel.pizetta@usp.br>

Since:
    2017/07/01

Todo:
    Maybe put all config together in magnet classes.

"""

import logging

import pyqtgraph.parametertree as pt

_logger = logging.getLogger(__name__)


class MagnetConfig(pt.parameterTypes.GroupParameter):
    """Class that configure the limit parameters of the magnet."""

    def __init__(self, **opts):
        opts['name'] = 'Magnet Config'
        opts['type'] = 'bool'
        opts['value'] = True
        pt.parameterTypes.GroupParameter.__init__(self, **opts)

        # Strength
        self.maxMagneticStrength = self.addChild({'name': 'Magnetic Strength Limit', 'type': 'float', 'value': 5, 'suffix': 'T', 'siPrefix': True, 'limits': (0., 20.)})

        # Size
        self.limitSizeX = self.addChild({'name': 'Size X Limit', 'type': 'float', 'value': 100.0, 'suffix': ' cm', 'limits': (0., 100.)})
        self.SizeX = self.addChild({'name': 'Size X Default', 'type': 'float', 'value': 20.0, 'suffix': ' cm', 'limits': (0., 100.)})
        self.limitSizeY = self.addChild({'name': 'Size Y Limit', 'type': 'float', 'value': 100.0, 'suffix': ' cm', 'limits': (0., 100.)})
        self.SizeY = self.addChild({'name': 'Size Y Default', 'type': 'float', 'value': 20.0, 'suffix': ' cm', 'limits': (0., 100.)})
        self.limitSizeZ = self.addChild({'name': 'Size Z Limit', 'type': 'float', 'value': 100.0, 'suffix': ' cm', 'limits': (0., 100.)})
        self.SizeZ = self.addChild({'name': 'Size Z Default', 'type': 'float', 'value': 60.0, 'suffix': ' cm', 'limits': (0., 100.)})

        # Inhomogeneity B0x, B0y and B0z, limits and default
        self.limitB0x = self.addChild({'name': 'B0x Limit', 'type': 'float', 'value': 10., 'step': 1, 'limits': (0, 100), 'suffix': ' mT', 'siPrefix': True})
        self.B0x = self.addChild({'name': 'B0x Default', 'type': 'float', 'value': 0., 'step': 1, 'limits': (-100, 100), 'suffix': ' mT', 'siPrefix': True})

        self.limitB0y = self.addChild({'name': 'B0y Limit', 'type': 'float', 'value': 10., 'step': 1, 'limits': (0, 100), 'suffix': ' mT', 'siPrefix': True})
        self.B0y = self.addChild({'name': 'B0y Default', 'type': 'float', 'value': 0., 'step': 1, 'limits': (-100, 100), 'suffix': ' mT', 'siPrefix': True})

        self.limitB0z = self.addChild({'name': 'B0z Limit', 'type': 'float', 'value': 10., 'step': 1, 'limits': (0, 100), 'suffix': ' mT', 'siPrefix': True})
        self.B0z = self.addChild({'name': 'B0z Default', 'type': 'float', 'value': 0., 'step': 1, 'limits': (-100, 100), 'suffix': ' mT', 'siPrefix': True})


class Magnet(pt.parameterTypes.GroupParameter):
    """Class that represents the parameters in the magnet.

    Args:
        magnet_config (MagnetConfig): An object that represents the limits to this magnet.

    """

    def __init__(self, magnet_config, **opts):
        opts['name'] = 'Magnet'
        opts['type'] = 'bool'
        opts['value'] = True
        pt.parameterTypes.GroupParameter.__init__(self, **opts)

        # Strength
        self.magneticStrength = self.addChild({'name': 'Magnetic Strength', 'type': 'float', 'value': 3,
                                               'suffix': 'T', 'siPrefix': True})
        self.magneticStrength.setLimits((0., magnet_config.maxMagneticStrength.value()))

        # Carrier frequency, it depends on nucleus set in RF
        self.carrierFrequency = self.addChild({'name': 'Carrier Frequency', 'type': 'float', 'value': 127.728,
                                               'suffix': 'MHz', 'siPrefix': True, 'readonly': True})

        # Number of points in each direction
        self.resolution = self.addChild({'name': 'Resolution', 'values': [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024],
                                         'value': 2, 'type': 'list'})

        # B0x, B0y and B0z inhomogeneity
        self.B0x = self.addChild({'name': 'Inhomogeneity X', 'type': 'float', 'value': 0.,
                                  'step': 1, 'limits': (-100, 100), 'suffix': ' mT', 'siPrefix': True})
        self.B0x.setValue(magnet_config.B0x.value())
        self.B0x.setLimits((- magnet_config.limitB0x.value(), magnet_config.limitB0x.value()))

        self.B0y = self.addChild({'name': 'Inhomogeneity Y', 'type': 'float', 'value': 0.,
                                  'step': 1, 'limits': (-100, 100), 'suffix': ' mT', 'siPrefix': True})
        self.B0y.setValue(magnet_config.B0y.value())
        self.B0y.setLimits((- magnet_config.limitB0y.value(), magnet_config.limitB0y.value()))

        self.B0z = self.addChild({'name': 'Inhomogeneity Z', 'type': 'float', 'value': 0.,
                                  'step': 1, 'limits': (-100, 100), 'suffix': ' mT', 'siPrefix': True})
        self.B0z.setValue(magnet_config.B0z.value())
        self.B0z.setLimits((- magnet_config.limitB0z.value(), magnet_config.limitB0z.value()))