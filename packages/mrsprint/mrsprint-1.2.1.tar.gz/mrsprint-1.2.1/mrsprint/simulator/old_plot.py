#! python
# -*- coding: utf-8 -*-

"""Module for plotting related classes and functions.

Authors:
    * Daniel Cosmo Pizetta <daniel.pizetta@usp.br>

Since:
    2017/07/01

"""

import logging
import threading

import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import pyqtgraph.parametertree as pt
from pyqtgraph.Qt import QtCore, QtGui

from mrsprint.globals import (AMFL, AMLN, B1_MAX, DT, FMFL, FMLN, GAMMA,
                                GR_MAX, P90_DURATION, PMFL, PMLN, TLLN, XFL,
                                XLN, YFL, YLN, ZFL, ZLN)
from mrsprint.simulator import (reduceMagnetizationInFrequency,
                                  reduceMagnetizationInPosition)

_logger = logging.getLogger(__name__)


class Plot(threading.Thread):
    """Class that controls the plot tasks."""

    def __init__(self, parameters={}, style={'color': '#EEE', 'font-size': '8pt'}, configurations={'leftWidth': 60}):
        threading.Thread.__init__(self, name='Plot')
        # setting parameters
        self.parameters = pt.parameterTypes.GroupParameter(name='Plot')
        self.parameters.framDefinition = self.parameters.addChild({'name': 'Frame definition', 'type': 'list', 'value': ['Loop', 'Interval']})
        self.parameters.frameRate = self.parameters.addChild({'name': 'Frame Rate', 'type': 'int', 'value': 30})


class SequencePlot(pg.GraphicsWindow, threading.Thread):
    """Class that controls the sequence plot."""

    def __init__(self, parameters={}, style={'color': '#EEE', 'font-size': '8pt'}, configurations={'leftWidth': 60}):
        pg.GraphicsWindow.__init__(self)
        pg.setConfigOptions(antialias=True, autoDownsample=True)
        threading.Thread.__init__(self, name='Sequence')

        global tp, tp_min, tp_max, rf_am, rf_pm, rf_fm, gr_x, gr_y, gr_z

        # setting parameters
        self.parameters = pt.parameterTypes.GroupParameter(name='Sequence')
        self.parameters.timeline = self.parameters.addChild({'name': 'Timeline', 'type': 'bool', 'value': True})
        self.parameters.gridX = self.parameters.addChild({'name': 'Grid X', 'type': 'bool', 'value': True})
        self.parameters.gridY = self.parameters.addChild({'name': 'Grid Y', 'type': 'bool', 'value': True})
        self.parameters.rfEmptyLines = self.parameters.addChild({'name': 'RF Empty Lines', 'type': 'bool', 'value': True})
        self.parameters.gradientEmptyLines = self.parameters.addChild({'name': 'Gradient Empty Lines', 'type': 'bool', 'value': True})

        # dict of all plots and timelines
        self.plots = {}
        self.plotsData = {}
        self.timelines = {}

        # RF ------------------------------------------------------------------------------------------

        self.plots['rf_am'] = pg.PlotItem(name='rf_am', pen=AMLN, brush=AMFL, fillLevel=0, width=2)
        self.plots['rf_am'].setLabel(axis='left', text='RF AM', units='G', **style)
        self.timelines['rf_am'] = pg.InfiniteLine(pos=tp[0], angle=90, pen=TLLN, movable=False)
        self.plots['rf_am'].addItem(self.timelines['rf_am'])
        self.plots['rf_am'].setXLink('rf_pm')
        self.addItem(self.plots['rf_am'])
        self.nextRow()

        self.plots['rf_pm'] = pg.PlotItem(name='rf_pm')
        self.plots['rf_pm'].getAxis('left').setTicks([[(3.14, chr(960)), (1.57, chr(960) + '/2'), (0.0, '0'), (-3.14, '-' + chr(960)), (-1.57, '-' + chr(960) + '/2')]])
        self.plots['rf_pm'].setLabel(axis='left', text='RF PM', units='Rad', **style)
        self.timelines['rf_pm'] = pg.InfiniteLine(pos=tp[0], angle=90, pen=TLLN, movable=False)
        self.plots['rf_pm'].addItem(self.timelines['rf_pm'])
        self.plots['rf_pm'].setXLink('rf_fm')
        self.addItem(self.plots['rf_pm'])
        self.nextRow()

        self.plots['rf_fm'] = pg.PlotItem(name='rf_fm')
        self.plots['rf_fm'].setLabel(axis='left', text='RF FM', units='Hz', **style)
        self.timelines['rf_fm'] = pg.InfiniteLine(pos=index, angle=90, pen=TLLN, movable=False)
        self.plots['rf_fm'].addItem(self.timelines['rf_fm'])
        self.plots['rf_fm'].setXLink('gr_x')
        self.addItem(self.plots['rf_fm'])
        self.nextRow()

        # GRADIENTS -----------------------------------------------------------------------------------------

        self.plots['gr_x'] = pg.PlotItem(name='gr_x')
        self.plots['gr_x'].setLabel(axis='left', text='Gr X', units='G/cm', **style)
        self.timelines['gr_x'] = pg.InfiniteLine(pos=tp[0], angle=90, pen=TLLN, movable=False)
        self.plots['gr_x'].addItem(self.timelines['gr_x'])
        self.plots['gr_x'].setXLink('gr_y')
        self.addItem(self.plots['gr_x'])
        self.nextRow()

        self.plots['gr_y'] = pg.PlotItem(name='gr_y')
        self.plots['gr_y'].setLabel(axis='left', text='Gr Y', units='G/cm', **style)
        self.timelines['gr_y'] = pg.InfiniteLine(pos=tp[0], angle=90, pen=TLLN, movable=False)
        self.plots['gr_y'].addItem(self.timelines['gr_y'])
        self.plots['gr_y'].setXLink('gr_z')
        self.addItem(self.plots['gr_y'])
        self.nextRow()

        self.plots['gr_z'] = pg.PlotItem(name='gr_z')
        self.plots['gr_z'].setLabel(axis='left', text='Gr Z', units='G/cm', **style)
        self.timelines['gr_z'] = pg.InfiniteLine(pos=tp[0], angle=90, pen=TLLN, movable=False)
        self.plots['gr_z'].addItem(self.timelines['gr_z'])
        self.addItem(self.plots['gr_z'])
        self.nextRow()

        # apply general configuration for all plots
        for plot in self.plots.values():
            plot.getAxis('left').setWidth(configurations['leftWidth'])
            plot.getAxis('bottom').setStyle(showValues=False)
            plot.getAxis('top').setStyle(showValues=False)
            plot.getAxis('right').setStyle(showValues=False)
            plot.showAxis(axis='bottom')
            plot.showAxis(axis='top')
            plot.showAxis(axis='right')
            plot.showGrid(x=self.parameters.gridX.value(), alpha=0.0)
            plot.showGrid(y=self.parameters.gridY.value(), alpha=0.0)
            plot.setRange(xRange=(tp_min, tp_max))

        # time scale in the last one
        self.plots['gr_z'].setLabel(axis='bottom', text='Time', units='s', **style)
        self.plots['gr_z'].getAxis('bottom').setStyle(showValues=False)

    def update(self):
        """The graphic is just updated when a new sequence is generated
        or another dimension of the sequence is changed."""

        # those globals values represents the current set of values
        global tp, tp_min, tp_max, rf_am, rf_pm, rf_fm, gr_x, gr_y, gr_z

        self.plots['rf_am'].plot(tp, rf_am, pen=AMLN, brush=AMFL, fillLevel=0, width=2)
        self.plots['rf_pm'].plot(tp, rf_pm, pen=PMLN, brush=PMFL, fillLevel=0, width=2)
        self.plots['rf_fm'].plot(tp, rf_fm, pen=FMLN, brush=FMFL, fillLevel=0, width=2)
        self.plots['gr_x'].plot(tp, gr_x, pen=XLN, brush=XFL, fillLevel=0, width=2)
        self.plots['gr_y'].plot(tp, gr_y, pen=YLN, brush=YFL, fillLevel=0, width=2)
        self.plots['gr_z'].plot(tp, gr_z, pen=ZLN, brush=ZFL, fillLevel=0, width=2)

        # re setting range for time
        for plot in self.plots.values():
            plot.setRange(xRange=(tp_min, tp_max))

    def updateTimeline(self, time_value):
        """More simple update just for timeline."""
        for timeline in self.timelines.values():
            timeline.setValue(time_value)

