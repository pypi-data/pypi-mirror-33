#! python
# -*- coding: utf-8 -*-


import logging
import os

import h5py
import numpy as np
from pyqtgraph.parametertree import Parameter

from bloch.simulator import evolve
from mrsprint.globals import DT, GAMMA, GR_MAX
from mrsprint.plot import plotEverything
from mrsprint.sequence import sequence
from mrsprint.simulator import (calculateT2Star, createPositions,
                                  frequencyShift,
                                  reduceMagnetizationInPosition)
from mrsprint.system.rf import rf_delay, rf_duration, square_rf_pulse

_logger = logging.getLogger(__name__)


def simple_fid():
    """Simple free induction decay (FID).

    Just rf and gradient are essential for the fid code.

    Todo:
        May accept the constants as parameters.
        May return parameters for bloch.evolve().
    """

    mode = 2           # [#]
    freq_shift = 250.  # [Hz]
    freq_step = 2.     # [Hz]
    freq_offset = 0.   # [Hz]
    t1 = 0.5           # [s]
    t2 = .01           # [s]

    _logger.debug("in %s", locals())

    # position setup
    position = createPositions(size=(2, 1, 1), step=(2, 1, 1), offset=(0, 0, 0))
    # frequency and t2 star setup
    freq_shift = frequencyShift(freq_shift, freq_step, offset=freq_offset)
    t2star = calculateT2Star(t2, freq_shift)
    # time to echo
    te = t2star * 5
    # rf setup
    p90x = square_rf_pulse(90, 0)
    dte = rf_delay(te)
    rf = np.concatenate((p90x, dte))
    # gradient setup
    gr = np.zeros((3, rf.size))

    mx, my, mz = evolve(rf, gr, DT, t1, t2, freq_shift, position, mode)
    plotEverything(mx, my, mz, gr, rf, freq_shift, position)


def simple_cpmg():
    """
    Simple Carr-Purcell-Meiboom-Gill (CPMG).
    It allows to measure transverse or spin-spin T2 relaxation times.
    """

    mode = 2
    freq_shift = 120.
    freq_step = 2.
    freq_offset = 0.
    t1 = 1.
    t2 = .100

    _logger.debug("in %s", locals())

    # position setup
    position = createPositions(size=(20, 1, 1), step=(2, 1, 1), offset=(0, 0, 0))
    # frequency and t2 star setup
    freq_shift = frequencyShift(freq_shift, freq_step, offset=freq_offset)
    t2star = calculateT2Star(t2, freq_shift)
    # sequence setup
    seq = sequence.CPMGSequence()
    parameters = Parameter.create(name='params', type='group', children=[seq])
    rf = seq.getRF()
    gr = seq.getGradient()
    # calculate magnetization, m0 is mz = 1, mx = my = 0
    mx, my, mz = evolve(rf, gr, DT, t1, t2, freq_shift, position, mode)
    plotEverything(mx, my, mz, gr, rf, freq_shift, position)


def cpmg_seven_pulses():
    """
    Test that generates a CPMG sequence.
    """

    mode = 2
    freq_shift = 256.
    freq_step = 64.
    freq_offset = 0.
    t1 = 1.
    t2 = .100

    _logger.debug("in %s", locals())

    # position setup
    position = createPositions(size=(20, 1, 1), step=(2, 1, 1), offset=(0, 0, 0))
    # frequency and t2 star setup
    freq_shift = frequencyShift(freq_shift, freq_step, offset=freq_offset)
    t2star = calculateT2Star(t2, freq_shift)
    # time to echo
    te = t2star * 5
    # pulse of 90 degrees in x
    p90x = square_rf_pulse(90, 0)
    tp90 = rf_duration(p90x)
    # pulse of 180 degrees in y
    p180y = square_rf_pulse(180, 90)
    tp180 = rf_duration(p180y)
    # delay bewteen pulse 90x and 180y  = te/2 between pulse centers
    d90_180 = rf_delay(-tp90 / 2. + te / 2. - tp180 / 2.)
    # delay bewteen pulse 180y and 180y  = te between pulse centers
    d180_180 = rf_delay(-tp180 / 2. + te - tp180 / 2.)

    # rf for CPMG sequence composed
    rf = np.concatenate((np.zeros(500),
                         p90x, d90_180,
                         -p180y, d180_180,
                         p180y, d180_180,
                         -p180y, d180_180,
                         p180y, d180_180,
                         -p180y, d180_180,
                         p180y, d180_180))

    # gradients for CMPG = 0
    gr = np.zeros((3, rf.size))

    # calculate magnetization, m0 is mz = 1, mx = my = 0
    mx, my, mz = evolve(rf, gr, DT, t1, t2, freq_shift, position, mode)
    plotEverything(mx, my, mz, gr, rf, freq_shift, position)


