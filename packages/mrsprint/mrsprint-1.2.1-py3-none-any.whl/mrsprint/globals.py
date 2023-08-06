#! python
# -*- coding: utf-8 -*-

"""Global values.

Authors:
    * Victor Hugo de Mello Pessoa <victor.pessoa@usp.br>
    * Daniel Cosmo Pizetta <daniel.pizetta@usp.br>

Since:
    2015/06/01

"""


import logging

import numpy

_logger = logging.getLogger(__name__)

TWO_PI = 2. * numpy.pi                     # [rad]
HALF_PI = numpy.pi / 2.                    # [rad]
CM_HZ = 0.01 / 1.                          # [cm/Hz]

GAMMA = 26752.219                          # [rad/(G*s)] COTADA 2016

GR_MIN = TWO_PI / GAMMA * CM_HZ            # [G/cm] min gradient
GR_MAX = 12                                # [G/cm] max gradient
SR_MAX = 4                                 # [(G/cm)/s] max gradient slew rate

B1_MAX = 0.3                               # [G] max RF amplitude
P90_DURATION = HALF_PI / (GAMMA * B1_MAX)  # [s] duration of 90 deg pulse
P90_POINTS = 64                            # [#] number of points in 90 deg pulse


# index for animation loop
index = 0
# index step for reduction of the frames to increase speed
index_step = 5

AMLN = (255, 255, 255)
PMLN = (255, 255, 255)
FMLN = (255, 255, 255)

XLN = (76, 217, 100)
YLN = (255, 204, 0)
ZLN = (255, 45, 85)
XYLN = (166, 211, 50)

AMFL = (255, 255, 255)
PMFL = (255, 255, 255)
FMFL = (255, 255, 255)

XFL = (76, 217, 100)
YFL = (255, 204, 0)
ZFL = (255, 45, 85)
XYFL = (166, 211, 50)

# timeline
TLLN = (255, 255, 255)

_logger.info("GAMMA: ", GAMMA)
_logger.info("B1_MAX: ", B1_MAX)
_logger.info("GR_MAX: ", GR_MAX)
_logger.info("P90_DURATION: ", P90_DURATION)