#
# class TimeDomainPlot(pg.GraphicsWindow, threading.Thread):
#     """
#     Class that controls the time domain plot.
#     """
#
#     def __init__(self, parameters={}, style={}, configurations={'leftWidth': 60}):
#         """
#         Constructor.
#         """
#         pg.GraphicsWindow.__init__(self)
#         pg.setConfigOptions(antialias=True, autoDownsample=True)
#         threading.Thread.__init__(self, name='Time Domain')
#
#         global tp, tp_min, tp_max, time_value, rf_am, rf_pm, rf_fm, gr_x, gr_y, gr_z, rd
#
#         self.parameters = pt.parameterTypes.GroupParameter('Time Domain')
#         self.parameters.modulus = self.parameters.timeDomain.addChild({'name': 'Modulus', 'type': 'bool', 'value': True})
#         self.parameters.phase = self.parameters.timeDomain.addChild({'name': 'Phase', 'type': 'bool', 'value': True})
#         self.parameters.real = self.parameters.timeDomain.addChild({'name': 'Real', 'type': 'bool', 'value': True})
#         self.parameters.imaginary = self.parameters.timeDomain.addChild({'name': 'Imaginary', 'type': 'bool', 'value': True})
#
#         # create a dock widget to put 1d kx, ky, x, y graphs
#         if len(rd.shape) == 1:
#
#             region = pg.LinearRegionItem()
#             region.setZValue(10)
#             beg, end = 0, rd.real.size
#             data_fft = np.fft.ifft(rd)
#             data_fft_abs = np.absolute(data_fft)
#             data_fft_phase = np.angle(data_fft)
#             data_abs = np.absolute(rd)
#             data_phase = np.angle(rd)
#
#             kxky_xy_win = pg.GraphicsWindow()
#
#             abs_plot = kxky_xy_win.addPlot(x=tp[beg:end], y=data_abs, row=0, col=0, pen='b')
#             abs_plot.showGrid(x=True, y=True, alpha=0.7)
#             abs_plot.setLabel(axis='left', text='Magnitude', **style)
#
#             phase_plot = kxky_xy_win.addPlot(x=tp[beg:end], y=data_phase, row=1, col=0, pen='b')
#             phase_plot.showGrid(x=True, y=True, alpha=0.7)
#             phase_plot.setLabel(axis='left', text='Phase', **style)
#
#             real_plot = kxky_xy_win.addPlot(x=tp[beg:end], y=data.real, row=2, col=0, pen='g')
#             real_plot.showGrid(x=True, y=True, alpha=0.7)
#             real_plot.setLabel(axis='left', text='Real', **style)
#
#             imag_plot = kxky_xy_win.addPlot(x=tp[beg:end], y=data.imag, row=3, col=0, pen='y')
#             imag_plot.showGrid(x=True, y=True, alpha=0.7)
#             imag_plot.setLabel(axis='left', text='Imaginary', **style)
#
#
# class FrequencyDomainPlot(pg.GraphicsWindow, threading.Thread):
#     """
#     Class that controls the frequency domain plot.
#     """
#
#     def __init__(self, parameters={}, style={}, configurations={'leftWidth': 60}):
#         """
#         Constructor.
#         """
#         pg.GraphicsWindow.__init__(self)
#         pg.setConfigOptions(antialias=True, autoDownsample=True)
#         threading.Thread.__init__(self, name='Frequency Domain')
#
#         global tp, tp_min, tp_max, time_value, rf_am, rf_pm, rf_fm, gr_x, gr_y, gr_z, rd
#
#         self.parameters = pt.parameterTypes.GroupParameter('Frequency Domain')
#         self.parameters.modulus = self.parameters.addChild({'name': 'Modulus', 'type': 'bool', 'value': True})
#         self.parameters.phase = self.parameters.addChild({'name': 'Phase', 'type': 'bool', 'value': True})
#         self.parameters.real = self.parameters.addChild({'name': 'Real', 'type': 'bool', 'value': True})
#         self.parameters.imaginary = self.parameters.addChild({'name': 'Imaginary', 'type': 'bool', 'value': True})
#
#         # create a dock widget to put 1d kx, ky, x, y graphs
#         if len(rd.shape) == 1:
#
#             region = pg.LinearRegionItem()
#             region.setZValue(10)
#
#             beg, end = 0, rd.real.size
#             data_fft = np.fft.ifft(rd)
#             data_fft_abs = np.absolute(data_fft)
#             data_fft_phase = np.angle(data_fft)
#             data_abs = np.absolute(rd)
#             data_phase = np.angle(rd)
#
#             kxky_xy_win = pg.GraphicsWindow()
#             pg.setConfigOptions(antialias=True, autoDownsample=True)
#
#             fft_abs_plot = kxky_xy_win.addPlot(x=tp[beg:end], y=data_fft_abs, row=0, col=1, pen='b')
#             fft_abs_plot.showGrid(x=True, y=True, alpha=0.7)
#             fft_abs_plot.setLabel(axis='left', text='Abs')
#
#
#             fft_phase_plot = kxky_xy_win.addPlot(x=tp[beg:end], y=data_fft_phase, row=1, col=1, pen='b')
#             fft_phase_plot.showGrid(x=True, y=True, alpha=0.7)
#             fft_phase_plot.setLabel(axis='left', text='Phase')
#
#             fft_real_plot = kxky_xy_win.addPlot(x=tp[beg:end], y=data_fft.real, row=2, col=1, pen='g')
#             fft_real_plot.showGrid(x=True, y=True, alpha=0.7)
#             fft_real_plot.setLabel(axis='left', text='Real')
#
#             fft_imag_plot = kxky_xy_win.addPlot(x=tp[beg:end], y=data_fft.imag, row=3, col=1, pen='y')
#             fft_imag_plot.showGrid(x=True, y=True, alpha=0.7)
#             fft_imag_plot.setLabel(axis='left', text='Imaginary')
#
#
#         if len(data.shape) == 2 and data.shape[0] >= 1:
#             data_fft = np.fft.ifft2(data)
#             data_fft_abs = np.absolute(data_fft)
#             data_abs = np.absolute(data)
#
#             kxky_xy_win = pg.ImageView()
#             kxky_xy_win.setImage((data_fft_abs.T * 255).astype(int))
#             kxky_xy_dock = QtGui.QDockWidget("K space - Fourier Transform")
#             kxky_xy_dock.setWidget(kxky_xy_win)
#             window.addDockWidget(QtCore.Qt.RightDockWidgetArea, kxky_xy_dock)
#             window.tabifyDockWidget(mag_dock, kxky_xy_dock)
#
#         # def updateReg():
#
#             # region.setZValue(10)
#             #minX, maxX = region.getRegion()
#             #kspace_abs_plot.setXRange(minX, maxX, padding=0)
#             #kspace_real_plot.setXRange(minX, maxX, padding=0)
#             #kspace_imag_plot.setXRange(minX, maxX, padding=0)
#
#
# class SimulatorPlot3D(gl.GLViewWidget, threading.Thread):
#     """
#     Class that controls the magnetization plot.
#     """
#
#     def __init__(self, parameters={}, style={'color': '#EEE', 'font-size': '8pt'}, configurations={'leftWidth': 60}):
#         """
#         Constructor.
#         """
#         pg.GraphicsWindow.__init__(self)
#         pg.setConfigOptions(antialias=True, autoDownsample=True)
#         threading.Thread.__init__(self, name='Simulator')
#
#         global tp, tp_min, tp_max, mx, my, mz, mxy_mag, mxy_pha, ps, fs
#         # grid
#         self.parameters = pt.parameterTypes.GroupParameter(name='Simulator 3D')
#         self.parameters.gridX = self.parameters.addChild({'name': 'Grid X', 'type': 'bool', 'value': True})
#         self.parameters.gridY = self.parameters.addChild({'name': 'Grid Y', 'type': 'bool', 'value': True})
#         self.parameters.gridZ = self.parameters.addChild({'name': 'Grid Z', 'type': 'bool', 'value': True})
#         # axis
#         self.parameters.axisX = self.parameters.addChild({'name': 'Axis X', 'type': 'bool', 'value': True})
#         self.parameters.axisY = self.parameters.addChild({'name': 'Axis Y', 'type': 'bool', 'value': True})
#         self.parameters.axisZ = self.parameters.addChild({'name': 'Axis Z', 'type': 'bool', 'value': True})
#         # gradient
#         self.parameters.gradientX = self.parameters.addChild({'name': 'Gradient X', 'type': 'bool', 'value': True})
#         self.parameters.gradientY = self.parameters.addChild({'name': 'Gradient Y', 'type': 'bool', 'value': True})
#         self.parameters.gradientZ = self.parameters.addChild({'name': 'Gradient Z', 'type': 'bool', 'value': True})
#         # magnetization
#         self.parameters.inResonanceLine = self.parameters.addChild({'name': 'In Resonance', 'type': 'bool', 'value': True})
#         self.parameters.offResonanceLines = self.parameters.addChild({'name': 'Off Resonance', 'type': 'bool', 'value': True})
#         self.parameters.numberOfIsocromatics = self.parameters.addChild({'name': 'Number of Isocromatics', 'type': 'int', 'value': 10, 'limits': [0, 100]})
#         self.parameters.summation = self.parameters.addChild({'name': 'Total', 'type': 'bool', 'value': True})
#         # voxel
#         self.parameters.voxel = self.parameters.addChild({'name': 'Voxel', 'type': 'bool', 'value': True})
#
#         max_abs_pos = np.max([np.abs(np.min(ps)), np.max(ps)]) + 1
#         self.setCameraPosition(distance=max_abs_pos * 2)
#
#         # show lines for each axis centered in 0,0,0
#         # create axis lines for each axis
#         if self.parameters.axisX.value():
#             xline = gl.GLLinePlotItem(pos=np.array([-max_abs_pos, 0, 0, max_abs_pos, 0, 0]).reshape(2, 3), color=XLN, antialias=True)
#             xline.setGLOptions('additive')
#             xline.setDepthValue(-10)
#             self.addItem(xline)
#         if self.parameters.axisY.value():
#             yline = gl.GLLinePlotItem(pos=np.array([0, -max_abs_pos, 0, 0, max_abs_pos, 0]).reshape(2, 3), color=YLN, antialias=True)
#             yline.setGLOptions('additive')
#             yline.setDepthValue(-10)
#             self.addItem(yline)
#         if self.parameters.axisZ.value():
#             zline = gl.GLLinePlotItem(pos=np.array([0, 0, -max_abs_pos, 0, 0, max_abs_pos]).reshape(2, 3), color=ZLN, antialias=True)
#             zline.setGLOptions('additive')
#             yline.setDepthValue(-10)
#             self.addItem(zline)
#
#         # show a 3D grid centered in 0,0,0
#         # create grid for each axis
#         if self.parameters.gridX.value():
#             xgrid = gl.GLGridItem(color=(255, 255, 255, 0.01))
#             xgrid.setGLOptions('additive')
#             xgrid.setDepthValue(-10)
#             xgrid.rotate(90, 0, 1, 0)
#             self.addItem(xgrid)
#         if self.parameters.gridY.value():
#             ygrid = gl.GLGridItem(color=(255, 255, 255, 0.01))
#             ygrid.setGLOptions('additive')
#             ygrid.setDepthValue(-10)
#             ygrid.rotate(90, 1, 0, 0)
#             self.addItem(ygrid)
#         if self.parameters.gridZ.value():
#             zgrid = gl.GLGridItem(color=(255, 255, 255, 0.01))
#             zgrid.setGLOptions('additive')
#             zgrid.setDepthValue(-10)
#             self.addItem(zgrid)
#
#         mag_sum = []
#         mag_pos = []
#         mag_neg = []
#         mag_zero = []
#         grad_x = []
#         grad_y = []
#         grad_z = []
#         voxels = []
#         subvoxels = []
#         index_pos = 0
#         fs_size = fs.size - 1
#
#         # sum the frequency components
#         mx_sum_fs, my_sum_fs, mz_sum_fs = reduceMagnetizationInFrequency(mx, my, mz, fs, fs.size)
#
#         for x_pos, y_pos, z_pos in list(zip(ps[0], ps[1], ps[2])):
#
#             # show spheres that represent a voxel for each voxel in position - this is static
#             if self.parameters.voxel.value():
#                 voxels.append(gl.GLMeshItem(meshdata=gl.MeshData.sphere(rows=10, cols=10), smooth=False, drawFaces=True, drawEdges=False, color=(255, 255, 255, 0.02)))
#                 voxels[index_pos].translate(x_pos, y_pos, z_pos)
#                 voxels[index_pos].setGLOptions('additive')
#                 self.addItem(voxels[index_pos])
#
#             # show spheres that represent a voxel for each voxel in position - this is static
#             if self.parameters.subVoxel.value():
#                 subvoxels.append(gl.GLScatterPlotItem(pos=np.array([x_pos, y_pos, z_pos]), size=2., color=(255, 0, 0, 1.)))
#                 subvoxels[index_pos].setGLOptions('additive')
#                 self.addItem(subvoxels[index_pos])
#
#             # create lines that represents the gradients - this is dymanic
#             if self.parameters.gradientX.value():
#                 grad_x.append(gl.GLLinePlotItem(pos=np.array([x_pos, y_pos, z_pos, x_pos, y_pos, z_pos]).reshape(2, 3), color=XLN, antialias=True, mode='lines', width=1))
#                 self.addItem(grad_x[index_pos])
#             if self.parameters.gradientY.value():
#                 grad_y.append(gl.GLLinePlotItem(pos=np.array([x_pos, y_pos, z_pos, x_pos, y_pos, z_pos]).reshape(2, 3), color=YLN, antialias=True, mode='lines', width=1))
#                 self.addItem(grad_y[index_pos])
#             if self.parameters.gradientZ.value():
#                 grad_z.append(gl.GLLinePlotItem(pos=np.array([x_pos, y_pos, z_pos, x_pos, y_pos, z_pos]).reshape(2, 3), color=ZLN, antialias=True, mode='lines', width=1))
#                 self.addItem(grad_z[index_pos])
#
#             # create lines that represents the magnetization, show the summation
#             if self.parameters.summation.value():
#                 mag_sum.append(gl.GLLinePlotItem(pos=np.array([x_pos, y_pos, z_pos, x_pos, y_pos, z_pos]).reshape(2, 3), color=pg.glColor(255, 255, 255), antialias=True, mode='lines', width=2))
#                 self.addItem(mag_sum[index_pos])
#
#             if self.parameters.zero.value():
#                 if (fs_size >= 1):
#                     # for more than one dimension, because of the return of the bloch function
#                     if ps.shape[1] != 1:
#                         mag_zero.append(gl.GLLinePlotItem(pos=np.array([x_pos, y_pos, z_pos, x_pos + mx_sum_fs[index_pos][0] * scale, y_pos + my_sum_fs[index_pos][0] * scale, z_pos + mz_sum_fs[index_pos][0] * scale]).reshape(2, 3), color=(255, 0, 0, 0.3), antialias=True, mode='lines', width=2))
#                     else:
#                         mag_zero.append(gl.GLLinePlotItem(pos=np.array([x_pos, y_pos, z_pos, x_pos + mx_sum_fs[0] * scale, y_pos + my_sum_fs[0] * scale, z_pos + mz_sum_fs[0] * scale]).reshape(2, 3), color=(255, 0, 0, 0.3), antialias=True, mode='lines', width=2))
#                 else:
#                     mag_zero.append(gl.GLLinePlotItem(pos=np.array([x_pos, y_pos, z_pos, x_pos + mx_sum_fs[0] * scale, y_pos + my_sum_fs[0] * scale, z_pos + mz_sum_fs[0] * scale]).reshape(2, 3), color=(255, 0, 0, 0.3), antialias=True, mode='lines', width=2))
#                 self.addItem(mag_zero[index_pos])
#
#             if (fs_size >= 1) and self.parameters.offResonanceLines.value():
#                 mag_neg.append(gl.GLLinePlotItem(pos=np.array([x_pos, y_pos, z_pos, x_pos, y_pos, z_pos]).reshape(2, 3), color=(0, 255, 255, 0.17), antialias=True, mode='lines', width=1))
#                 mag_pos.append(gl.GLLinePlotItem(pos=np.array([x_pos, y_pos, z_pos, x_pos, y_pos, z_pos]).reshape(2, 3), color=(255, 0, 255, 0.17), antialias=True, mode='lines', width=1))
#                 self.addItem(mag_pos[index_pos])
#                 self.addItem(mag_neg[index_pos])
#
#             index_pos += 1
#
#         def updateTimeline(time_value):
#
#             for x_pos, y_pos, z_pos in list(zip(ps[0], ps[1], ps[2])):
#
#                 # update off resonance magnetization for each time point
#                 if plot3DOffResMag:
#                     if fs_size >= 1:
#                         orl = 0
#                         # for more than one dimension, because of the return of the bloch function
#                         if ps.shape[1] != 1:
#                             # for orl in range(0, int((plot3DOffResPercentage / 100.) * (fsa_size-1) / 2.) + 1):
#                             mag_neg[index_pos].setData(pos=np.array([x_pos, y_pos, z_pos, x_pos + mx[0 + orl][index_pos][index] * scale, y_pos + my[0 + orl][index_pos][index] * scale, z_pos + mz[0 + orl][index_pos][index] * scale]).reshape(2, 3))
#                             mag_pos[index_pos].setData(pos=np.array([x_pos, y_pos, z_pos, x_pos + mx[fsa_size - orl][index_pos][index] * scale, y_pos + my[fsa_size - orl][index_pos][index] * scale, z_pos + mz[fsa_size - orl][index_pos][index] * scale]).reshape(2, 3))
#                         else:
#                             # for orl in range(0, int((plot3DOffResPercentage / 100.) * (fsa_size-1) / 2.) + 1):
#                             mag_neg[index_pos].setData(pos=np.array([x_pos, y_pos, z_pos, x_pos + mx[0 + orl][index] * scale, y_pos + my[0 + orl][index] * scale, z_pos + mz[0 + orl][index] * scale]).reshape(2, 3))
#                             mag_pos[index_pos].setData(pos=np.array([x_pos, y_pos, z_pos, x_pos + mx[fsa_size - orl][index] * scale, y_pos + my[fsa_size - orl][index] * scale, z_pos + mz[fsa_size - orl][index] * scale]).reshape(2, 3))
#
#                 # update total magnetization for each time point
#                 if plot3DTotalMag:
#                     if (fsa_size >= 1):
#                         # for more than one dimension, because of the return of the bloch function
#                         if position.shape[1] != 1:
#                             mag_sum[index_pos].setData(pos=np.array([x_pos, y_pos, z_pos, x_pos + mx_sum_fs[index_pos][index] * scale, y_pos + my_sum_fs[index_pos][index] * scale, z_pos + mz_sum_fs[index_pos][index] * scale]).reshape(2, 3))
#                         else:
#                             mag_sum[index_pos].setData(pos=np.array([x_pos, y_pos, z_pos, x_pos + mx_sum_fs[index] * scale, y_pos + my_sum_fs[index] * scale, z_pos + mz_sum_fs[index] * scale]).reshape(2, 3))
#                     else:
#                         mag_sum[index_pos].setData(pos=np.array([x_pos, y_pos, z_pos, x_pos + mx_sum_fs[index] * scale, y_pos + my_sum_fs[index] * scale, z_pos + mz_sum_fs[index] * scale]).reshape(2, 3))
#
#                 # update gradients for each time point
#                 if plot3DGrad:
#                     grad_x[index_pos].setData(pos=np.array([x_pos, 0, 0, x_pos, 0, x_pos * gr[0][index] / gr_max_global]).reshape(2, 3))
#                     grad_y[index_pos].setData(pos=np.array([0, y_pos, 0, 0, y_pos, y_pos * gr[1][index] / gr_max_global]).reshape(2, 3))
#                     grad_z[index_pos].setData(pos=np.array([0, 0, z_pos, 0, 0, z_pos + z_pos * gr[2][index] / gr_max_global]).reshape(2, 3))
#
#                 index_pos += 1
#
#
# class MagnetizationPlot(pg.GraphicsWindow, threading.Thread):
#     """
#     Class that controls the magnetization plot.
#     """
#
#     def __init__(self, parameters={}, style={'color': '#EEE', 'font-size': '8pt'}, configurations={'leftWidth': 60}):
#         """
#         Constructor.
#         """
#         pg.GraphicsWindow.__init__(self)
#         pg.setConfigOptions(antialias=True, autoDownsample=True)
#         threading.Thread.__init__(self, name='Magnetization')
#
#         global time_value, tp, tp_min, tp_max, mx, my, mz, mxy_mag, mxy_pha
#
#         self.parameters = pt.parameterTypes.GroupParameter(name='Magnetization')
#         self.parameters.timeline = self.parameters.addChild({'name': 'Timeline', 'type': 'bool', 'value': True})
#         self.parameters.gridX = self.parameters.addChild({'name': 'Grid X', 'type': 'bool', 'value': True})
#         self.parameters.gridY = self.parameters.addChild({'name': 'Grid Y', 'type': 'bool', 'value': True})
#         self.parameters.mx = self.parameters.addChild({'name': 'Mx', 'type': 'bool', 'value': True})
#         self.parameters.my = self.parameters.addChild({'name': 'My', 'type': 'bool', 'value': True})
#         self.parameters.mz = self.parameters.addChild({'name': 'Mz', 'type': 'bool', 'value': True})
#         self.parameters.mxy_mag = self.parameters.addChild({'name': 'Mxy Modulus', 'type': 'bool', 'value': True})
#         self.parameters.mxy_pha = self.parameters.addChild({'name': 'Mxy Phase', 'type': 'bool', 'value': True})
#
#         # dict of all plots and timelines
#         self.plots = {}
#         self.timelines = {}
#
#         # MAGNETIZATION ---------------------------------------------------------------------
#
#         self.plots['mx'] = pg.PlotItem(name='mx')
#         self.plots['mx'].setLabel(axis='left', text='Mag X', **style)
#         self.timelines['mx'] = pg.InfiniteLine(pos=tp[0], angle=90, pen=TLLN, movable=False)
#         self.plots['mx'].addItem(self.timelines['mx'])
#         self.plots['mx'].setXLink('my')
#         self.addItem(self.plots['mx'])
#         self.nextRow()
#
#         self.plots['my'] = pg.PlotItem(name='my')
#         self.plots['my'].setLabel(axis='left', text='Mag Y', **style)
#         self.timelines['my'] = pg.InfiniteLine(pos=tp[0], angle=90, pen=TLLN, movable=False)
#         self.plots['my'].addItem(self.timelines['my'])
#         self.plots['my'].setXLink('mz')
#         self.addItem(self.plots['my'])
#         self.nextRow()
#
#         self.plots['mz'] = pg.PlotItem(name='mz')
#         self.plots['mz'].setLabel(axis='left', text='Mag Z', **style)
#         self.timelines['mz'] = pg.InfiniteLine(pos=tp[0], angle=90, pen=TLLN, movable=False)
#         self.plots['mz'].addItem(self.timelines['mz'])
#         self.plots['mz'].setXLink('mxy_mag')
#         self.addItem(self.plots['mz'])
#         self.nextRow()
#
#         # MAGNITUDE AND PHASE -------------------------------------------------------------------
#
#         self.plots['mxy_mag'] = pg.PlotItem(name='mxy_mag')
#         self.plots['mxy_mag'].setLabel(axis='left', text='Mag XY', **style)
#         self.timelines['mxy_mag'] = pg.InfiniteLine(pos=tp[0], angle=90, pen=TLLN, movable=False)
#         self.plots['mxy_mag'].addItem(self.timelines['mxy_mag'])
#         self.plots['mxy_mag'].setXLink('mxy_pha')
#         self.addItem(self.plots['mxy_mag'])
#         self.nextRow()
#
#         self.plots['mxy_pha'] = pg.PlotItem(name='mxy_pha')
#         self.plots['mxy_pha'].setLabel(axis='left', text='Phase XY', **style)
#         self.timelines['mxy_pha'] = pg.InfiniteLine(pos=tp[0], angle=90, pen=TLLN, movable=False)
#         self.plots['mxy_pha'].addItem(self.timelines['mxy_pha'])
#         self.addItem(self.plots['mxy_pha'])
#
#         # apply general configuration for all plots
#         for plot in self.plots.values():
#             plot.getAxis('left').setWidth(configurations['leftWidth'])
#             plot.getAxis('bottom').setStyle(showValues=False)
#             plot.getAxis('top').setStyle(showValues=False)
#             plot.getAxis('right').setStyle(showValues=False)
#             plot.showAxis(axis='bottom')
#             plot.showAxis(axis='top')
#             plot.showAxis(axis='right')
#             plot.showGrid(x=self.parameters.gridX.value(), alpha=0.2)
#             plot.showGrid(y=self.parameters.gridY.value(), alpha=0.2)
#             plot.setRange(xRange=(tp_min, tp_max))
#
#         # time scale in the last one
#         self.plots['mxy_pha'].setLabel(axis='bottom', text='Time', units='s', **style)
#         self.plots['mxy_pha'].getAxis('bottom').setStyle(showValues=False)
#
#     def update(self):
#         """
#         The graphic is just updated when a new sequence is generated
#         or another dimension of the sequence is changed.
#         """
#
#         # those globals values represents the current set of values
#         global tp, tp_min, tp_max, mx, my, mz, mxy_mag, mxy_pha
#         self.plots['mx'].plot(tp, mx, pen=XLN, brush=XFL, fillLevel=0, width=2)
#         self.plots['my'].plot(tp, my, pen=YLN, brush=YFL, fillLevel=0, width=2)
#         self.plots['mz'].plot(tp, mz, pen=ZLN, brush=ZFL, fillLevel=0, width=2)
#         self.plots['mxy_mag'].plot(tp, mxy_mag, pen=XYLN, brush=XYFL, fillLevel=0, width=2)
#         self.plots['mxy_pha'].plot(tp, mxy_pha, pen=XYLN, brush=XYFL, fillLevel=0, width=2)
#
#         # re setting range for time
#         for plot in self.plots.values():
#             plot.setRange(xRange=(tp_min, tp_max))
#
#     def updateTimeline(self, time_value):
#         """
#         More simple update just for timeline.
#         """
#
#         for timeline in self.timelines.values():
#             timeline.setValue(time_value)
#
#
# def protocolDockWidget():
#
#     prot_dock = QtGui.QDockWidget("Protocol")
#     prot_list = QtGui.QListWidget(prot_dock)
#     prot_dock.setWidget(prot_list)
#
#
#
# class MainWindow(QtGui.QMainWindow):
#
#
#     seq_dock = QtGui.QDockWidget("Sequence")
#     mag_dock = QtGui.QDockWidget("Magnetization")
#
#
#     plotParameters = pt.parameterTypes.GroupParameter(name='Plot')
#
#     plotSequence = SequencePlot()
#     plotMagnetization = MagnetizationPlot()
#
#     seq_dock.setWidget(plotSequence)
#     mag_dock.setWidget(plotMagnetization)
#
#     plotParameters.addChild(plotSequence.parameters)
#     plotParameters.addChild(plotMagnetization.parameters)
#
#     parameterTree.setParameters(plotParameters, showTop=True)
#
#     param_dock = QtGui.QDockWidget("Parameters")
#
#     param_dock.setWidget(t)
#
#     prot_list_dock = QtGui.QDockWidget("Protocols")
#     seq_list_dock = QtGui.QDockWidget("Sequences")
#
#     window.addDockWidget(QtCore.Qt.RightDockWidgetArea, seq_dock)
#     window.addDockWidget(QtCore.Qt.RightDockWidgetArea, mag_dock)
#     window.addDockWidget(QtCore.Qt.LeftDockWidgetArea, seq_list_dock)
#     window.addDockWidget(QtCore.Qt.LeftDockWidgetArea, prot_list_dock)
#     window.addDockWidget(QtCore.Qt.LeftDockWidgetArea, param_dock)
#     window.tabifyDockWidget(seq_list_dock, prot_list_dock)
#
#     def updatePlots():
#
#         global index
#
#         time_value = tp[index]
#
#         if index > tpsize - index_step:
#             timer.stop()
#             return
#
#         if index == 0:
#             plotSequence.update()
#             plotMagnetization.update()
#
#         plotMagnetization.updateTimeline(time_value)
#         plotSequence.updateTimeline(time_value)
#         index += 1
#
#     # region.sigRegionChanged.connect(updateReg)
#     #region.setRegion([tp[data[0][0]], tp[data[0][-1]]])
#
#     timer = QtCore.QTimer()
#     timer.timeout.connect(update)
#     timer.start(0.1)
#     self.showMaximized()