def gradient_echo_phase_enc_1d_x_new():
    """
    Gradient echo sequence.
    """

    mode = 2
    freq_shift_max = 125
    freq_step = 1
    freq_offset = 0
    t1 = 1.
    t2 = .100

    _logger.debug("in %s", locals())

    position = createPositions(size=(4.8, 1, 1), step=(0.2, 1, 1), offset=(0.2, 0, 0))

    freq_shift = frequencyShift(freq_shift_max, freq_step, freq_offset)
    t2star = calculateT2Star(t2, freq_shift)
    te = t2star

    seq = sequence.CPMGSequence()
    parameters = Parameter.create(name='params', type='group', children=[seq])
    rf = seq.getRF()
    gr = seq.getGradient()

    # pulse 90 degrees in y
    p90y = square_rf_pulse(90, 0)
    d90 = rf_delay(rf_duration(p90y))
    # delay time to echo
    dte2 = rf_delay(te / 2.)
    # rf pulse sequence
    rf = np.concatenate((np.zeros(100), p90y, dte2, dte2, dte2, dte2, dte2, dte2))
    grx = np.concatenate((np.zeros(100), d90.real, dte2.real, dte2.real - 1, dte2.real + 1, dte2.real + 1, dte2.real, dte2.real))
    grx_read = np.concatenate((np.zeros(100), d90.real, dte2.real, dte2.real, dte2.real + 1, dte2.real + 1, dte2.real, dte2.real))
    # index from start read gradient to the end of it
    points_to_read = np.nonzero(grx_read)[0]
    # 3d gradient
    gr = np.concatenate((grx, np.zeros(grx.size), np.zeros(grx.size))).reshape(3, grx.size) * GR_MAX
    freq_shift_max = 250

    nvoxels = position.shape[1]
    readout_array = np.zeros((points_to_read.size), dtype=complex)

    print("nvoxels: ", nvoxels)
    print("points_to_read.shape: ", points_to_read.shape, " From ", points_to_read[0], " to ", points_to_read[-1])
    print("readout_array.shape: ", readout_array.shape)

    mx0 = np.zeros(nvoxels * (freq_shift_max - 1)).reshape(freq_shift_max - 1, nvoxels)
    my0 = mx0
    mzi = np.zeros(nvoxels)
    mzi[30:31] = 2.
    mzi[21:23] = 3.
    mzi[nvoxels - 1:nvoxels] = 1.
    mzi[0:3] = 1.
    mz0 = np.zeros(nvoxels * (freq_shift_max - 1)).reshape(freq_shift_max - 1, nvoxels)

    for i in np.arange(0, freq_shift_max - 1):
        mz0[int(i)] = mzi

    mx, my, mz = evolve(rf, gr, DT, t1, t2, freq_shift, position, mode, mx0, my0, mz0)
    mxf, myf, mzf = reduceMagnetizationInPosition(mx, my, mz, position, freq_shift)
    mxy = mxf + 1.0j * myf
    cra = mxy[points_to_read[0]:points_to_read[-1] + 1]

    print("readout,shape", readout_array.shape)
    plotEverything(mx, my, mz, gr, rf, freq_shift, position, cra)


