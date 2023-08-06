#! python
# -*- coding: utf-8 -*-

"""Package for simulator related classes and objects.

Authors:
    * Daniel Cosmo Pizetta <daniel.pizetta@usp.br>

Since:
    2018/06/07

Todo:
    Maybe remove old_plot module.

"""


import logging

import numpy as np

_logger = logging.getLogger(__name__)


def reduce_magnetization_in_frequency(mx, my, mz, freq_shift, fsa_size):
    """Reduces the magnetization vector by summing frequency components.

    Args:
        mx (np.array): Array of magnetization x without reduction in frequency.
        my (np.array): Array of magnetization y without reduction in frequency.
        mz (np.array): Array of magnetization z without reduction in frequency.
        freq_shift (np.array):  Array of frequency shift.
        fsa_size (int): Size of array of frequency shift.

    Returns:
        tuple: (mx, my, mz) arrays of magnetization reduced

    Todo:
        Shape size different of 2.
        Better solution for freq_shift array.
        Set physical unit for each args.

    """
    fsa_size = fsa_size - 1
    fsa_size_half = int(fsa_size / 2)

    if len(mx.shape) >= 2:
        mx_neg = np.sum(mx[:fsa_size_half], axis=0)
        mx_pos = np.sum(mx[fsa_size_half + 1:], axis=0)
        mx_f = mx_neg + mx_pos + mx[fsa_size_half]
    else:
        mx_f = mx

    if len(my.shape) >= 2:
        my_neg = np.sum(my[:fsa_size_half], axis=0)
        my_pos = np.sum(my[fsa_size_half + 1:], axis=0)
        my_f = my_neg + my_pos + my[fsa_size_half]
    else:
        my_f = my

    if len(mz.shape) >= 2:
        mz_neg = np.sum(mz[:fsa_size_half], axis=0)
        mz_pos = np.sum(mz[fsa_size_half + 1:], axis=0)
        mz_f = mz_neg + mz_pos + mz[fsa_size_half]
    else:
        mz_f = mz

    max_global = np.max((np.max(mx_f), np.max(my_f), np.max(mz_f)))

    return mx_f / max_global, my_f / max_global, mz_f / max_global


def reduce_magnetization_in_position(mx, my, mz, position, freq_shift):
    """Reduces the magnetization vector by summing position components.

    Args:
        mx (np.array): Array of x magnetization without reduction in frequency.
        my (np.array): Array of y magnetization without reduction in frequency.
        mz (np.array): Array of z magnetization without reduction in frequency.
        position (np.array): Array of positions.
        freq_shift (np.array): Array of frequency shift.

    Returns:
        tuple: (mx, my, mz) arrays of magnetization reduced.

    Todo:
        Test shape size different of 2.
        Set physical unit for each args.

    """
    _logger.debug("Shapes for mxyz {}, freq_shift {} and position {}".format(mx.shape,
                                                                             freq_shift.shape,
                                                                             position.shape))

    mxf, myf, mzf = reduce_magnetization_in_frequency(mx, my, mz, freq_shift, freq_shift.size)
    mxf, myf, mzf = reduce_magnetization_in_frequency(mxf, myf, mzf, position, position.shape[1])

    return mxf, myf, mzf


def create_positions(size=(1, 1, 1), step=(1., 1., 1.), offset=(0., 0., 0.), dtype=np.float32):
    """Creates array of positions.

    Args:
        size (tuple(int)): Size in x, y and z. The minimum number is one for each axis.
        step (tuple(float)): Step for each axis.
        offset (tuple(float)): Offset for each axis. If zero, the final vector begins in
            zero and ends in size plus offset.

    Returns:
        np.array: Position array in this format [[gr_x_plotx gr_y_plotx gr_z_plotx ...]
            [gr_x_ploty gr_y_ploty gr_z_ploty ...][gr_x_plotz gr_y_plotz gr_z_plotz ...]],
            where p is the number of position (from offset to size plus offset).

    Todo:
        Set physical unit for each args.

    """
    if np.min(step) <= 0.:
        raise ValueError("Step values must be greater then zero")

    size_scaled = size[0] / step[0], size[1] / step[1], size[2] / step[2]

    xposf = np.array([])
    yposf = np.array([])
    zposf = np.array([])

    if (size_scaled[0] >= 1. and size_scaled[1] >= 1. and size_scaled[2] >= 1.):
        nelements = np.prod(np.array(size_scaled))
        xpos = np.arange(offset[0], size[0] + offset[0], step[0])
        ypos = np.arange(offset[1], size[1] + offset[1], step[1])
        zpos = np.arange(offset[2], size[2] + offset[2], step[2])

        for element in np.arange(0, nelements):
            xposf = np.append(xposf, xpos[int(element % xpos.size)])
            yposf = np.append(yposf, ypos[int((element / xpos.size) % ypos.size)])
            zposf = np.append(zposf, zpos[int((element / (xpos.size * ypos.size)) % zpos.size)])
    else:
        raise ValueError("Step values must be equal or greater than size values.")

    posf = np.array([xposf, yposf, zposf])
    return posf


def frequency_shift(freq_shift, freq_step=1., offset=0., symetric=True, dtype=np.float32):
    """Generates an array of frequency shift, from -frequency_shift to +frequency_shift, between offset.

    Args:
        freq_shift (float [Hz]): Maximum frequency to shift.
        freq_step (float [Hz]): Spacing between values.
        offset (float [Hz]): Offset frequency.
        symetric (bool): If true, generates the array between offset (-maximum shift,
            maximum shift), otherwise from offset to maximum frequency. Default is True.
        dtype (np.dtype): Data type for the array. Default is np.float32.

    Returns:
        np.array [Hz]: Array of frequency shift value.

    Todo:
        Use the key symetric for something.

    """
    f_neg = np.arange(-freq_step, -freq_shift, -freq_step, dtype=dtype)[::-1]
    f_pos = np.arange(freq_step, freq_shift, freq_step, dtype=dtype)
    f_zero = np.arange(0., 1., dtype=dtype)
    frequency_shift = np.concatenate((f_neg, f_zero, f_pos)) + offset

    return frequency_shift


def calculate_t2_star(t2, freq_shift):
    """Returns the value for t2*, considering the range of frequencies.

    Args:
        t2 (float [s]): T2 value in seconds.
        freq_shift (float [Hz]): Frequency shift from resonance - symetric 
            between zero (in resonance).

    Returns:
        float [s]: T2 star value.

    Todo:
        Confirm if it is the right way to calculate or if it has a weight function for t2star
        Pass freq_shift as a number?

    """
    shift = np.max(freq_shift) + np.abs(np.min(freq_shift))
    t2star = 1. / (1. / t2 + shift)
    return t2star


def transform_cart_to_pol(x, y):
    """Returns a transformed catesian vector into polar coordinates.

    Args:
        x (np.array): X coordinate.
        y (np.array): Y coordinate.

    Returns:
        tuple: (rho, phi) vectors formed by radial and angular coordinates.

    """
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)

    return (rho, phi)


def transform_pol_to_cart(rho, phi):
    """Returns a transformed polar vector into cartesian coordinates.

    Args:
        rho (np.array): Radial coordinate.
        phi (np.array): Angular coordinate.

    Returns:
        tuple: (x, y) vectors formed by x and y coordinates

    """
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)

    return (x, y)
