#! python
# -*- coding: utf-8 -*-

"""Module for gradient related classes and functions.

Authors:
    * Victor Hugo de Mello Pessoa <victor.pessoa@usp.br>
    * Daniel Cosmo Pizetta <daniel.pizetta@usp.br>

Since:
    2017/07/01

Todo:
    Change nameOfFunctions to name_of_functions.

"""

import logging

import numpy as np
import pyqtgraph.parametertree as pt

_logger = logging.getLogger(__name__)


class Gradient(pt.parameterTypes.GroupParameter):
    """Class that represents the gradients parameters in the sistem."""

    def __init__(self, **opts):
        opts['name'] = 'Gradient System'
        opts['type'] = 'bool'
        opts['value'] = True
        pt.parameterTypes.GroupParameter.__init__(self, **opts)
        # gradient x
        self.xMaxValue = self.addChild({'name': 'X Max Value', 'type': 'float', 'value': 20, 'suffix': 'G/cm', 'siPrefix': True})
        self.xMinRiseTime = self.addChild({'name': 'X Min Rise Time', 'type': 'float', 'value': 0., 'suffix': 's', 'siPrefix': True})
        # gradient y
        self.yMaxValue = self.addChild({'name': 'Y Max Value', 'type': 'float', 'value': 20, 'suffix': 'G/cm', 'siPrefix': True})
        self.yMinRiseTime = self.addChild({'name': 'Y Min Rise Time', 'type': 'float', 'value': 0., 'suffix': 's', 'siPrefix': True})
        # gradient z
        self.zMaxValue = self.addChild({'name': 'Z Max Value', 'type': 'float', 'value': 20, 'suffix': 'G/cm', 'siPrefix': True})
        self.zMinRiseTime = self.addChild({'name': 'Z Min Rise Time', 'type': 'float', 'value': 0., 'suffix': 's', 'siPrefix': True})


def gradient_duration(gradient_event, dt):
    """Return the duration of the gradient event (array).

    It is based on the size and dt.

    Args:
        gradient_event (np.array): An array of event.
        dt (float [s]): Value of time resolution.

    Return:
        float [s]: Duration of the event.

    Todo:
        Regard the dimensions of the array.

    """
    # get the second dimension size, the first one is 3
    # because of grad x, y and z
    size = gradient_event.shape[1]
    return size * dt


def gradient_delay(duration, dt, number_of_points=0):
    """Generate a delay of gradient pulse.

    Args:
        duration (float [s]): Delay time.
        dt (float [s]): Time resolution.
        number_of_points (int): Number of points.

    Returns:
        np.array: Gradient delay - a zero x, y and z gradient components

    """
    grad = np.zeros(number_of_points)
    pulse_units = int(duration / dt)
    grad = np.append(grad, np.zeros(pulse_units * 3).reshape(3, pulse_units))

    return grad