def gradient_echo_phase_enc():
    """
    Gradient echo sequence.
    """

    mode = 2
    freq_shift_max = 36
    freq_step = 1
    t1 = 1.
    t2 = .100

    _logger.debug("in %s", locals())

    position = createPositions(size=(4.8, 4.8, 1), step=(0.8, 0.8, 1), offset=(0.2, 0.2, 0))

    freq_shift = frequencyShift(freq_shift_max, freq_step)
    t2star = calculateT2Star(t2, freq_shift)
    te = t2star

    # pulse 90 degrees in y
    p90y = square_rf_pulse(90, 0)
    d90 = rf_delay(rf_duration(p90y))
    # delay time to echo
    dte = rf_delay(te)
    dte2 = rf_delay(te / 2.)
    grx = square_rf_pulse(180, 0)

    # rf pulse sequence
    rf = np.concatenate((np.zeros(100), p90y, dte2, dte2, dte2, dte2, dte2, dte2))
    grx = np.concatenate((np.zeros(100), d90.real, dte2.real, dte2.real - 1, dte2.real + 1, dte2.real + 1, dte2.real, dte2.real))
    gry = np.concatenate((np.zeros(100), d90.real, dte2.real, dte2.real + 1, dte2.real, dte2.real, dte2.real, dte2.real))
    grx_read = np.concatenate((np.zeros(100), d90.real, dte2.real, dte2.real, dte2.real + 1, dte2.real + 1, dte2.real, dte2.real))
    # index from start read gradient to the end of it
    points_to_read = np.nonzero(grx_read)[0]
    # 3d gradient
    gr = np.concatenate((grx, gry, np.zeros(grx.size))).reshape(3, grx.size) * GR_MAX
    freq_shift_max = 250

    phase_encs = 12
    phase_enc = 0
    nvoxels = position.shape[1]
    readout_array = np.zeros((phase_encs, phase_encs), dtype=complex)

    print("nvoxels: ", nvoxels)
    print("phase_enc: ", phase_encs)
    print("points_to_read.shape: ", points_to_read.shape, " From ", points_to_read[0], " to ", points_to_read[-1])
    print("readout_array.shape: ", readout_array.shape)

    mx0 = np.zeros(nvoxels * (freq_shift_max - 1)).reshape(freq_shift_max - 1, nvoxels)
    my0 = mx0
    mzi = np.ones(nvoxels)
    mzi[3] = 2
    mzi[6] = 2
    mzi[11] = 0
    mzi[15] = 0
    mzi[9] = 1
    mzi[12] = 1
    mzi[0] = 0

    mz0 = np.zeros(nvoxels * (freq_shift_max - 1)).reshape(freq_shift_max - 1, nvoxels)

    for i in np.arange(0, freq_shift_max - 1):
        mz0[int(i)] = mzi

    print("mag_zero.shape: ", mx0.shape)
    print("mag_z.shape: ", mz0.shape)

    for grady in np.linspace(0, 1., phase_encs):
        # create a new phase gradient
        gr[1][:] = gry * grady * GR_MAX * 0.1
        print("Current phase encoding: ", phase_enc + 1, " of ", phase_encs, "with grady = ", grady)
        # colocar um erro na função bloch caso mx0, my0 ou mz0 não tenham as dimensoes corretas,
        # ele ignora e nao avisa, duas hrs pra encontrar isso
        print("bef mag_zero.shape: ", mx0.shape)
        print("bef mag_z.shape: ", mz0.shape)
        mx, my, mz = evolve(rf, gr, DT, t1, t2, freq_shift, position, 2, mx0, my0, mz0)
        print("aft mag_zero.shape: ", mx.shape)
        print("aft mag_z.shape: ", mz.shape)
        mxf, myf, mzf = reduceMagnetizationInPosition(mx, my, mz, position, freq_shift)
        print("mxf.shape: ", mxf.shape)
        mxy = mxf + 1.0j * myf
        cra = mxy[points_to_read[0]:points_to_read[-1] + 1]
        print("cra", cra.shape)
        readout_array[phase_enc] = cra[int(cra.size / 2) - int(phase_encs / 2): int(cra.size / 2) + int(phase_encs / 2)]
        #plotEverything(tp, mx, my, mz, gr, rf, freq_shift, position, cra[int(cra.size / 2) - 1024 / 2:int(cra.size / 2) + 1024 / 2])
        phase_enc += 1
    print("readout,shape", readout_array.shape)
    plotEverything(mx, my, mz, gr, rf, freq_shift, position, readout_array)