def plotEverything(mx, my, mz, gr, rf, freq_shift, position, data=np.array(0)):

    global index, DT, index_step, tpsize

    tp = np.arange(0, rf.size) * DT
    # Initiate window
    app = QtGui.QApplication([])
    app.setStyle('cleanlooks')
    window = QtGui.QMainWindow()
    window.setWindowTitle("Bloch Simulator GUI by Daniel Pizetta, Core by Brian Hargreaves, Niraj Amalkanti, Mikki Lustig, NPann")
    labelStyle = {'color': '#EEE', 'font-size': '8pt'}

    voxelSize = 1                 # this is the twice radius of max magnetization
    subVoxelSize = voxelSize / 2.  # this is the sub voxel size

    # options 3D
    show3DWindow = True           # show 3D window
    show3DAxes = True             # show axes
    show3DGrid = False            # show grids - false for a clean visualization
    plot3DVoxel = False           # plot voxel volumn
    plot3DGrad = True             # plot gradient lines
    plot3DOffResMag = True       # plot off resonance magnetization - choose False to improve speed
    plot3DOffResPercentage = 100    # plot off resonance magnetization line quantities - choose a small percentage to improve speed
    plot3DTotalMag = True         # plot total magnetization
    plot3DSubVoxel = True
    plot3DTotalMagZero = True
    # options K Space - FFT

    # options 1D sequence
    show1DSeqWindow = True        # show 1D sequence window
    show1DSeqGrid = False         # show grids
    plot1DSeqRF = True            # plot rf lines
    plot1DSeqRFZero = True        # plot even zero rf lines - chose False to improve speed
    plot1DSeqGrad = True          # plot gradient lines
    plot1DSeqGradZero = True      # plot even zero gradient lines - chose False to improve speed
    plot1DSeqTimeline = True      # plot an timeline for each graph in 1D - chose False to improve speed

    # options 1D magnetization
    show1DMagWindow = True           # show 1D magnetization window
    plot1DMagTotalMag = True         # plot total magnetization
    plot1DMagOffResMag = True       # plot off resonance magnetization - choose False to improve speed
    plot1DMagOffResPercentage = 100    # plot off resonance magnetization line quantities - choose a small percentage to improve speed
    plot1DMagLabRefTotalMagn = False  # plot total magnetization

    # index for animation loop
    index = 0
    # index step for reduction of the frames to increase speed
    index_step = 20
    # frequency shift array size
    fsa_size = freq_shift.size - 1
    # positions array size
    xpa_size = 1
    ypa_size = 1
    zpa_size = 1
    scale = 1

    # spacing in left side, for graph adjust
    leftWidth = 50

    mxtemp, mytemp, mztemp = mx, my, mz

    # reduce and rescale the magnetization
    mx, my, mz = reduceMagnetizationInPosition(mx, my, mz, position, freq_shift)

    # time scale calculation
    tp = tp
    tp_min = np.min(tp)
    tp_max = np.max(tp)
    tpsize = tp.size

    # transversal magnetization
    mxy = mx + 1.0j * my
    mag_mxy = np.absolute(mxy)
    phase_mxy = np.angle(mxy, deg=False)

    gr_max_global = np.max(gr)

    # get all gradients components
    gr_x = gr[0]
    gr_y = gr[1]
    gr_z = gr[2]

    # get all RF components
    rf_am = np.absolute(rf)
    rf_pm = np.angle(rf, deg=False)
    rf_fm = np.gradient(rf_pm, tp[0] - tp[1])

    ################################################################################################
    # Sequence dock
    ################################################################################################

    # create a graph window for sequence visualization
    seq_win = pg.GraphicsWindow()
    pg.setConfigOptions(antialias=True)  # , autoDownsample=True)
    # create a dock widget to put 2d sequence graphs
    seq_dock = QtGui.QDockWidget("Sequence")
    seq_dock.setWidget(seq_win)

    # RF ------------------------------------------------------------------------------------------

    rf_am_plot = seq_win.addPlot(x=tp, y=rf_am, pen='g')
    rf_am_plot_timeline = pg.InfiniteLine(pos=index, angle=90, pen='w', movable=False)
    rf_am_plot.addItem(rf_am_plot_timeline)
    rf_am_plot.setRange(xRange=(tp_min, tp_max))
    rf_am_plot.getAxis('left').setWidth(leftWidth)
    rf_am_plot.showGrid(x=True, y=True, alpha=0.0)
    rf_am_plot.getAxis('bottom').setStyle(showValues=False)
    rf_am_plot.getAxis('top').setStyle(showValues=False)
    rf_am_plot.getAxis('right').setStyle(showValues=False)
    rf_am_plot.showAxis(axis='bottom')
    rf_am_plot.showAxis(axis='top')
    rf_am_plot.showAxis(axis='right')
    rf_am_plot.setLabel(axis='left', text='RF AM', units='G', **labelStyle)
    seq_win.nextRow()

    rf_pm_plot = seq_win.addPlot(x=tp, y=rf_pm, pen='y')
    rf_pm_plot_timeline = pg.InfiniteLine(pos=index, angle=90, pen='c', movable=False)
    rf_pm_plot.addItem(rf_pm_plot_timeline)
    rf_pm_plot.getAxis('left').setWidth(leftWidth)
    rf_pm_plot.showGrid(x=True, y=True, alpha=0.0)
    rf_pm_plot.getAxis('bottom').setStyle(showValues=False)
    rf_pm_plot.getAxis('top').setStyle(showValues=False)
    rf_pm_plot.getAxis('right').setStyle(showValues=False)
    rf_pm_plot.showAxis(axis='bottom')
    rf_pm_plot.showAxis(axis='top')
    rf_pm_plot.showAxis(axis='right')
    rf_pm_plot.setRange(xRange=(tp_min, tp_max))
    rf_pm_plot.getAxis('left').setTicks([[(3.14, chr(960)), (1.57, chr(960) + '/2'), (0.0, '0'), (-3.14, '-' + chr(960)), (-1.57, '-' + chr(960) + '/2')]])
    rf_pm_plot.setLabel(axis='left', text='RF PM', units='Rad', **labelStyle)
    seq_win.nextRow()

    rf_fm_plot = seq_win.addPlot(x=tp, y=rf_fm, pen='r')
    rf_fm_plot_timeline = pg.InfiniteLine(pos=index, angle=90, pen='c', movable=False)
    rf_fm_plot.addItem(rf_fm_plot_timeline)
    rf_fm_plot.getAxis('left').setWidth(leftWidth)
    rf_fm_plot.getAxis('bottom').setStyle(showValues=False)
    rf_fm_plot.getAxis('top').setStyle(showValues=False)
    rf_fm_plot.getAxis('right').setStyle(showValues=False)
    rf_fm_plot.showAxis(axis='bottom')
    rf_fm_plot.showAxis(axis='top')
    rf_fm_plot.showAxis(axis='right')
    rf_fm_plot.showGrid(x=True, y=True, alpha=0.0)
    rf_fm_plot.setRange(xRange=(tp_min, tp_max))
    rf_fm_plot.setLabel(axis='left', text='RF FM', units='Hz', **labelStyle)

    seq_win.nextRow()

    # GRADIENTS -----------------------------------------------------------------------------------------

    gr_x_plot = seq_win.addPlot(x=tp, y=gr_x, pen='g')
    gr_x_plot_timeline = pg.InfiniteLine(pos=index, angle=90, pen='w', movable=False)
    gr_x_plot.addItem(gr_x_plot_timeline)
    gr_x_plot.getAxis('left').setWidth(leftWidth)
    gr_x_plot.showGrid(x=True, y=True, alpha=0.0)
    gr_x_plot.setRange(xRange=(tp_min, tp_max), yRange=(-GR_MAX * 1.01, GR_MAX * 1.01))
    gr_x_plot.setLabel(axis='left', text='Gr X', units='G/cm', **labelStyle)
    gr_x_plot.getAxis('bottom').setStyle(showValues=False)
    gr_x_plot.getAxis('top').setStyle(showValues=False)
    gr_x_plot.getAxis('right').setStyle(showValues=False)
    gr_x_plot.showAxis(axis='top')
    gr_x_plot.showAxis(axis='right')
    seq_win.nextRow()

    gr_y_plot = seq_win.addPlot(x=tp, y=gr_y, pen='y')
    gr_y_plot_timeline = pg.InfiniteLine(pos=index, angle=90, pen='w', movable=False)
    gr_y_plot.addItem(gr_y_plot_timeline)
    gr_y_plot.getAxis('left').setWidth(leftWidth)
    gr_y_plot.showGrid(x=True, y=True, alpha=0.0)
    gr_y_plot.setRange(xRange=(tp_min, tp_max), yRange=(-GR_MAX * 1.01, GR_MAX * 1.01))
    gr_y_plot.setLabel(axis='left', text='Gr Y', units='G/cm', **labelStyle)
    gr_y_plot.getAxis('bottom').setStyle(showValues=False)
    gr_y_plot.getAxis('top').setStyle(showValues=False)
    gr_y_plot.getAxis('right').setStyle(showValues=False)
    gr_y_plot.showAxis(axis='top')
    gr_y_plot.showAxis(axis='right')
    seq_win.nextRow()

    gr_z_plot = seq_win.addPlot(x=tp, y=gr_z, pen='r')
    gr_z_plot_timeline = pg.InfiniteLine(pos=index, angle=90, pen='w', movable=False)
    gr_z_plot.addItem(gr_z_plot_timeline)
    gr_z_plot.getAxis('left').setWidth(leftWidth)
    gr_z_plot.showGrid(x=True, y=True, alpha=0.0)
    gr_z_plot.setRange(xRange=(tp_min, tp_max), yRange=(-GR_MAX * 1.01, GR_MAX * 1.01))
    gr_z_plot.setLabel(axis='left', text='Gr Z', units='G/cm', **labelStyle)
    gr_z_plot.setLabel(axis='bottom', text='Time', units='s', **labelStyle)
    gr_z_plot.getAxis('top').setStyle(showValues=False)
    gr_z_plot.getAxis('right').setStyle(showValues=False)
    gr_z_plot.showAxis(axis='top')
    gr_z_plot.showAxis(axis='right')
    seq_win.nextRow()

    ################################################################################################
    # Magnetization dock
    ################################################################################################

    # create a graph window for magnetization
    mag_win = pg.GraphicsWindow()
    # create a dock widget to put 2d sequence graphs
    mag_dock = QtGui.QDockWidget("Magnetization")
    mag_dock.setWidget(mag_win)

    mx_plot = mag_win.addPlot(x=tp, y=mx, pen='g')
    # mx_plot.plot(x=tp, y=mxfreq[0], pen=(0, 255, 0, 5))
    mx_plot_timeline = pg.InfiniteLine(pos=index, angle=90, pen='w', movable=False)
    mx_plot.addItem(mx_plot_timeline)
    mx_plot.getAxis('left').setWidth(leftWidth)
    mx_plot.showGrid(x=True, y=True, alpha=0.0)
    mx_plot.setRange(xRange=(tp_min, tp_max), yRange=(-1.01, 1.01))
    mx_plot.setLabel(axis='left', text='Mag X - Real', **labelStyle)
    mx_plot.getAxis('bottom').setStyle(showValues=False)
    mx_plot.getAxis('top').setStyle(showValues=False)
    mx_plot.getAxis('right').setStyle(showValues=False)
    mx_plot.showAxis(axis='top')
    mx_plot.showAxis(axis='right')
    mag_win.nextRow()

    my_plot = mag_win.addPlot(x=tp, y=my, pen='y')
    # my_plot.plot(x=tp, y=myfreq[0], pen=(255, 255, 0, 5))
    my_plot_timeline = pg.InfiniteLine(pos=index, angle=90, pen='w', movable=False)
    my_plot.addItem(my_plot_timeline)
    my_plot.getAxis('left').setWidth(leftWidth)
    my_plot.showGrid(x=True, y=True, alpha=0.0)
    my_plot.setRange(xRange=(tp_min, tp_max), yRange=(-1.01, 1.01))
    my_plot.setLabel(axis='left', text='Mag Y - Imag.', **labelStyle)
    my_plot.getAxis('bottom').setStyle(showValues=False)
    my_plot.getAxis('top').setStyle(showValues=False)
    my_plot.getAxis('right').setStyle(showValues=False)
    my_plot.showAxis(axis='top')
    my_plot.showAxis(axis='right')
    mag_win.nextRow()

    mz_plot = mag_win.addPlot(x=tp, y=mz, pen='r')
    # mz_plot.plot(x=tp, y=mzfreq, pen=(255, 0, 0, 5))
    mz_plot_timeline = pg.InfiniteLine(pos=index, angle=90, pen='w', movable=False)
    mz_plot.addItem(mz_plot_timeline)
    mz_plot.getAxis('left').setWidth(leftWidth)
    mz_plot.getAxis('left').setWidth(leftWidth)
    mz_plot.showGrid(x=True, y=True, alpha=0.0)
    mz_plot.setRange(xRange=(tp_min, tp_max), yRange=(-1.01, 1.01))
    mz_plot.setLabel(axis='left', text='Mag Z', **labelStyle)
    mz_plot.getAxis('bottom').setStyle(showValues=False)
    mz_plot.getAxis('top').setStyle(showValues=False)
    mz_plot.getAxis('right').setStyle(showValues=False)
    mz_plot.showAxis(axis='top')
    mz_plot.showAxis(axis='right')
    mag_win.nextRow()

    mag_mxy_plot = mag_win.addPlot(x=tp, y=mag_mxy, pen='c')
    mag_mxy_plot_timeline = pg.InfiniteLine(pos=index, angle=90, pen='w', movable=False)
    mag_mxy_plot.addItem(mag_mxy_plot_timeline)
    mag_mxy_plot.setRange(xRange=(tp_min, tp_max), yRange=(-0.01, 1.01))
    mag_mxy_plot.getAxis('left').setWidth(leftWidth)
    mag_mxy_plot.showGrid(x=True, y=True, alpha=0.0)
    mag_mxy_plot.setLabel(axis='left', text='Mag Tranv', **labelStyle)
    mag_mxy_plot.getAxis('bottom').setStyle(showValues=False, tickTextHeight=0)
    mag_mxy_plot.getAxis('top').setStyle(showValues=False, tickTextHeight=0)
    mag_mxy_plot.getAxis('right').setStyle(showValues=False)
    mag_mxy_plot.showAxis(axis='top')
    mag_mxy_plot.showAxis(axis='right')
    mag_win.nextRow()

    phase_mxy_plot = mag_win.addPlot(x=tp, y=phase_mxy, pen='c')
    phase_mxy_plot_timeline = pg.InfiniteLine(pos=index, angle=90, pen='w', movable=False)
    phase_mxy_plot.addItem(phase_mxy_plot_timeline)
    phase_mxy_plot.getAxis('left').setWidth(leftWidth)
    phase_mxy_plot.setRange(xRange=(tp_min, tp_max))
    phase_mxy_plot.showGrid(x=True, y=True, alpha=0.0)
    phase_mxy_plot.getAxis('left').setTicks([[(3.14, chr(960)), (1.57, chr(960) + '/2'), (0.0, '0'), (-3.14, '-' + chr(960)), (-1.57, '-' + chr(960) + '/2')]])
    phase_mxy_plot.setLabel(axis='left', text='Phase', **labelStyle)
    phase_mxy_plot.setLabel(axis='bottom', text='Time', units='s', **labelStyle)
    phase_mxy_plot.getAxis('top').hide()
    phase_mxy_plot.getAxis('top').setStyle(showValues=False)
    phase_mxy_plot.getAxis('right').setStyle(showValues=False)
    phase_mxy_plot.showAxis(axis='top')
    phase_mxy_plot.showAxis(axis='right')

    # create a temp copy of magnetization
    mx, my, mz = mxtemp, mytemp, mztemp

    # create a 3d view
    view = gl.GLViewWidget()
    max_abs_pos = np.max([np.abs(np.min(position)), np.max(position)]) + 1
    view.setCameraPosition(distance=max_abs_pos * 2)

    # show lines for each axis centered in 0,0,0
    if show3DAxes:

        # create axis lines for each axis
        xline = gl.GLLinePlotItem(pos=np.array([-max_abs_pos, 0, 0, max_abs_pos, 0, 0]).reshape(2, 3), color=(0, 255, 0, 1), antialias=True)
        xline.setGLOptions('additive')
        yline = gl.GLLinePlotItem(pos=np.array([0, -max_abs_pos, 0, 0, max_abs_pos, 0]).reshape(2, 3), color=(255, 255, 0, 1), antialias=True)
        yline.setGLOptions('additive')
        zline = gl.GLLinePlotItem(pos=np.array([0, 0, -max_abs_pos, 0, 0, max_abs_pos]).reshape(2, 3), color=(255, 0, 0, 1), antialias=True)
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
    if show3DGrid:
        # create grid for each axis
        xgrid = gl.GLGridItem(color=(255, 255, 255, 0.01))
        xgrid.setGLOptions('additive')
        ygrid = gl.GLGridItem(color=(255, 255, 255, 0.01))
        ygrid.setGLOptions('additive')

        xgrid.setDepthValue(10)
        ygrid.setDepthValue(10)
        # add grids to the view
        view.addItem(xgrid)
        view.addItem(ygrid)

        # rotate x and y grids to face the correct direction
        xgrid.rotate(90, 0, 1, 0)
        ygrid.rotate(90, 1, 0, 0)
    zgrid = gl.GLGridItem(color=(255, 255, 255, 0.01))
    zgrid.setGLOptions('additive')
    # draw grid after surfaces since they may be translucent

    zgrid.setDepthValue(10)
    view.addItem(zgrid)
    mag_sum = []
    mag_pos = []
    mag_neg = []
    mag_zero = []
    grad_x = []
    grad_y = []
    grad_z = []
    voxels = []
    subvoxels = []
    index_pos = 0

    mag_negs = []
    mag_poss = []
    # sum the frequency components
    mx_sum_fs, my_sum_fs, mz_sum_fs = reduceMagnetizationInFrequency(mx, my, mz, freq_shift, freq_shift.size)

    for x_pos, y_pos, z_pos in list(zip(position[0], position[1], position[2])):

        # show spheres that represent a voxel for each voxel in position - this is static
        if plot3DVoxel:
            voxels.append(gl.GLMeshItem(meshdata=gl.MeshData.sphere(rows=10, cols=10), smooth=False, drawFaces=True, drawEdges=False, color=(255, 255, 255, 0.02)))
            voxels[index_pos].translate(x_pos, y_pos, z_pos)
            voxels[index_pos].setGLOptions('additive')
            view.addItem(voxels[index_pos])

        # show spheres that represent a voxel for each voxel in position - this is static
        if plot3DSubVoxel:
            subvoxels.append(gl.GLScatterPlotItem(pos=np.array([x_pos, y_pos, z_pos]), size=2., color=(255, 0, 0, 1.)))
            subvoxels[index_pos].setGLOptions('additive')
            view.addItem(subvoxels[index_pos])

        # create lines that represents the gradients - this is dymanic
        if plot3DGrad:
            grad_x.append(gl.GLLinePlotItem(pos=np.array([x_pos, y_pos, z_pos, x_pos, y_pos, z_pos]).reshape(2, 3), color=(0, 255, 0, 0.5), antialias=True, mode='lines', width=1))
            grad_y.append(gl.GLLinePlotItem(pos=np.array([x_pos, y_pos, z_pos, x_pos, y_pos, z_pos]).reshape(2, 3), color=(255, 255, 0, 0.5), antialias=True, mode='lines', width=1))
            grad_z.append(gl.GLLinePlotItem(pos=np.array([x_pos, y_pos, z_pos, x_pos, y_pos, z_pos]).reshape(2, 3), color=(255, 0, 0, 0.5), antialias=True, mode='lines', width=1))
            view.addItem(grad_x[index_pos])
            view.addItem(grad_y[index_pos])
            view.addItem(grad_z[index_pos])

        # create lines that represents the magnetization, show the summation, max and min freq shift - this is dymanic
        if plot3DTotalMag:
            mag_sum.append(gl.GLLinePlotItem(pos=np.array([x_pos, y_pos, z_pos, x_pos, y_pos, z_pos]).reshape(2, 3), color=pg.glColor(255, 255, 255), antialias=True, mode='lines', width=5))
            view.addItem(mag_sum[index_pos])

        if plot3DTotalMagZero:
            if (fsa_size >= 1):
                # for more than one dimension, because of the return of the bloch function
                if position.shape[1] != 1:
                    mag_zero.append(gl.GLLinePlotItem(pos=np.array([x_pos, y_pos, z_pos, x_pos + mx_sum_fs[index_pos][0] * scale, y_pos + my_sum_fs[index_pos][0] * scale, z_pos + mz_sum_fs[index_pos][0] * scale]).reshape(2, 3), color=(255, 0, 0, 0.3), antialias=True, mode='lines', width=5))
                else:
                    mag_zero.append(gl.GLLinePlotItem(pos=np.array([x_pos, y_pos, z_pos, x_pos + mx_sum_fs[0] * scale, y_pos + my_sum_fs[0] * scale, z_pos + mz_sum_fs[0] * scale]).reshape(2, 3), color=(255, 0, 0, 0.3), antialias=True, mode='lines', width=5))
            else:
                mag_zero.append(gl.GLLinePlotItem(pos=np.array([x_pos, y_pos, z_pos, x_pos + mx_sum_fs[0] * scale, y_pos + my_sum_fs[0] * scale, z_pos + mz_sum_fs[0] * scale]).reshape(2, 3), color=(255, 0, 0, 0.3), antialias=True, mode='lines', width=5))
            view.addItem(mag_zero[index_pos])

        if (fsa_size >= 1) and plot3DOffResMag:
            # for orl in range(0, int((plot3DOffResPercentage / 100.) * (fsa_size - 1) / 2.) + 1):
                #orl = 0
            mag_neg.append(gl.GLLinePlotItem(pos=np.array([x_pos, y_pos, z_pos, x_pos, y_pos, z_pos]).reshape(2, 3), color=(0, 255, 255, 0.3), antialias=True, mode='lines', width=5))
            mag_pos.append(gl.GLLinePlotItem(pos=np.array([x_pos, y_pos, z_pos, x_pos, y_pos, z_pos]).reshape(2, 3), color=(255, 0, 255, 0.3), antialias=True, mode='lines', width=5))
            # must be 2d vector
            # mag_neg.append(mag_neg)
            # mag_pos.append(mag_pos)
            view.addItem(mag_pos[index_pos])
            view.addItem(mag_neg[index_pos])

        index_pos += 1

    view3D_dock = QtGui.QDockWidget("3D Spin View")
    view3D_dock.setWidget(view)

    window.addDockWidget(QtCore.Qt.LeftDockWidgetArea, seq_dock)
    window.addDockWidget(QtCore.Qt.LeftDockWidgetArea, mag_dock)
    window.addDockWidget(QtCore.Qt.RightDockWidgetArea, view3D_dock)

    # create a dock widget to put 1d kx, ky, x, y graphs
    if len(data.shape) == 1:
        print("lenn", len(data.shape))
        #region = pg.LinearRegionItem()
        # region.setZValue(10)
        #mag_mxy_plot.addItem(region, ignoreBounds=True)
        #mxy_transposed = mxy.T

        beg, end = 0, data.real.size

        # complex fft
        data_fft = np.fft.ifft(data)
        # magnitude fft
        data_fft_abs = np.absolute(data_fft)
        data_fft_phase = np.angle(data_fft)
        # magnitude
        data_abs = np.absolute(data)
        data_phase = np.angle(data)

        print("data_abs.shape: ", data_abs.shape)
        print("beg, end: ", beg, end)

        kxky_xy_win = pg.GraphicsWindow()
        pg.setConfigOptions(antialias=True)

        # plot k space
