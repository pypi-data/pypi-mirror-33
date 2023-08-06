#! python
# -*- coding: utf-8 -*-

"""Module for plotting related classes and functions.

Authors:
    * Victor Hugo de Mello Pessoa <victor.pessoa@usp.br>
    * Daniel Cosmo Pizetta <daniel.pizetta@usp.br>

Since:
    2017/07/01

"""


import logging

import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtCore, QtGui

from mrsprint.simulator import (reduce_magnetization_in_frequency,
                                reduce_magnetization_in_position)

_logger = logging.getLogger(__name__)


class Plot():
    """Class that contains the plots of simulation.

    Args:
        settings (Settings): Represents the program settings.
        mx (np.ndarray): Magnetization in x.
        my (np.ndarray): Magnetization in y.
        mz (np.ndarray): Magnetization in z.
        gr (np.ndarray): Gradients of magnetic field.
        tp (np.ndarray): Time.
        freq_shift (np.ndarray): Frequency shift due to field inhomogeneity.
        position (np.ndarray): Position of spins.
        max_magnetization (float): Maximum value of magnetization.

    """

    def __init__(self, settings, mx, my, mz, gr, tp, freq_shift, position, max_magnetization):
        self.mx = mx
        self.my = my
        self.mz = mz
        self.gr = gr
        self.tp = tp
        self.freq_shift = freq_shift
        self.position = position
        self.max_magnetization = max_magnetization
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.index_pos = 0

        self.show3DAxes = settings.simulator_group.show3DAxes.value()
        self.show3DGrid = settings.simulator_group.show3DGrid.value()
        self.plot3DGrad = settings.simulator_group.plot3DGrad.value()

        self.plot3DOffResMag = settings.simulator_group.plot3DOffResMag.value()
        self.plot3DOffResPercentage = settings.simulator_group.plot3DOffResPercentage.value()

        self.plot3DTotalMag = settings.simulator_group.plot3DTotalMag.value()
        self.plot3DTotalMagZero = settings.simulator_group.plot3DTotalMagZero.value()

    def plotMagnetization(self, mag_win):
        """Create the graphics of magnetization.

        Args:
            mag_win (pg.graphicsWindows.GraphicsWindow): Window where plot will be made.

        """
        # reduce and rescale the magnetization
        mx, my, mz = reduce_magnetization_in_position(self.mx, self.my, self.mz, self.position, self.freq_shift)

        # transversal magnetization
        self.reduced_mxy = mx + 1.0j * my
        mag_mxy = np.absolute(self.reduced_mxy)
        phase_mxy = np.angle(self.reduced_mxy, deg=False)

        # create the graphics of magnetization
        mx_plot = plot_item(mag_win, self.tp, mx, "r", False, "", "", True, "Mag (x)", "")
        my_plot = plot_item(mag_win, self.tp, my, "g", False, "", "", True, "Mag (y)", "")
        mz_plot = plot_item(mag_win, self.tp, mz, "b", False, "", "", True, "Mag (z)", "")

        mxy_plot = plot_item(mag_win, self.tp, mag_mxy, "c", False, "", "", True, "Mag transv", "")
        ph_mxy_plot = plot_item(mag_win, self.tp, phase_mxy, "c", True, "Time", "", True, "Phase", "")

        ph_mxy_plot.getAxis('left').setTicks([[(np.pi, chr(960)), (np.pi / 2, chr(960) + '/2'), (0.0, '0'), (-np.pi, '-' + chr(960)), (-np.pi / 2, '-' + chr(960) + '/2')]])

        # connect the visualization of the graphics
        plot = [mx_plot, my_plot, mz_plot, mxy_plot, ph_mxy_plot]
        for i in range(len(plot) - 1):
            plot[i].getViewBox().setXLink(plot[i + 1].getViewBox())

        self.timelines = [pg.InfiniteLine(pos=0, angle=90, pen="w", movable=False) for i in plot]

        for i in range(len(plot)):
            plot[i].addItem(self.timelines[i])

    def plotSpin(self, view):
        """Create the 3D exhibition of magnetization over the experiment.

        Args:
            view (pg.graphicsWindows.GraphicsWindow): Window where the plot will be made.

        """
        # index for animation loop
        self.index = 0
        # index step for reduction of the frames to increase speed
        self.index_step = 20
        # frequency shift array size
        self.fsa_size = self.freq_shift.size - 1

        # create a 3d view
        max_abs_pos = np.max([np.abs(np.min(self.position)), np.max(self.position)]) + 1
        view.setCameraPosition(distance=max_abs_pos * 3)

        # show lines for each axis centered in 0,0,0
        if self.show3DAxes:
            # create axis lines for each axis
            xline = gl.GLLinePlotItem(pos=np.array([0, 0, 0, max_abs_pos, 0, 0]).reshape(2, 3),
                                      color=(255, 0, 0, 1), width=3, antialias=True)
            xline.setGLOptions('additive')
            yline = gl.GLLinePlotItem(pos=np.array([0, 0, 0, 0, max_abs_pos, 0]).reshape(2, 3),
                                      color=(0, 255, 0, 1), width=3, antialias=True)
            yline.setGLOptions('additive')
            zline = gl.GLLinePlotItem(pos=np.array([0, 0, 0, 0, 0, max_abs_pos]).reshape(2, 3),
                                      color=(0, 0, 255, 1), width=3, antialias=True)
            zline.setGLOptions('additive')

            # draw axis lines after surfaces since they may be translucent
            xline.setDepthValue(10)
            yline.setDepthValue(10)
            zline.setDepthValue(10)

            # add axis lines to the view
            view.addItem(xline)
            view.addItem(yline)
            view.addItem(zline)

        # show a 3D grid centered in 0,0,0
        if self.show3DGrid:
            zgrid = gl.GLGridItem(color=(255, 255, 255, 0.01))
            zgrid.setGLOptions('additive')
            zgrid.setDepthValue(10)
            view.addItem(zgrid)

        self.mag_sum = []
        self.mag_pos = []
        self.mag_neg = []
        self.mag_zero = []

        self.grad_x = []
        self.grad_y = []
        self.grad_z = []

        self.index_pos = 0

        self.mag_negs = []
        self.mag_poss = []

        # sum the frequency components
        self.mx_sum_fs, self.my_sum_fs, self.mz_sum_fs = reduce_magnetization_in_frequency(self.mx, self.my, self.mz, self.freq_shift, self.freq_shift.size)
        self.mx_sum_fs *= self.max_magnetization
        self.my_sum_fs *= self.max_magnetization
        self.mz_sum_fs *= self.max_magnetization

        for x_pos, y_pos, z_pos in list(zip(self.position[0], self.position[1], self.position[2])):

            # create lines that represents the gradients - this is dynamic
            if self.plot3DGrad:
                self.grad_x.append(gl.GLLinePlotItem(pos=np.array([x_pos, y_pos, z_pos, x_pos, y_pos, z_pos]).reshape(2, 3), color=(255, 0, 0, 0.5), antialias=True, mode='lines', width=1))
                self.grad_y.append(gl.GLLinePlotItem(pos=np.array([x_pos, y_pos, z_pos, x_pos, y_pos, z_pos]).reshape(2, 3), color=(0, 255, 0, 0.5), antialias=True, mode='lines', width=1))
                self.grad_z.append(gl.GLLinePlotItem(pos=np.array([x_pos, y_pos, z_pos, x_pos, y_pos, z_pos]).reshape(2, 3), color=(0, 0, 255, 0.5), antialias=True, mode='lines', width=1))

                view.addItem(self.grad_x[self.index_pos])
                view.addItem(self.grad_y[self.index_pos])
                view.addItem(self.grad_z[self.index_pos])

            # create lines that represents the magnetization, show the summation, max and min freq shift - this is dynamic
            if self.plot3DTotalMag:
                self.mag_sum.append(gl.GLLinePlotItem(pos=np.array([x_pos, y_pos, z_pos, x_pos, y_pos, z_pos]).reshape(2, 3), color=pg.glColor(255, 255, 255), antialias=True, mode='lines', width=5))
                view.addItem(self.mag_sum[self.index_pos])

            if self.plot3DTotalMagZero:
                if (self.fsa_size >= 1):
                    # for more than one dimension, because of the return of bloch function
                    if self.position.shape[1] != 1:
                        self.mag_zero.append(gl.GLLinePlotItem(pos=np.array([x_pos, y_pos, z_pos, x_pos + self.mx_sum_fs[self.index_pos][0], y_pos + self.my_sum_fs[self.index_pos][0], z_pos + self.mz_sum_fs[self.index_pos][0]]).reshape(2, 3), color=(255, 255, 255, 0.3), antialias=True, mode='lines', width=10))
                    else:
                        self.mag_zero.append(gl.GLLinePlotItem(pos=np.array([x_pos, y_pos, z_pos, x_pos + self.mx_sum_fs[0], y_pos + self.my_sum_fs[0], z_pos + self.mz_sum_fs[0]]).reshape(2, 3), color=(255, 255, 255, 0.3), antialias=True, mode='lines', width=10))
                else:
                    self.mag_zero.append(gl.GLLinePlotItem(pos=np.array([x_pos, y_pos, z_pos, x_pos + self.mx_sum_fs[0], y_pos + self.my_sum_fs[0], z_pos + self.mz_sum_fs[0]]).reshape(2, 3), color=(255, 255, 255, 0.3), antialias=True, mode='lines', width=10))
                view.addItem(self.mag_zero[self.index_pos])

            if (self.fsa_size >= 1) and self.plot3DOffResMag:
                # for orl in range(0, int((plot3DOffResPercentage / 100.) * (self.fsa_size - 1) / 2.) + 1):
                # orl = 0
                self.mag_neg.append(gl.GLLinePlotItem(pos=np.array([x_pos, y_pos, z_pos, x_pos, y_pos, z_pos]).reshape(2, 3), color=(0, 255, 255, 0.3), antialias=True, mode='lines', width=5))
                self.mag_pos.append(gl.GLLinePlotItem(pos=np.array([x_pos, y_pos, z_pos, x_pos, y_pos, z_pos]).reshape(2, 3), color=(255, 0, 255, 0.3), antialias=True, mode='lines', width=5))
                # must be 2d vector
                # self.mag_neg.append(self.mag_neg)
                # self.mag_pos.append(self.mag_pos)
                view.addItem(self.mag_pos[self.index_pos])
                view.addItem(self.mag_neg[self.index_pos])

            self.index_pos += 1

    def update(self):
        """Update magnetization position vectors and timelines on graphics dynamically."""

        self.index_pos = 0
        gr_max_global = np.max(self.gr)

        if self.index > self.tp.size - self.index_step:
            self.timer.stop()
            return

        for x_pos, y_pos, z_pos in list(zip(self.position[0], self.position[1], self.position[2])):
            # update off resonance magnetization for each time point
            if self.plot3DOffResMag:
                if self.fsa_size >= 1:
                    orl = 0
                    # for more than one dimension, because of the return of the bloch function
                    if self.position.shape[1] != 1:
                        # for orl in range(0, int((plot3DOffResPercentage / 100.) * (self.fsa_size - 1) / 2.) + 1):
                        self.mag_neg[self.index_pos].setData(pos=np.array([x_pos, y_pos, z_pos, x_pos + self.mx[0 + orl][self.index_pos][self.index], y_pos + self.my[0 + orl][self.index_pos][self.index], z_pos + self.mz[0 + orl][self.index_pos][self.index]]).reshape(2, 3))
                        self.mag_pos[self.index_pos].setData(pos=np.array([x_pos, y_pos, z_pos, x_pos + self.mx[self.fsa_size - orl][self.index_pos][self.index], y_pos + self.my[self.fsa_size - orl][self.index_pos][self.index], z_pos + self.mz[self.fsa_size - orl][self.index_pos][self.index]]).reshape(2, 3))
                    else:
                        # for orl in range(0, int((plot3DOffResPercentage / 100.) * (self.fsa_size - 1) / 2.) + 1):
                        self.mag_neg[self.index_pos].setData(pos=np.array([x_pos, y_pos, z_pos, x_pos + self.mx[0 + orl][self.index], y_pos + self.my[0 + orl][self.index], z_pos + self.mz[0 + orl][self.index]]).reshape(2, 3))
                        self.mag_pos[self.index_pos].setData(pos=np.array([x_pos, y_pos, z_pos, x_pos + self.mx[self.fsa_size - orl][self.index], y_pos + self.my[self.fsa_size - orl][self.index], z_pos + self.mz[self.fsa_size - orl][self.index]]).reshape(2, 3))

            # update total magnetization for each time point
            if self.plot3DTotalMag:
                if (self.fsa_size >= 1):
                    # for more than one dimension, because of the return of the bloch function
                    if self.position.shape[1] != 1:
                        self.mag_sum[self.index_pos].setData(pos=np.array([x_pos, y_pos, z_pos, x_pos + self.mx_sum_fs[self.index_pos][self.index], y_pos + self.my_sum_fs[self.index_pos][self.index], z_pos + self.mz_sum_fs[self.index_pos][self.index]]).reshape(2, 3))
                    else:
                        self.mag_sum[self.index_pos].setData(pos=np.array([x_pos, y_pos, z_pos, x_pos + self.mx_sum_fs[self.index], y_pos + self.my_sum_fs[self.index], z_pos + self.mz_sum_fs[self.index]]).reshape(2, 3))
                else:
                    self.mag_sum[self.index_pos].setData(pos=np.array([x_pos, y_pos, z_pos, x_pos + self.mx_sum_fs[self.index], y_pos + self.my_sum_fs[self.index], z_pos + self.mz_sum_fs[self.index]]).reshape(2, 3))

            # update gradients for each time point
            if self.plot3DGrad:
                self.grad_x[self.index_pos].setData(pos=np.array([x_pos, 0, 0, x_pos, 0, x_pos * self.gr[0][self.index] / gr_max_global]).reshape(2, 3))
                self.grad_y[self.index_pos].setData(pos=np.array([0, y_pos, 0, 0, y_pos, y_pos * self.gr[1][self.index] / gr_max_global]).reshape(2, 3))
                self.grad_z[self.index_pos].setData(pos=np.array([0, 0, z_pos, 0, 0, z_pos + z_pos * self.gr[2][self.index] / gr_max_global]).reshape(2, 3))

            self.index_pos += 1

        # update timeline in 2d graphics
        for timeline in self.timelines:
            timeline.setValue(self.tp[self.index])

        self.index += self.index_step

    def run(self):
        """Run the simulation on plot, from zero."""
        self.index = 0
        self.timer.start()

    def play(self):
        """Start the simulation on plot."""
        self.timer.start()

    def pause(self):
        """Stop the simulation on plot."""
        self.timer.stop()