def gradient_echo_phase_enc_1d_x():
    """
    Test for gradient echo sequence.
    """

    mode = 2
    freq_shift_max = 200  # +-10MHz          125
    freq_step = 1         # Passos de 5kHz   1
    t1 = 1.
    t2 = .100

    _logger.debug("in %s", locals())

    freq_shift = frequencyShift(freq_shift_max, freq_step)
    # FOV = 700nm*8pixels = 5600 nm - = 0.00056cm
    # STEP = 100 nm (cada voxel tem tres itens de magnetizacao - seria como intravoxel)
    # como a magnatizacao nao tem dimensao espacial, coloquei 3 para representar um voxel o que seria
    # o intravoxel, soh para ter uma dimensao comparada com o espacamento
    position = createPositions(size=(0.0275, 1, 1), step=(0.001, 1, 1), offset=(0.0, 0, 0))
    print(position.shape)
    t2star = calculateT2Star(t2, freq_shift)
    te = t2star

    # pulse 90 degrees in y
    p90y = square_rf_pulse(90, 0)
    d90 = rf_delay(rf_duration(p90y))
    # delay time to echo
    dte2 = rf_delay(te / 2.)
    # rf pulse sequence
    rf = np.concatenate((p90y, dte2, dte2, dte2, dte2, dte2, dte2))
    grx = np.concatenate((d90.real, dte2.real, dte2.real - 1, dte2.real + 1, dte2.real + 1, dte2.real, dte2.real))
    grx_read = np.concatenate((d90.real, dte2.real, dte2.real, dte2.real + 1, dte2.real + 1, dte2.real, dte2.real))
    # index from start read gradient to the end of it
    points_to_read = np.nonzero(grx_read)[0]
    # 3d gradient
    gr = np.concatenate((grx, np.zeros(grx.size), np.zeros(grx.size))).reshape(3, grx.size) * GR_MAX
    freq_shift_max = freq_shift.shape[0] + 1  # 20Mhz total      250

    nvoxels = position.shape[1]
    readout_array = np.zeros((points_to_read.size), dtype=complex)

    print("nvoxels: ", nvoxels)
    print("points_to_read.shape: ", points_to_read.shape, " From ", points_to_read[0], " to ", points_to_read[-1])
    print("readout_array.shape: ", readout_array.shape)

    mx0 = np.zeros(nvoxels * (freq_shift_max - 1)).reshape(freq_shift_max - 1, nvoxels)
    my0 = mx0

    beg_vox = 0
    beg_spa = 3
    vox_spa = 7

    mz0 = np.zeros(7)
    mz0[0:3] = 1
    mz0[3:8] = 0
    mzi = np.zeros(0)

    for vox_spa in np.arange(0, 4):
        mzi = np.append(mzi, mz0)

    print("MZIIII SHAPE ", mzi.shape)

    mz0 = np.zeros(nvoxels * (freq_shift_max - 1)).reshape(freq_shift_max - 1, nvoxels)

    for i in np.arange(0, freq_shift_max - 1):
        mz0[int(i)] = mzi

    # colocar um erro na função bloch caso mx0, my0 ou mz0 não tenham as dimensoes corretas,
    # ele ignora e nao avisa, duas hrs pra encontrar isso

    print(mx0.shape, my0.shape, mz0.shape)
    mx, my, mz = evolve(rf, gr, DT, t1, t2, freq_shift, position, 2, mx0, my0, mz0)
    mxf, myf, mzf = reduceMagnetizationInPosition(mx, my, mz, position, freq_shift)
    mxy = mxf + 1.0j * myf
    cra = mxy[points_to_read[0]:points_to_read[-1] + 1]
    print("readout,shape", readout_array.shape)
    plotEverything(mx, my, mz, gr, rf, freq_shift, position, cra)