#         kspace_abs_plot = kxky_xy_win.addPlot(x=tp[beg:end], y=data_abs, row=0, col=0, pen='b')
#         kspace_abs_plot.showGrid(x=True, y=True, alpha=0.7)
#         kspace_abs_plot.setLabel(axis='left', text='Magnitude', **labelStyle)
#         kspace_abs_plot.setLabel(axis='bottom', text='Time', units='s', **labelStyle)

#         kspace_phase_plot = kxky_xy_win.addPlot(x=tp[beg:end], y=data_phase, row=1, col=0, pen='b')
#         kspace_phase_plot.showGrid(x=True, y=True, alpha=0.7)
#         kspace_phase_plot.setLabel(axis='left', text='Phase', **labelStyle)
#         kspace_phase_plot.setLabel(axis='bottom', text='Time', units='s', **labelStyle)
#
#         kspace_real_plot = kxky_xy_win.addPlot(x=tp[beg:end], y=data.real, row=2, col=0, pen='g')
#         kspace_real_plot.showGrid(x=True, y=True, alpha=0.7)
#         kspace_real_plot.setLabel(axis='left', text='Real', **labelStyle)
#         kspace_real_plot.setLabel(axis='bottom', text='Time', units='s', **labelStyle)
#
#         kspace_imag_plot = kxky_xy_win.addPlot(x=tp[beg:end], y=data.imag, row=3, col=0, pen='y')
#         kspace_imag_plot.showGrid(x=True, y=True, alpha=0.7)
#         kspace_imag_plot.setLabel(axis='left', text='Imaginary', **labelStyle)
#         kspace_imag_plot.setLabel(axis='bottom', text='Time', units='s', **labelStyle)

        # plot fft from k space

        fft_abs_plot = kxky_xy_win.addPlot(x=tp[beg:end], y=data_fft_abs, row=0, col=1, pen='c')
        fft_abs_plot.showGrid(x=True, y=True, alpha=0.7)
        fft_abs_plot.setLabel(axis='left', text='Magnitude', **labelStyle)
        fft_abs_plot.setLabel(axis='bottom', text='Frequency', **labelStyle)