def plot_item(graphics, x, y, line_color, x_axis=True, x_label="", x_unit="", y_axis=True, y_label="", y_unit=""):
    """Create a new plot item in a graph.

    Args:
        graphics (pl.graphicsWindow): The GraphicsWindow where the plot will be shown.
        x (np.array): List of x coordinates.
        y (np.array): List of y coordinates.
        line_color (str): String containing the color ("r", "g", "b", "w", for example).
        x_axis (bool): Visibility of x axis.
        x_label (str): Label of x axis.
        x_unit(str): Unit of x axis.
        y_axis (bool): Visibility of y axis.
        y_label (str): Label of y axis.
        y_unit(str): Unit of y axis.

    Returns:
        pg.graphicsItems.PlotItem: Plot.

    """

    item = graphics.addPlot(x=x, y=y, pen=line_color)

    if x_axis:
        if x_label or x_unit:
            item.setLabel(axis="bottom", text=x_label, units=x_unit)
    else:
        item.getAxis("bottom").setStyle(showValues=False)
        item.showAxis(axis="bottom")

    if y_axis:
        if y_label or y_unit:
            item.setLabel(axis="left", text=y_label, units=y_unit)
    else:
        item.getAxis("left").setStyle(showValues=False)
        item.showAxis(axis="left")

    item.setRange(xRange=(min(x), max(x)))
    item.getViewBox().setLimits(xMin=min(x), xMax=max(x))

    item.getAxis("top").setStyle(showValues=False)
    item.getAxis("right").setStyle(showValues=False)

    item.showAxis(axis="top")
    item.showAxis(axis="right")

    graphics.nextRow()

    return item