def spin_echo():
    """
    Test for spin echo sequence.
    """

    mode = 2
    freq_shift = 120.
    freq_step = 2.
    freq_offset = 0.
    t1 = 1.
    t2 = .100

    _logger.debug("in %s", locals())

    position = createPositions(size=(2, 1, 1), step=(2, 1, 1), offset=(0, 0, 0))

    freq_shift = frequencyShift(freq_shift, freq_step, offset=freq_offset)
    t2star = calculateT2Star(t2, freq_shift)

    te = t2star * 10

    p90x = square_rf_pulse(90, 0.)
    d90 = rf_delay(te / 2. - rf_duration(p90x) * 3. / 2.)

    p180y = square_rf_pulse(180, 90)
    d180 = rf_delay(te - rf_duration(p90x))

    rf = np.concatenate((np.zeros(500), p90x, d90, p180y, d180))
    gr = np.zeros((3, rf.size))

    mx, my, mz = evolve(rf, gr, DT, t1, t2, freq_shift, position, mode)
    plotEverything(mx, my, mz, gr, rf, freq_shift, position)


def cpmg_hdf5():

    mode = 2
    freq_shift = 120.
    freq_step = 2.
    freq_offset = 0.
    t1 = 1.
    t2 = .100

    freq_shift = frequencyShift(freq_shift, freq_step, offset=freq_offset)
    t2star = calculateT2Star(t2, freq_shift)
    seq = sequence.CPMGSequence()
    p = Parameter.create(name='params', type='group', children=[seq])
    rf = seq.getRF()
    gr = seq.getGradient()

    here = os.path.abspath(os.path.dirname(__file__))
    file_path = os.path.join(here + "/../example/subject/linear_interleved_3x1x1.hdf5")

    # opening file
    file_ = h5py.File(file_path, 'r')
    sample_group = file_.require_group("SampleGroup")

    # reading file
    param_dset = sample_group.require_dataset("param", exact=True, shape=(9,), dtype=float)
    shape_ = tuple(sample_group.require_dataset("shape", exact=True, shape=(4,), dtype=int).value)
    data_dset = sample_group.require_dataset("data", exact=True, shape=shape_, dtype=float)

    # creating positions
    size_ = [param_dset.value[i] for i in [0, 1, 2]]
    dimension = [int(param_dset.value[3 + i]) for i in [0, 1, 2]]
    step_ = [size_[i] / dimension[i] for i in [0, 1, 2]]
    offset_ = [-size_[i] / 2 + step_[i] / 2 for i in [0, 1, 2]]
    position = createPositions(size=size_, step=step_, offset=offset_)

    # calculate magnetization, m0 is mz = 1, mx = my = 0
    mx, my, mz = evolve(rf, gr, DT, t1, t2, freq_shift, position, mode)

    # creating the array with the density of nuclei

    rho = []
    shape = []
    if(len(mx.shape) == 2):
        shape = (mx.shape[0], 1, mx.shape[1])
    else:
        shape = (mx.shape[0], 1, mx.shape[2])

    for i in range(dimension[0]):
        for j in range(dimension[1]):
            for k in range(dimension[2]):
                rho.append(data_dset.value[i, j, k, 2])

    rho_array = np.array([i * np.ones(shape) for i in rho])
    file_.close()

    # add density of nuclei effect
    mx = mx * rho_array
    my = my * rho_array
    mz = mz * rho_array

    plotEverything(mx, my, mz, gr, rf, freq_shift, position)


if __name__ == "__main__":
    # simple_fid()
    # simple_cpmg()
    # cpmg_seven_pulses()
    # spin_echo()
    # gradient_echo_phase_enc_1d_x()
    # gradient_echo_phase_enc()
    gradient_echo_phase_enc_1d_x_new()
    # cpmg_hdf5()