#         fft_phase_plot = kxky_xy_win.addPlot(x=tp[beg:end], y=data_fft_phase, row=1, col=1, pen='b')
#         fft_phase_plot.showGrid(x=True, y=True, alpha=0.7)
#         fft_phase_plot.setLabel(axis='left', text='Phase', **labelStyle)
#         fft_phase_plot.setLabel(axis='bottom', text='Frequency', units='Hz', **labelStyle)
#
#         fft_real_plot = kxky_xy_win.addPlot(x=tp[beg:end], y=data_fft.real, row=2, col=1, pen='g')
#         fft_real_plot.showGrid(x=True, y=True, alpha=0.7)
#         fft_real_plot.setLabel(axis='left', text='Real', **labelStyle)
#         fft_real_plot.setLabel(axis='bottom', text='Frequency', units='Hz', **labelStyle)
#
#         fft_imag_plot = kxky_xy_win.addPlot(x=tp[beg:end], y=data_fft.imag, row=3, col=1, pen='y')
#         fft_imag_plot.showGrid(x=True, y=True, alpha=0.7)
#         fft_imag_plot.setLabel(axis='left', text='Imaginary', **labelStyle)
#         fft_imag_plot.setLabel(axis='bottom', text='Frequency', units='Hz', **labelStyle)

        kxky_xy_dock = QtGui.QDockWidget("K space - Fourier Transform")
        kxky_xy_dock.setWidget(kxky_xy_win)
        window.addDockWidget(QtCore.Qt.RightDockWidgetArea, kxky_xy_dock)
        # kxky_xy_dock.setFloating(True)
        window.tabifyDockWidget(mag_dock, kxky_xy_dock)

    if len(data.shape) == 2 and data.shape[0] >= 1:

        print("data_shape: ", data.shape)
        #region = pg.LinearRegionItem()
        # region.setZValue(10)
        #mag_mxy_plot.addItem(region, ignoreBounds=True)
        #more = data.size-8192*2
        # np.zeros(more).reshape(data.shape[0], data.shape.)
        # complex fft
        data_fft = np.fft.ifft2(data)
        # magnitude fft
        data_fft_abs = np.absolute(data_fft)
        # magnitude
        data_abs = np.absolute(data)

        kxky_xy_win = pg.ImageView()
        kxky_xy_win.setImage((data_fft_abs.T * 255).astype(int))
        kxky_xy_dock = QtGui.QDockWidget("K space - Fourier Transform")
        kxky_xy_dock.setWidget(kxky_xy_win)
        window.addDockWidget(QtCore.Qt.RightDockWidgetArea, kxky_xy_dock)
        window.tabifyDockWidget(mag_dock, kxky_xy_dock)

    # def updateReg():

        # region.setZValue(10)
        #minX, maxX = region.getRegion()
        #kspace_abs_plot.setXRange(minX, maxX, padding=0)
        #kspace_real_plot.setXRange(minX, maxX, padding=0)
        #kspace_imag_plot.setXRange(minX, maxX, padding=0)

    def update():

        global index, index_step, tpsize

        index_pos = 0

        if index > tpsize - index_step:
            timer.stop()
            return

        for x_pos, y_pos, z_pos in list(zip(position[0], position[1], position[2])):

            # update off resonance magnetization for each time point
            if plot3DOffResMag:
                if fsa_size >= 1:
                    orl = 0
                    # for more than one dimension, because of the return of the bloch function
                    if position.shape[1] != 1:
                        # for orl in range(0, int((plot3DOffResPercentage / 100.) * (fsa_size - 1) / 2.) + 1):
                        mag_neg[index_pos].setData(pos=np.array([x_pos, y_pos, z_pos, x_pos + mx[0 + orl][index_pos][index] * scale, y_pos + my[0 + orl][index_pos][index] * scale, z_pos + mz[0 + orl][index_pos][index] * scale]).reshape(2, 3))
                        mag_pos[index_pos].setData(pos=np.array([x_pos, y_pos, z_pos, x_pos + mx[fsa_size - orl][index_pos][index] * scale, y_pos + my[fsa_size - orl][index_pos][index] * scale, z_pos + mz[fsa_size - orl][index_pos][index] * scale]).reshape(2, 3))
                    else:
                        # for orl in range(0, int((plot3DOffResPercentage / 100.) * (fsa_size - 1) / 2.) + 1):
                        mag_neg[index_pos].setData(pos=np.array([x_pos, y_pos, z_pos, x_pos + mx[0 + orl][index] * scale, y_pos + my[0 + orl][index] * scale, z_pos + mz[0 + orl][index] * scale]).reshape(2, 3))
                        mag_pos[index_pos].setData(pos=np.array([x_pos, y_pos, z_pos, x_pos + mx[fsa_size - orl][index] * scale, y_pos + my[fsa_size - orl][index] * scale, z_pos + mz[fsa_size - orl][index] * scale]).reshape(2, 3))

            # update total magnetization for each time point
            if plot3DTotalMag:
                if (fsa_size >= 1):
                    # for more than one dimension, because of the return of the bloch function
                    if position.shape[1] != 1:
                        mag_sum[index_pos].setData(pos=np.array([x_pos, y_pos, z_pos, x_pos + mx_sum_fs[index_pos][index] * scale, y_pos + my_sum_fs[index_pos][index] * scale, z_pos + mz_sum_fs[index_pos][index] * scale]).reshape(2, 3))
                    else:
                        mag_sum[index_pos].setData(pos=np.array([x_pos, y_pos, z_pos, x_pos + mx_sum_fs[index] * scale, y_pos + my_sum_fs[index] * scale, z_pos + mz_sum_fs[index] * scale]).reshape(2, 3))
                else:
                    mag_sum[index_pos].setData(pos=np.array([x_pos, y_pos, z_pos, x_pos + mx_sum_fs[index] * scale, y_pos + my_sum_fs[index] * scale, z_pos + mz_sum_fs[index] * scale]).reshape(2, 3))

            # update gradients for each time point
            if plot3DGrad:
                grad_x[index_pos].setData(pos=np.array([x_pos, 0, 0, x_pos, 0, x_pos * gr[0][index] / gr_max_global]).reshape(2, 3))
                grad_y[index_pos].setData(pos=np.array([0, y_pos, 0, 0, y_pos, y_pos * gr[1][index] / gr_max_global]).reshape(2, 3))
                grad_z[index_pos].setData(pos=np.array([0, 0, z_pos, 0, 0, z_pos + z_pos * gr[2][index] / gr_max_global]).reshape(2, 3))

            index_pos += 1

        # update timeline in 2d graphics
        gr_x_plot_timeline.setValue(tp[index])
        gr_y_plot_timeline.setValue(tp[index])
        gr_z_plot_timeline.setValue(tp[index])
        rf_am_plot_timeline.setValue(tp[index])
        rf_pm_plot_timeline.setValue(tp[index])
        rf_fm_plot_timeline.setValue(tp[index])
        mx_plot_timeline.setValue(tp[index])
        my_plot_timeline.setValue(tp[index])
        mz_plot_timeline.setValue(tp[index])
        mag_mxy_plot_timeline.setValue(tp[index])
        phase_mxy_plot_timeline.setValue(tp[index])
        index += index_step

    # region.sigRegionChanged.connect(updateReg)
    #region.setRegion([tp[data[0][0]], tp[data[0][-1]]])

    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(0.01)
    window.showMaximized()
    app.exec_()
