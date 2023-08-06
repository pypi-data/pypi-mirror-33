#! python
# -*- coding: utf-8 -*-

"""Module for radiofrequency related classes and functions.

Authors:
    * Victor Hugo de Mello Pessoa <victor.pessoa@usp.br>
    * Daniel Cosmo Pizetta <daniel.pizetta@usp.br>

Since:
    2017/07/01

"""


import logging

import numpy as np
import pyqtgraph.parametertree as pt
from mrsprint.simulator import transform_pol_to_cart

_logger = logging.getLogger(__name__)


class RF(pt.parameterTypes.GroupParameter):
    """Class that represents the RF parameters in the system."""

    def __init__(self, **opts):
        opts['name'] = 'RF System'
        opts['type'] = 'bool'
        opts['value'] = True
        pt.parameterTypes.GroupParameter.__init__(self, **opts)
        # RF AM
        self.amMaxValue = self.addChild({'name': 'AM Max Value', 'type': 'float', 'value': 0.3, 'suffix': 'G', 'siPrefix': True})
        self.amMinRiseTime = self.addChild({'name': 'AM Min Rise Time', 'type': 'float', 'value': 0., 'suffix': 's', 'siPrefix': True})
        # RF PM
        self.pmMaxValue = self.addChild({'name': 'PM Max Value', 'type': 'float', 'value': 20, 'suffix': 'G/cm', 'siPrefix': True})
        self.pmMinRiseTime = self.addChild({'name': 'PM Min Rise Time', 'type': 'float', 'value': 0., 'suffix': 's', 'siPrefix': True})
        # RF FM
        self.fmMaxValue = self.addChild({'name': 'FM Max Value', 'type': 'float', 'value': 20, 'suffix': 'G/cm', 'siPrefix': True})
        self.fmMinRiseTime = self.addChild({'name': 'FM Min Rise Time', 'type': 'float', 'value': 0., 'suffix': 's', 'siPrefix': True})


def rf_duration(rf_event, dt):
    """Return the duration of the rf event (array) based on the number of the points and  dt.

    Args:
        rf_event (np.array): An array of event.
        dt (float [s]): Value of time resolution.

    Returns:
        float [s]: duration of the event.

    Todo:
        Regard the dimensions of the array.

    """
    # rf is a complex array, so just get the size of first dimension
    size = rf_event.size
    return size * dt


def rf_delay(duration, dt):
    """Generate a delay of rf pulse.

    Args:
        duration (float [s]): Delay time.
        dt (float [s]): Time resolution.

    Returns:
        np.array(complex): Rf delay - a zero am, pm, fm components in complex format.

    """
    am = np.zeros(0)
    pm = np.zeros(0)
    pulse_units = int(duration / dt)
    pm = np.append(pm, np.zeros(pulse_units))
    am = np.append(am, np.zeros(pulse_units))
    x, y = transform_pol_to_cart(am, pm)

    return x + 1.0j * y


def square_rf_pulse(dt, gamma, b1_max, flip_angle=90, phase=0., degrees=True):
    """Generate a hard rf pulse with a specific and constant flip angle and phase.

    Args:
        dt (float [s]): Value of time resolution.
        gamma (float [rad/(G*s)]): Gyromagnetic ratio of the excited nuclei.
        b1_max (float [G]): Max RF amplitude.
        flip_angle (float [degrees, radians]): Array of flip angle for rf pulse in degrees (if degrees = True).
        phase (float [degrees, radians]): Array of phase angle for rf pulse in degrees (if degrees = True).
        degrees (bool): Inform if the input is in degrees or radians.

    Returns:
        np.array(complex): A square rf pulse in imaginary form.

    """
    if degrees:
        flip_angle = np.deg2rad(flip_angle)
        phase = np.deg2rad(phase)

    am = np.zeros(0)
    pm = np.zeros(0)

    pulse_time = flip_angle / (gamma * b1_max)
    pulse_units = int(pulse_time / dt)
    pm = np.append(pm, np.ones(pulse_units) * phase)
    am = np.append(am, np.ones(pulse_units) * b1_max)
    x, y = transform_pol_to_cart(am, pm)

    return x + 1.0j * y
